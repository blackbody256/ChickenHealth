import os
from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.contrib.auth.decorators import login_required
from django.contrib import messages
import tensorflow as tf
from tensorflow.keras.preprocessing import image
from tensorflow.keras.applications.efficientnet import preprocess_input
import numpy as np
from .models import Diagnosis  # Changed from detector.models to .models
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from PIL import Image
import io
import base64
from django.core.paginator import Paginator
from django.db.models import Q, Avg, Count
from datetime import datetime, timedelta

# Define the class names (ensure this order matches your model's training)
class_names = ['Coccidiosis', 'Healthy', 'New Castle Disease', 'Salmonella']

# Recommendations dictionary
recommendations = {
    'Coccidiosis': {
        'treatment': [
            'Administer anticoccidial drugs (e.g., Amprolium, Sulfaquinoxaline) as prescribed by a vet.',
            'Ensure proper hydration and nutrition to support recovery.'
        ],
        'prevention': [
            'Maintain strict hygiene in coops and feeders.',
            'Use coccidiostats in feed for young birds.',
            'Implement a rotation of anticoccidial drugs to prevent resistance.',
            'Ensure proper ventilation and dry litter conditions.'
        ],
        'immediate_action': [
            'Isolate affected birds immediately to prevent spread.',
            'Clean and disinfect the coop thoroughly.',
            'Consult a veterinarian for accurate diagnosis and treatment plan.'
        ]
    },
    'Healthy': {
        'treatment': [
            'No specific treatment needed. Continue good husbandry practices.'
        ],
        'prevention': [
            'Maintain a balanced diet and fresh water supply.',
            'Ensure clean and spacious living conditions.',
            'Regularly monitor flock health and behavior.',
            'Implement a biosecurity plan to prevent disease introduction.'
        ],
        'immediate_action': [
            'Continue routine care and observation.',
            'Record daily feed and water consumption.'
        ]
    },
    'New Castle Disease': {
        'treatment': [
            'There is no specific treatment for Newcastle Disease. Supportive care may be provided.',
            'Focus on preventing secondary bacterial infections.'
        ],
        'prevention': [
            'Vaccination is the most effective preventive measure.',
            'Strict biosecurity protocols are crucial.',
            'Avoid contact with wild birds and other poultry.'
        ],
        'immediate_action': [
            'Immediately report suspected cases to veterinary authorities.',
            'Isolate affected birds and implement strict quarantine measures.',
            'Cull severely affected birds to prevent further spread (under veterinary guidance).'
        ]
    },
    'Salmonella': {
        'treatment': [
            'Antibiotics may be prescribed by a veterinarian, but use with caution due to potential for resistance and impact on gut flora.',
            'Provide supportive care, including electrolytes and vitamins.'
        ],
        'prevention': [
            'Source chicks from NPIP-certified hatcheries.',
            'Maintain strict hygiene in all areas, especially feed and water.',
            'Control rodents and wild birds.',
            'Consider vaccination in high-risk areas.'
        ],
        'immediate_action': [
            'Isolate sick birds.',
            'Thoroughly clean and disinfect contaminated areas.',
            'Test the flock to identify carriers.',
            'Consult a veterinarian for guidance on treatment and control.'
        ]
    }
}

# Global variable for the model
model = None

def load_model():
    """Loads the Keras model into a global variable."""
    global model
    if model is None:
        model_path = os.path.join(settings.BASE_DIR, '..', 'efficientnetb3-Chicken Disease-98.27.h5')
        model = tf.keras.models.load_model(model_path, compile=False)

@login_required
def upload_predict(request):
    """Handle image upload and prediction"""
    load_model()  # Load the model if it's not already loaded

    if request.method == 'POST' and request.FILES.get('image'):
        # Get the uploaded image
        uploaded_image = request.FILES['image']
        fs = FileSystemStorage()
        filename = fs.save(uploaded_image.name, uploaded_image)
        uploaded_image_url = fs.url(filename)

        # Preprocess the image
        img_path = os.path.join(settings.MEDIA_ROOT, filename)
        img = image.load_img(img_path, target_size=(224, 224))
        img_array = image.img_to_array(img)
        img_array = np.expand_dims(img_array, axis=0)
        img_array = preprocess_input(img_array)

        # Make a prediction
        prediction = model.predict(img_array)
        predicted_class = class_names[np.argmax(prediction)]
        confidence = np.max(prediction) * 100

        # Save diagnosis to database
        if request.user.is_authenticated:
            Diagnosis.objects.create(
                user=request.user,
                image=filename,
                disease_name=predicted_class,
                confidence=confidence
            )

        # Redirect to results page with data - FIXED: Added namespace
        return redirect('diagnosis:results_view',
                        predicted_class=predicted_class,
                        confidence=f'{confidence:.2f}%',
                        uploaded_image_url=uploaded_image_url)

    return render(request, 'diagnosis/upload.html')  # Changed from detector to diagnosis

