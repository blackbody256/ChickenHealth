from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'users'

urlpatterns = [
    # Home page at root URL
    path('', views.home, name='home'),  # This will handle the root URL
    
    # Authentication
    path('signup/', views.SignUpView.as_view(), name='signup'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.user_logout, name='logout'),
    
    # User pages
    path('about/', views.about, name='about'),
    
    # Dashboards
    path('dashboard/', views.dashboard, name='dashboard'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('vet-dashboard/', views.vet_dashboard, name='vet_dashboard'),
    
    # Profile management
    path('profile/', views.ProfileEditView.as_view(), name='profile_edit'),
    
    # User management (admin only)
    path('manage-farmers/', views.manage_farmers, name='manage_farmers'),
    path('add-farmer/', views.add_farmer, name='add_farmer'),
    path('edit-farmer/<int:user_id>/', views.edit_farmer, name='edit_farmer'),
    path('delete-farmer/<int:user_id>/', views.delete_farmer, name='delete_farmer'),
    
    # Password reset
    path('password-reset/', views.CustomPasswordResetView.as_view(), name='password_reset'),
    path('password-reset/done/', views.CustomPasswordResetDoneView.as_view(), name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', views.CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('password-reset-complete/', views.CustomPasswordResetCompleteView.as_view(), name='password_reset_complete'),
]