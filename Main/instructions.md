
# Instructions to Create and Run the Chicken Disease Detection Django App

This guide provides all the necessary steps to set up a Django application that uses your trained model to predict chicken diseases from an uploaded image.

## 1. Environment Setup

First, you need to create a conda environment and install the required packages.

**1.1. Create and Activate the Conda Environment**

Open your terminal and run the following commands:

```bash
# Create a new conda environment named 'ayute' with Python 3.7.12
conda create -n ayute python=3.7.12 -y

# Activate the environment
conda activate ayute
```

**1.2. Install Required Packages**

With the `ayute` environment activated, install the necessary Python libraries with their specific versions:

```bash
# Install Django, TensorFlow, and Pillow
pip install Django==3.2.25 tensorflow==2.9.1 Pillow==9.5.0
```

## 2. Project Setup

Next, create the Django project and the app that will handle the image uploads and predictions.

**2.1. Create the Django Project**

Navigate to the directory where you want to create your project (e.g., `/home/andrew/Downloads/new`) and run the following command:

```bash
# Create a new Django project named 'disease_detection'
django-admin startproject disease_detection
```

This will create a `disease_detection` directory. Move into this directory:

```bash
cd disease_detection
```

**2.2. Create the Detector App**

Now, create a Django app named `detector` within your project:

```bash
# Create the 'detector' app
python manage.py startapp detector
```

## 3. Code Implementation

Now it's time to write the code for the application.

**3.1. Configure Project Settings**

Open the `disease_detection/settings.py` file and add the `detector` app to the `INSTALLED_APPS` list:

```python
# disease_detection/settings.py

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'detector',  # Add this line
]
```

**3.2. Create the Views**

Open the `detector/views.py` file and add the following code. This code will handle the image upload, model loading, and prediction.

```python
# detector/views.py

import os
from django.shortcuts import render
from django.conf import settings
from django.core.files.storage import FileSystemStorage
import tensorflow as tf
from tensorflow.keras.preprocessing import image
import numpy as np

# Define the class names
class_names = ['Coccidiosis', 'Healthy', 'Newcastle disease', 'Salmonella']

# Global variable for the model
model = None

def load_model():
    """Loads the Keras model into a global variable."""
    global model
    if model is None:
        model_path = os.path.join(settings.BASE_DIR, '..', 'efficientnetb3-Chicken Disease-98.27.h5')
        model = tf.keras.models.load_model(model_path, compile=False)

def upload_predict(request):
    load_model()  # Load the model if it's not already loaded

    if request.method == 'POST' and request.FILES['image']:
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
        img_array /= 255.

        # Make a prediction
        prediction = model.predict(img_array)
        predicted_class = class_names[np.argmax(prediction)]
        confidence = np.max(prediction) * 100

        return render(request, 'detector/upload.html', {
            'uploaded_image_url': uploaded_image_url,
            'predicted_class': predicted_class,
            'confidence': f'{confidence:.2f}%'
        })

    return render(request, 'detector/upload.html')
```

**3.3. Create the URL Patterns**

Create a new file named `detector/urls.py` and add the following code:

```python
# detector/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('', views.upload_predict, name='upload_predict'),
]
```

Now, include these URLs in your main project's `urls.py` file. Open `disease_detection/urls.py` and modify it as follows:

```python
# disease_detection/urls.py

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('detector.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

**3.4. Create the HTML Template**

Create a `templates` directory inside the `detector` app directory. Inside the `templates` directory, create another directory named `detector`. Finally, create an `upload.html` file inside `detector/templates/detector/`.

```
disease_detection/
├── detector/
│   ├── templates/
│   │   └── detector/
│   │       └── upload.html
```

Add the following HTML code to the `detector/templates/detector/upload.html` file:

```html
<!-- detector/templates/detector/upload.html -->

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Chicken Disease Detection</title>
    <style>
        body { font-family: sans-serif; margin: 2em; }
        .container { max-width: 500px; margin: auto; }
        .result { margin-top: 2em; }
        img { max-width: 100%; height: auto; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Chicken Disease Detection</h1>
        <form method="post" enctype="multipart/form-data">
            {% csrf_token %}
            <input type="file" name="image" accept="image/*" required>
            <button type="submit">Upload and Predict</button>
        </form>

        {% if uploaded_image_url %}
            <div class="result">
                <h2>Prediction Result</h2>
                <img src="{{ uploaded_image_url }}" alt="Uploaded Image">
                <p><strong>Predicted Disease:</strong> {{ predicted_class }}</p>
                <p><strong>Confidence:</strong> {{ confidence }}</p>
            </div>
        {% endif %}
    </div>
</body>
</html>
```

**3.5. Configure Media Files**

Finally, you need to configure the `MEDIA_URL` and `MEDIA_ROOT` in your `disease_detection/settings.py` file. This is where uploaded files will be stored. Add the following lines to the end of your `settings.py` file:

```python
# disease_detection/settings.py

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
```

## 4. Running the Application

Now you are ready to run the Django development server.

**4.1. Run the Migrations**

First, run the database migrations:

```bash
python manage.py migrate
```

**4.2. Start the Server**

Start the Django development server:

```bash
python manage.py runserver
```

You should see output indicating that the server is running. You can now access the application in your web browser at `http://127.0.0.1:8000/`.

You can now upload an image of a chicken, and the application will predict whether it has Coccidiosis, Salmonella, Newcastle disease, or is Healthy.
