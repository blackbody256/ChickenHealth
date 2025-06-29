from django import forms
from PIL import Image
from .models import ChickenAnalysis

class ImageUploadForm(forms.Form):
    image = forms.ImageField(
        widget=forms.ClearableFileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*'
        })
    )
    
    def clean_image(self):
        image = self.cleaned_data.get('image')
        
        if not image:
            raise forms.ValidationError("No image file provided.")
        
        # Check file size (limit to 10MB)
        if image.size > 5 * 1024 * 1024:
            raise forms.ValidationError("Image file too large. Please upload an image smaller than 10MB.")
        
        # Check file extension
        if not image.name.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
            raise forms.ValidationError("Unsupported file type. Please upload a valid image.")
        
        # Check MIME type
        if not image.content_type.startswith('image/'):
            raise forms.ValidationError("File is not an image. Please upload a valid image file.")
        
        # Validate that it's actually an image using PIL
        try:
            pil_image = Image.open(image)
            pil_image.verify()
        except Exception:
            raise forms.ValidationError("Invalid image file. Please upload a valid image.")
        
        return image