@login_required
def results_view(request, predicted_class, confidence, uploaded_image_url):
    # Get recommendations for the predicted class
    class_recommendations = recommendations.get(predicted_class, {
        'treatment': ['No specific recommendations available.'],
        'prevention': ['No specific recommendations available.'],
        'immediate_action': ['No specific recommendations available.']
    })

    context = {
        'predicted_class': predicted_class,
        'confidence': confidence,
        'uploaded_image_url': uploaded_image_url,
        'recommendations': class_recommendations
    }
    return render(request, 'diagnosis/results.html', context)  # Changed from detector to diagnosis

@login_required
def diagnosis_history(request):
    """Display user's diagnosis history with filtering and pagination"""
    diagnoses = Diagnosis.objects.filter(user=request.user).order_by('-timestamp')
    
    # Apply filters
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    disease_filter = request.GET.get('disease_filter')
    
    if date_from:
        diagnoses = diagnoses.filter(timestamp__date__gte=date_from)
    if date_to:
        diagnoses = diagnoses.filter(timestamp__date__lte=date_to)
    if disease_filter:
        if disease_filter == 'healthy':
            diagnoses = diagnoses.filter(disease_name__icontains='healthy')
        else:
            diagnoses = diagnoses.filter(disease_name__icontains=disease_filter)
    
    # Calculate statistics
    total_diagnoses = diagnoses.count()
    healthy_count = diagnoses.filter(disease_name__icontains='healthy').count()
    disease_count = total_diagnoses - healthy_count
    avg_confidence = diagnoses.aggregate(avg=Avg('confidence'))['avg'] or 0
    
    # Pagination
    paginator = Paginator(diagnoses, 10)  # Show 10 diagnoses per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'diagnoses': page_obj,
        'total_diagnoses': total_diagnoses,
        'healthy_count': healthy_count,
        'disease_count': disease_count,
        'avg_confidence': avg_confidence,
        'is_paginated': page_obj.has_other_pages(),
        'page_obj': page_obj,
    }
    
    return render(request, 'diagnosis/history.html', context)

@login_required
def diagnosis_detail(request, diagnosis_id):
    """Display detailed view of a specific diagnosis"""
    diagnosis = get_object_or_404(Diagnosis, id=diagnosis_id, user=request.user)
    
    # Get similar diagnoses (same disease type, recent)
    similar_diagnoses = Diagnosis.objects.filter(
        user=request.user,
        disease_name=diagnosis.disease_name
    ).exclude(id=diagnosis.id).order_by('-timestamp')[:5]
    
    context = {
        'diagnosis': diagnosis,
        'similar_diagnoses': similar_diagnoses,
    }
    
    return render(request, 'diagnosis/detail.html', context)

@login_required
def reanalyze_diagnosis(request, diagnosis_id):
    """Re-analyze an existing diagnosis image"""
    diagnosis = get_object_or_404(Diagnosis, id=diagnosis_id, user=request.user)
    
    if request.method == 'POST':
        # Load the model and re-analyze the image
        load_model()
        
        # Get the image path
        img_path = diagnosis.image.path
        
        try:
            # Preprocess the image
            img = image.load_img(img_path, target_size=(224, 224))
            img_array = image.img_to_array(img)
            img_array = np.expand_dims(img_array, axis=0)
            img_array = preprocess_input(img_array)

            # Make a prediction
            prediction = model.predict(img_array)
            predicted_class = class_names[np.argmax(prediction)]
            confidence = np.max(prediction) * 100

            # Create a new diagnosis entry
            new_diagnosis = Diagnosis.objects.create(
                user=request.user,
                image=diagnosis.image.name,  # Reuse the same image
                disease_name=predicted_class,
                confidence=confidence
            )

            messages.success(request, 'Image re-analyzed successfully!')
            return redirect('diagnosis:detail', diagnosis_id=new_diagnosis.id)
            
        except Exception as e:
            messages.error(request, f'Error re-analyzing image: {str(e)}')
            return redirect('diagnosis:detail', diagnosis_id=diagnosis.id)
    
    return redirect('diagnosis:detail', diagnosis_id=diagnosis.id)

def index(request):
    """Home page"""
    return render(request, 'diagnosis/index.html')