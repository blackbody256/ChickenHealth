from django import forms
from PIL import Image
from .models import ChickenAnalysis

class ImageUploadForm(forms.ModelForm):
    class Meta:
        model = ChickenAnalysis
        fields = ['image']
        widgets = {
            'image': forms.ClearableFileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*'
        })
        }

    def clean_image(self):
        image = self.cleaned_data.get('image')

        if not image:
            raise forms.ValidationError("No image file provided.")

        # Check file size (limit to 5MB)
        if image.size > 5 * 1024 * 1024:
            raise forms.ValidationError("Image file too large. Please upload an image smaller than 5MB.")

        # Validate that it's actually an image using PIL
        try:
            image.seek(0) # Rewind file for Pillow to read
            pil_image = Image.open(image)
            pil_image.verify()
            image.seek(0) # Rewind file for Django to save
        except Exception:
            raise forms.ValidationError("Invalid image file. Please upload a valid image.")

        return image