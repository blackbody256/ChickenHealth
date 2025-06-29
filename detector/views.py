from django.shortcuts import render
from django.contrib import messages
from django.http import JsonResponse
from .forms import ImageUploadForm
from .models import ChickenAnalysis
from .ml_utils import ChickenDiseaseDetector
import os
# Create your views here.
def upload_image(request):
    if request.method == 'POST':
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            analysis = form.save(commit=False)
            analysis.save()
            
            #Perform disease detection
            detector = ChickenDiseaseDetector()
            image_path = analysis.image.path
            
            predicted_disease, confidence = detector.predict(image_path)
            
            if predicted_disease:
                analysis.predicted_disease = predicted_disease
                analysis.confidence_score = confidence
                analysis.save()
                
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
        detector = ChickenDiseaseDetector()
        recommendations = detector.get_recommendations(analysis.predicted_disease)
        
        context = {
            'analysis': analysis,
            'recommendations' : recommendations
        }
        return render(request, 'result.html', context)
    except ChickenAnalysis.DoesnotExist:
        messages.error(request, 'Analysis not found')
        return redirect('upload')

def history(request):
    analyses = ChickenAnalysis.objects.all()[:10] # show last 10 analyses
    return render(request, 'history.html', {'analyses' : analyses})