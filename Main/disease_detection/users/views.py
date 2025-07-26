from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView, UpdateView
from .forms import SignUpForm, ProfileEditForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib.auth.views import LoginView
from django.http import HttpResponseRedirect
from django.core.exceptions import PermissionDenied, ValidationError
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth import logout
from django.db.models import Count, Q
from django.utils import timezone
from datetime import datetime, timedelta

#for user management
from django.contrib.auth import get_user_model
User = get_user_model()
from .forms import FarmerCreationForm
from django import forms
from .forms import FarmerForm
from django.shortcuts import get_object_or_404
from functools import wraps
from diagnosis.models import Diagnosis

#decorator to check if user is admin
def admin_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated and (request.user.role == 'ADMIN' or request.user.is_superuser or request.user.is_staff):
            return view_func(request, *args, **kwargs)
        raise PermissionDenied
    return _wrapped_view

class CustomLoginView(LoginView):
    template_name = 'login.html'

    def get_success_url(self):
        user = self.request.user
        
        # Check if user is admin and redirect to analytics dashboard
        if (hasattr(user, 'role') and user.role == 'ADMIN') or user.is_superuser or user.is_staff:
            return '/admin-dashboard/'
        elif user.role == 'VET':
            return '/vet-dashboard/'
        else:
            return '/dashboard/'  # Default: FARMER
        

class SignUpView(CreateView):
    form_class = SignUpForm
    template_name = 'signup.html'
    
    def form_valid(self, form):
        try:
            user = form.save()
            login(self.request, user)
            
            # Redirect based on user role
            if (hasattr(user, 'role') and user.role == 'ADMIN') or user.is_superuser or user.is_staff:
                return HttpResponseRedirect('/admin-dashboard/')
            elif user.role == 'VET':
               return HttpResponseRedirect('/vet-dashboard/')
            else:
               return HttpResponseRedirect('/dashboard/')
        except ValidationError as e:
            # Add the validation error to the form
            form.add_error('role', e.message if hasattr(e, 'message') else str(e))
            return self.form_invalid(form)

# Profile edit page
class ProfileEditView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = ProfileEditForm
    template_name = 'profile_edit.html'
    
    def get_object(self):
        # Return the current user's profile
        return self.request.user
    
    def get_success_url(self):
        # Keep user on the same profile edit page
        return self.request.path  # This returns the current URL path
    
    def form_valid(self, form):
        messages.success(self.request, 'Your profile has been updated successfully!')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        messages.error(self.request, 'Please correct the errors below.')
        return super().form_invalid(form)

def home(request):
    return render(request, 'home.html')

@login_required
def dashboard(request):
    user = request.user
    context = {}

    if user.role == 'FARMER':
        user_diagnoses = Diagnosis.objects.filter(user=user)
        total_diagnoses = user_diagnoses.count()
        diseased_droppings = user_diagnoses.exclude(
            Q(disease_name__icontains='healthy') |
            Q(disease_name__icontains='no disease')
        ).count()
        healthy_droppings = total_diagnoses - diseased_droppings
        recent_activities = user_diagnoses.order_by('-timestamp')[:5]

        context = {
            'user_type': 'farmer',
            'user': user,
            'total_diagnoses': total_diagnoses,
            'diseased_droppings': diseased_droppings,
            'healthy_droppings': healthy_droppings,
            'recent_activities': recent_activities,
            'total_farms': 1, # Placeholder for now
            'total_uploads': total_diagnoses, # Same as diagnoses for farmer
            'pending_tasks': diseased_droppings, # Diseased droppings can be considered pending tasks
        }
    elif user.role == 'ADMIN':
        total_users = User.objects.count()
        total_farmers = User.objects.filter(role='FARMER').count()
        total_vets = User.objects.filter(role='VET').count()
        total_diagnoses = Diagnosis.objects.count()

        context = {
            'user_type': 'admin',
            'user': user,
            'total_users': total_users,
            'total_farmers': total_farmers,
            'total_vets': total_vets,
            'total_diagnoses': total_diagnoses,
        }
    elif user.role == 'VET':
        total_farmers = User.objects.filter(role='FARMER').count()
        total_diagnoses = Diagnosis.objects.count()
        diseased_droppings = Diagnosis.objects.exclude(
            Q(disease_name__icontains='healthy') |
            Q(disease_name__icontains='no disease')
        ).count()
        healthy_droppings = total_diagnoses - diseased_droppings

        context = {
            'user_type': 'vet',
            'user': user,
            'total_farmers': total_farmers,
            'total_diagnoses': total_diagnoses,
            'diseased_droppings': diseased_droppings,
            'healthy_droppings': healthy_droppings,
        }
    else:
        context = {
            'user_type': 'basic',
            'user': user,
            'total_farms': 0,
            'total_diagnoses': 0,
            'total_uploads': 0,
            'pending_tasks': 0,
        }

    return render(request, 'dashboard.html', context)

