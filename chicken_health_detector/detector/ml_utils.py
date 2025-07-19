import tensorflow as tf
import numpy as np
from PIL import Image
import os
from django.conf import settings
import cv2
import logging

# Set up logging
logger = logging.getLogger(__name__)

class ChickenDiseaseDetector:
    def __init__(self):
        self.model = None
        self.class_names = ['Healthy', 'Coccidiosis', 'Salmonella', 'Newcastle Disease']
        self.input_shape = (224, 224)  # Default input shape
        self.load_model()

    def load_model(self):
        """Load the trained model with better error handling"""
        model_path = os.path.join(settings.BASE_DIR, 'ml_models', 'chicken_disease_model.h5')
        
        # Create ml_models directory if it doesn't exist
        ml_models_dir = os.path.join(settings.BASE_DIR, 'ml_models')
        if not os.path.exists(ml_models_dir):
            os.makedirs(ml_models_dir)
            logger.warning(f"Created ml_models directory at {ml_models_dir}")

        if not os.path.exists(model_path):
            logger.error(f"Model file not found at {model_path}")
            logger.info("Please ensure the model file 'chicken_disease_model.h5' exists in the 'ml_models' directory")
            raise FileNotFoundError(f"Model file not found at {model_path}")

        try:
            # Suppress TensorFlow warnings for cleaner output
            tf.get_logger().setLevel('ERROR')
            
            # Load model with custom objects if needed
            self.model = tf.keras.models.load_model(
                model_path,
                compile=False  # Skip compilation to avoid potential issues
            )
            
            # Recompile the model with basic settings
            self.model.compile(
                optimizer='adam',
                loss='categorical_crossentropy',
                metrics=['accuracy']
            )
            
            # Get input shape from model
            if self.model.input_shape:
                self.input_shape = self.model.input_shape[1:3]  # Remove batch dimension
            
            logger.info(f"Model loaded successfully from {model_path}")
            logger.info(f"Model input shape: {self.input_shape}")
            logger.info(f"Model output classes: {len(self.class_names)}")
            
        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
            raise IOError(f"Error loading model: {str(e)}") from e

    def preprocess_image(self, image_path):
        """Preprocess image for prediction with better error handling"""
        try:
            # Check if file exists
            if not os.path.exists(image_path):
                logger.error(f"Image file not found: {image_path}")
                return None

            # Try different methods to load the image
            try:
                # Method 1: Use OpenCV
                image = cv2.imread(image_path)
                if image is None:
                    raise ValueError("OpenCV failed to load image")
                image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            except Exception as cv_error:
                logger.warning(f"OpenCV failed, trying PIL: {cv_error}")
                try:
                    # Method 2: Use PIL
                    pil_image = Image.open(image_path)
                    image = np.array(pil_image.convert('RGB'))
                except Exception as pil_error:
                    logger.error(f"Both OpenCV and PIL failed: {pil_error}")
                    return None

            # Resize image to model input size
            image = cv2.resize(image, self.input_shape)
            
            # Normalize pixel values to [0, 1]
            image = image.astype('float32') / 255.0
            
            # Add batch dimension
            image = np.expand_dims(image, axis=0)
            
            logger.debug(f"Image preprocessed successfully. Shape: {image.shape}")
            return image
            
        except Exception as e:
            logger.error(f"Error preprocessing image {image_path}: {str(e)}")
            return None

    def predict(self, image_path):
        """Make prediction on image with improved error handling"""
        if self.model is None:
            logger.error("Model is not loaded")
            return None, 0.0

        processed_image = self.preprocess_image(image_path)
        if processed_image is None:
            logger.error("Failed to preprocess image")
            return None, 0.0

        try:
            # Make prediction
            predictions = self.model.predict(processed_image, verbose=0)
            
            # Handle different prediction formats
            if len(predictions.shape) == 2:
                prediction = predictions[0]
            else:
                prediction = predictions
            
            # Get predicted class and confidence
            predicted_class_index = np.argmax(prediction)
            confidence = float(prediction[predicted_class_index]) * 100  # Convert to percentage
            
            # Ensure index is within bounds
            if predicted_class_index >= len(self.class_names):
                logger.error(f"Predicted class index {predicted_class_index} out of bounds")
                return None, 0.0
            
            predicted_class = self.class_names[predicted_class_index]
            
            logger.info(f"Prediction: {predicted_class} with confidence {confidence:.2f}%")
            return predicted_class, confidence
            
        except Exception as e:
            logger.error(f"Error making prediction: {str(e)}")
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
                    'Ensure proper ventilation in coop',
                    'Keep the living area clean and dry'
                ]
            },
            'Coccidiosis': {
                'status': 'Disease Detected',
                'recommendations': [
                    'Isolate affected birds immediately',
                    'Consult veterinarian for anticoccidial medication',
                    'Improve sanitation and reduce moisture',
                    'Provide electrolyte solution to prevent dehydration',
                    'Clean and disinfect living areas thoroughly',
                    'Monitor other birds for symptoms'
                ]
            },
            'Salmonella': {
                'status': 'Disease Detected',
                'recommendations': [
                    'Quarantine affected birds immediately',
                    'Contact veterinarian for antibiotic treatment',
                    'Implement strict biosecurity measures',
                    'Disinfect all equipment and facilities',
                    'Monitor other birds closely for symptoms',
                    'Review feed and water sources for contamination'
                ]
            },
            'Newcastle Disease': {
                'status': 'Disease Detected',
                'recommendations': [
                    'Report to veterinary authorities immediately',
                    'Quarantine all birds in the flock',
                    'No specific treatment available',
                    'Focus on prevention through vaccination',
                    'Implement strict biosecurity protocols',
                    'Dispose of deceased birds properly'
                ]
            }
        }
        
        return recommendations.get(disease, {
            'status': 'Unknown',
            'recommendations': [
                'Consult with a qualified veterinarian for proper diagnosis',
                'Monitor the bird closely for other symptoms',
                'Ensure proper nutrition and hydration'
            ]
        })

    def validate_model(self):
        """Validate that the model is working correctly"""
        if self.model is None:
            return False, "Model not loaded"
        
        try:
            # Create a dummy input to test the model
            dummy_input = np.random.random((1, *self.input_shape, 3)).astype('float32')
            test_prediction = self.model.predict(dummy_input, verbose=0)
            
            if test_prediction.shape[-1] != len(self.class_names):
                return False, f"Model output shape {test_prediction.shape} doesn't match class names {len(self.class_names)}"
            
            return True, "Model validation successful"
        except Exception as e:
            return False, f"Model validation failed: {str(e)}"

# Global detector instance
detector_instance = None

def initialize_detector():
    """Initialize the detector instance with comprehensive error handling"""
    global detector_instance
    
    logger.info("Initializing Chicken Disease Detector...")
    
    try:
        detector_instance = ChickenDiseaseDetector()
        
        # Validate the model
        is_valid, validation_message = detector_instance.validate_model()
        if not is_valid:
            logger.error(f"Model validation failed: {validation_message}")
            detector_instance = None
            return False
        
        logger.info("Chicken Disease Detector initialized successfully")
        logger.info(f"Model loaded with {len(detector_instance.class_names)} classes")
        return True
        
    except FileNotFoundError as e:
        logger.error(f"Model file not found: {str(e)}")
        logger.error("Please ensure the model file is in the correct location")
        detector_instance = None
        return False
        
    except Exception as e:
        logger.error(f"Failed to initialize detector: {str(e)}")
        detector_instance = None
        return False

def get_detector_status():
    """Get the current status of the detector"""
    if detector_instance is None:
        return {
            'loaded': False,
            'error': 'Detector not initialized',
            'classes': []
        }
    
    return {
        'loaded': True,
        'error': None,
        'classes': detector_instance.class_names,
        'input_shape': detector_instance.input_shape
    }