from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.core.exceptions import ValidationError
from .forms import ImageUploadForm
from .models import ChickenAnalysis
from .ml_utils import detector_instance, get_detector_status
import os
import logging

# Set up logging
logger = logging.getLogger(__name__)

def upload_image(request):
    """Handle image upload and analysis"""
    
    # Check detector status
    detector_status = get_detector_status()
    if not detector_status['loaded']:
        messages.error(
            request, 
            "The disease analysis model is currently unavailable. "
            "Please contact the administrator or try again later."
        )
        logger.error(f"Detector not available: {detector_status['error']}")
    
    if request.method == 'POST':
        form = ImageUploadForm(request.POST, request.FILES)
        
        if form.is_valid():
            try:
                # Save the analysis record
                analysis = form.save()
                logger.info(f"Image uploaded successfully: {analysis.id}")
                
                # Check if detector is available
                if detector_instance is None:
                    messages.error(
                        request, 
                        "The disease analysis model could not be loaded. "
                        "The image has been saved but cannot be analyzed at this time."
                    )
                    return render(request, 'upload.html', {'form': form})

                # Get the image path
                image_path = analysis.image.path
                
                # Verify the image file exists
                if not os.path.exists(image_path):
                    logger.error(f"Image file not found: {image_path}")
                    messages.error(request, 'Image file could not be found after upload.')
                    analysis.delete()  # Clean up the database record
                    return render(request, 'upload.html', {'form': form})

                # Perform disease detection
                try:
                    predicted_disease, confidence = detector_instance.predict(image_path)
                    
                    if predicted_disease is not None:
                        analysis.predicted_disease = predicted_disease
                        analysis.confidence_score = confidence
                        analysis.save()
                        
                        logger.info(
                            f"Analysis completed for {analysis.id}: "
                            f"{predicted_disease} ({confidence:.2f}%)"
                        )
                        
                        # Redirect to results page
                        return redirect('result', analysis_id=analysis.id)
                    else:
                        logger.error(f"Prediction failed for analysis {analysis.id}")
                        messages.error(
                            request, 
                            'Error analyzing image. The image may be corrupted or in an unsupported format.'
                        )
                        
                except Exception as e:
                    logger.error(f"Error during prediction: {str(e)}")
                    messages.error(
                        request, 
                        'An error occurred during image analysis. Please try again.'
                    )
                    
            except ValidationError as e:
                logger.error(f"Validation error: {str(e)}")
                messages.error(request, f'Validation error: {str(e)}')
                
            except Exception as e:
                logger.error(f"Unexpected error during upload: {str(e)}")
                messages.error(
                    request, 
                    'An unexpected error occurred. Please try again.'
                )
        else:
            # Form validation failed
            logger.warning("Form validation failed")
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = ImageUploadForm()
    
    context = {
        'form': form,
        'detector_status': detector_status
    }
    return render(request, 'upload.html', context)

def result(request, analysis_id):
    """Display analysis results"""
    try:
        analysis = get_object_or_404(ChickenAnalysis, id=analysis_id)
        logger.info(f"Displaying results for analysis {analysis_id}")
        
        # Check if detector is available for recommendations
        if detector_instance is None:
            recommendations = {
                'status': 'Error',
                'recommendations': [
                    'Analysis model is currently offline.',
                    'Please consult with a veterinarian for proper diagnosis.'
                ]
            }
            logger.warning("Detector unavailable for recommendations")
        else:
            # Get recommendations based on the predicted disease
            if analysis.predicted_disease:
                recommendations = detector_instance.get_recommendations(analysis.predicted_disease)
            else:
                recommendations = {
                    'status': 'Incomplete',
                    'recommendations': [
                        'Analysis was not completed successfully.',
                        'Please try uploading the image again.',
                        'Consult with a veterinarian if problems persist.'
                    ]
                }
        
        context = {
            'analysis': analysis,
            'recommendations': recommendations
        }
        return render(request, 'result.html', context)
        
    except ChickenAnalysis.DoesNotExist:
        logger.error(f"Analysis {analysis_id} not found")
        messages.error(request, 'Analysis not found. Please try uploading a new image.')
        return redirect('upload')
    except Exception as e:
        logger.error(f"Error displaying results for {analysis_id}: {str(e)}")
        messages.error(request, 'An error occurred while displaying results.')
        return redirect('upload')

def result_detail(request, analysis_id):
    """Display detailed results for a specific analysis"""
    analysis = get_object_or_404(ChickenAnalysis, id=analysis_id)
    
    # Calculate additional metrics if needed
    context = {
        'analysis': analysis,
        'confidence_level': 'High' if analysis.confidence_score >= 80 else 'Medium' if analysis.confidence_score >= 60 else 'Low',
        'risk_level': 'Low' if analysis.predicted_disease == 'Healthy' else 'High',
    }
    
    return render(request, 'result_detail.html', context)

def history(request):
    """Display analysis history"""
    try:
        analyses = ChickenAnalysis.objects.all().order_by('-analysis_date')[:20]
        logger.info(f"Displaying {len(analyses)} analyses in history")
        
        context = {
            'analyses': analyses,
            'detector_status': get_detector_status()
        }
        return render(request, 'history.html', context)
        
    except Exception as e:
        logger.error(f"Error displaying history: {str(e)}")
        messages.error(request, 'An error occurred while loading analysis history.')
        return render(request, 'history.html', {'analyses': []})

def api_status(request):
    """API endpoint to check detector status"""
    status = get_detector_status()
    return JsonResponse(status)

def delete_analysis(request, analysis_id):
    """Delete a specific analysis"""
    analysis = get_object_or_404(ChickenAnalysis, id=analysis_id)
    
    if request.method == 'POST':
        # Delete the image file if it exists
        if analysis.image and os.path.exists(analysis.image.path):
            os.remove(analysis.image.path)
            logger.info(f"Deleted image file: {analysis.image.path}")
        
        # Delete the database record
        analysis.delete()
        logger.info(f"Deleted analysis {analysis_id}")
        
        messages.success(request, 'Analysis deleted successfully.')
        
    return redirect('history')