@login_required
def admin_dashboard(request):
    total_users = User.objects.count()
    total_farmers = User.objects.filter(role='FARMER').count()
    total_vets = User.objects.filter(role='VET').count()
    total_diagnoses = Diagnosis.objects.count()

    context = {
        'total_users': total_users,
        'total_farmers': total_farmers,
        'total_vets': total_vets,
        'total_diagnoses': total_diagnoses,
    }
    return render(request, 'admin_dashboard.html', context)

@login_required
def vet_dashboard(request):
    total_farmers = User.objects.filter(role='FARMER').count()
    total_diagnoses = Diagnosis.objects.count()
    diseased_droppings = Diagnosis.objects.exclude(
        Q(disease_name__icontains='healthy') |
        Q(disease_name__icontains='no disease')
    ).count()
    healthy_droppings = total_diagnoses - diseased_droppings

    context = {
        'total_farmers': total_farmers,
        'total_diagnoses': total_diagnoses,
        'diseased_droppings': diseased_droppings,
        'healthy_droppings': healthy_droppings,
    }
    return render(request, 'vet_dashboard.html', context)

def about(request):
    return render(request, 'about.html')

# Password reset views
from django.contrib.auth.views import (
    PasswordResetView, 
    PasswordResetDoneView, 
    PasswordResetConfirmView, 
    PasswordResetCompleteView
)

class CustomPasswordResetView(PasswordResetView):
    template_name = 'password_reset.html'
    email_template_name = 'password_reset_email.html'
    success_url = reverse_lazy('password_reset_done')

class CustomPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'password_reset_done.html'

class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'password_reset_confirm.html'
    success_url = reverse_lazy('password_reset_complete')

class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'password_reset_complete.html'

# User management views
@login_required
@admin_required
def manage_farmers(request):
    farmers = User.objects.exclude(role='ADMIN')
    return render(request, "manage_farmers.html", {"farmers": farmers})

@login_required
@admin_required
def edit_farmer(request, user_id):
    farmer = get_object_or_404(User, pk=user_id)

    if request.method == "POST":
        form = FarmerForm(request.POST, instance=farmer)
        if form.is_valid():
            form.save()
            messages.success(request, "Farmer updated successfully.")
            return redirect("manage_farmers")
    else:
        form = FarmerForm(instance=farmer)

    return render(request, "edit_farmer.html", {"form": form, "farmer": farmer})

@login_required
@admin_required
def delete_farmer(request, user_id):
    farmer = get_object_or_404(User, pk=user_id)
    farmer.delete()
    messages.success(request, "Farmer deleted.")
    return redirect("manage_farmers")

@login_required
@admin_required
def add_farmer(request):
    if request.method == "POST":
        form = FarmerCreationForm(request.POST)
        if form.is_valid():
            # Check if trying to create another admin
            if form.cleaned_data.get('role') == 'ADMIN':
                existing_admins = User.objects.filter(role='ADMIN').count()
                if existing_admins >= 1:
                    messages.error(request, "Only one admin is allowed in the system.")
                    return render(request, "add_farmer.html", {"form": form})
            
            form.save()
            messages.success(request, "Farmer added successfully.")
            return redirect("manage_farmers")
    else:
        form = FarmerCreationForm()
    
    return render(request, "add_farmer.html", {"form": form})

@login_required
def user_logout(request):
    """Logout user and redirect to login"""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('login')