import tensorflow as tf
import numpy as np
from PIL import Image
import os
from django.conf import settings
import cv2

class ChickenDiseaseDetector:
    def __init__(self):
        self.model = None
        self.class_names = ['Healthy', 'Coccidiosis', 'Salmonella', 'Newcastle Disease']  # Adjust based on your model
        self.load_model()
    
    def load_model(self):
        """Load the trained model"""
        model_path = os.path.join(settings.BASE_DIR, 'ml_models', 'chicken_disease_model.h5')
        try:
            self.model = tf.keras.models.load_model(model_path)
            print("Model loaded successfully")
        except Exception as e:
            print(f"Error loading model: {e}")
    
    def preprocess_image(self, image_path):
        """Preprocess image for prediction"""
        try:
            # Load and resize image
            image = cv2.imread(image_path)
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            image = cv2.resize(image, (224, 224))  # Adjust size based on your model
            
            # Normalize pixel values
            image = image.astype('float32') / 255.0
            image = np.expand_dims(image, axis=0)
            
            return image
        except Exception as e:
            print(f"Error preprocessing image: {e}")
            return None
    
    def predict(self, image_path):
        """Make prediction on image"""
        if self.model is None:
            return None, 0.0
        
        processed_image = self.preprocess_image(image_path)
        if processed_image is None:
            return None, 0.0
        
        try:
            prediction = self.model.predict(processed_image)
            predicted_class_index = np.argmax(prediction[0])
            confidence = float(prediction[0][predicted_class_index])
            predicted_class = self.class_names[predicted_class_index]
            
            return predicted_class, confidence
        except Exception as e:
            print(f"Error making prediction: {e}")
            return None, 0.0
    
    def get_recommendations(self, disease):
        """Get treatment recommendations based on diagnosis"""
        recommendations = {
            'Healthy': {
                'status': 'Good',
                'recommendations': [
                    'Continue current feeding practices',
                    'Maintain clean water supply',
                    'Regular health monitoring',
                    'Ensure proper ventilation in coop'
                ]
            },
            'Coccidiosis': {
                'status': 'Disease Detected',
                'recommendations': [
                    'Isolate affected birds immediately',
                    'Consult veterinarian for anticoccidial medication',
                    'Improve sanitation and reduce moisture',
                    'Provide electrolyte solution',
                    'Clean and disinfect living areas'
                ]
            },
            'Salmonella': {
                'status': 'Disease Detected',
                'recommendations': [
                    'Quarantine affected birds',
                    'Contact veterinarian immediately',
                    'Implement strict biosecurity measures',
                    'Disinfect all equipment and facilities',
                    'Monitor other birds closely'
                ]
            },
            'Newcastle Disease': {
                'status': 'Disease Detected',
                'recommendations': [
                    'Report to veterinary authorities immediately',
                    'Quarantine all birds',
                    'No specific treatment available',
                    'Focus on prevention through vaccination',
                    'Implement strict biosecurity protocols'
                ]
            }
        }
        
        return recommendations.get(disease, {
            'status': 'Unknown',
            'recommendations': ['Consult with a veterinarian for proper diagnosis']
        })