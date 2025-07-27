from django.contrib.auth.forms import UserCreationForm
from django import forms
from .models import User

class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)
    
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'role', 'password1', 'password2')  # Added password fields
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['role'].choices = User.ROLE_CHOICES
        
        # Add CSS classes and placeholders
        self.fields['username'].widget.attrs.update({
            'class': 'form-input',
            'placeholder': 'Enter username'
        })
        self.fields['first_name'].widget.attrs.update({
            'class': 'form-input',
            'placeholder': 'Enter first name'
        })
        self.fields['last_name'].widget.attrs.update({
            'class': 'form-input',
            'placeholder': 'Enter last name'
        })
        self.fields['email'].widget.attrs.update({
            'class': 'form-input',
            'placeholder': 'Enter email address'
        })
        self.fields['password1'].widget.attrs.update({
            'class': 'form-input',
            'placeholder': 'Enter password'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-input',
            'placeholder': 'Confirm password'
        })
        self.fields['role'].widget.attrs.update({
            'class': 'form-input'
        })

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user

# Add this to edit the profiles
class ProfileEditForm(forms.ModelForm):
    email = forms.EmailField(required=True)
    
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'username')
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Enter your first name'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-input', 
                'placeholder': 'Enter your last name'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-input',
                'placeholder': 'Enter your email address'
            }),
            'username': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Enter your username'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make username field read-only for existing users
        if self.instance and self.instance.pk:
            self.fields['username'].widget.attrs['readonly'] = True
            self.fields['username'].help_text = "Username cannot be changed"
    
    def clean_email(self):
        email = self.cleaned_data['email']
        # Check if email is already taken by another user
        if User.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("This email address is already in use.")
        return email
    

# managing users 
class FarmerCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password')
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'FARMER'
        if commit:
            user.save()
        return user
    
class FarmerForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'is_active']