from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from .forms import ImageUploadForm
from .models import ChickenAnalysis
from .ml_utils import detector_instance # Import the singleton instance
import os
# Create your views here.
def upload_image(request):
    if request.method == 'POST':
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            analysis = form.save()
            
            # Check if the model loaded correctly at startup
            if detector_instance is None:
                messages.error(request, "The disease analysis model could not be loaded. Please contact the site administrator.")
                return render(request, 'upload.html', {'form': form})

            #Perform disease detection
            image_path = analysis.image.path
            predicted_disease, confidence = detector_instance.predict(image_path)
            
            if predicted_disease:
                analysis.predicted_disease = predicted_disease
                analysis.confidence_score = confidence
                analysis.save()
                # Redirect to the result page after successful analysis
                return redirect('result', analysis_id=analysis.id)
            else:
                messages.error(request, 'Error analyzing image. Please try again.')
        else:
            messages.error(request, 'Please upload a valid image file.')
    else: 
        form = ImageUploadForm()
    
    return render(request, 'upload.html', {'form': form})

def result(request, analysis_id):
    try:
        analysis = ChickenAnalysis.objects.get(id=analysis_id)
        
        # Check if the model loaded correctly at startup
        if detector_instance is None:
            # This case is less likely to be hit if the upload worked, but is good for safety
            return render(request, 'result.html', {'analysis': analysis, 'recommendations': {'status': 'Error', 'recommendations': ['Analysis model is offline.']}})
        recommendations = detector_instance.get_recommendations(analysis.predicted_disease)
        
        context = {
            'analysis': analysis,
            'recommendations' : recommendations
        }
        return render(request, 'result.html', context)
    except ChickenAnalysis.DoesNotExist:
        messages.error(request, 'Analysis not found')
        return redirect('upload')

def history(request):
    analyses = ChickenAnalysis.objects.all()[:10] # show last 10 analyses
    return render(request, 'history.html', {'analyses' : analyses})