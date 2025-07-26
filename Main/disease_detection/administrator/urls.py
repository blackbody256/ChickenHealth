from django.urls import path
from . import views

app_name = 'administrator'

urlpatterns = [
    path('upload/', views.upload_dataset_view, name='upload_dataset'),  # Using existing function
    path('datasets/', views.dataset_list_view, name='dataset_list'),  # Using existing function
    path('delete/<int:pk>/', views.delete_dataset_view, name='delete_dataset'),  # Using existing function
]