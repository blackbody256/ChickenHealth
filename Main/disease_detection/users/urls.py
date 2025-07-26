from django.urls import path
from .views import (
    SignUpView, 
    CustomLoginView, 
    ProfileEditView, 
    dashboard, 
    admin_dashboard, 
    vet_dashboard, 
    about, 
    CustomPasswordResetView, 
    CustomPasswordResetDoneView, 
    CustomPasswordResetConfirmView, 
    CustomPasswordResetCompleteView,
    manage_farmers,
    edit_farmer,
    delete_farmer,
    add_farmer,
    user_logout
)

urlpatterns = [
    path('signup/', SignUpView.as_view(), name='signup'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('profile/', ProfileEditView.as_view(), name='profile_edit'),
    path('dashboard/', dashboard, name='dashboard'),
    path('admin-dashboard/', admin_dashboard, name='admin_dashboard'),
    path('vet-dashboard/', vet_dashboard, name='vet_dashboard'),
    path('about/', about, name='about'),
    path('password-reset/', CustomPasswordResetView.as_view(), name='password_reset'),
    path('password-reset/done/', CustomPasswordResetDoneView.as_view(), name='password_reset_done'),
    path('password-reset/confirm/<uidb64>/<token>/', CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('password-reset/complete/', CustomPasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('manage-farmers/', manage_farmers, name='manage_farmers'),
    path('edit-farmer/<int:user_id>/', edit_farmer, name='edit_farmer'),
    path('delete-farmer/<int:user_id>/', delete_farmer, name='delete_farmer'),
    path('add-farmer/', add_farmer, name='add_farmer'),
    path('logout/', user_logout, name='logout'),
]