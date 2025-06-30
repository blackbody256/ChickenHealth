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
                'accept': 'image/*',
                'id': 'imageInput'  # Add ID for JavaScript
            })
        }

    def clean_image(self):
        image = self.cleaned_data.get('image')

        if not image:
            raise forms.ValidationError("No image file provided.")

        # Check file size (limit to 5MB)
        if image.size > 5 * 1024 * 1024:
            raise forms.ValidationError("Image file too large. Please upload an image smaller than 5MB.")

        # Validate file extension
        allowed_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']
        file_extension = image.name.lower().split('.')[-1]
        if f'.{file_extension}' not in allowed_extensions:
            raise forms.ValidationError("Please upload a valid image file (JPG, PNG, BMP, TIFF).")

        # Validate that it's actually an image using PIL
        try:
            image.seek(0)
            pil_image = Image.open(image)
            pil_image.verify()
            image.seek(0)
            
            # Check minimum dimensions
            with Image.open(image) as img:
                if img.size[0] < 50 or img.size[1] < 50:
                    raise forms.ValidationError("Image is too small. Minimum size is 50x50 pixels.")
            
            image.seek(0)
        except Exception as e:
            raise forms.ValidationError("Invalid image file. Please upload a valid image.")

        return image