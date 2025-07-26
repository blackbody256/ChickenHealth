from django import forms
from .models import VetUpload

class VetUploadForm(forms.ModelForm):
    class Meta:
        model = VetUpload
        fields = ['title', 'file']
