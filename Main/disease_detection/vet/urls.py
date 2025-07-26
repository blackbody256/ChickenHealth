from django.urls import path
from . import views

app_name = 'vet'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),  # Using existing function
    path('list/', views.dataset_list, name='dataset_list'),  # Using existing function
    path('upload/', views.upload_data, name='upload_data'),  # Using existing function
    path('uploads/', views.view_uploads, name='view_uploads'),  # Using existing function
    path('delete/<int:upload_id>/', views.delete_upload, name='delete_upload'),  # Using existing function
    path('report/', views.vet_report, name='report'),  # Using existing function
    path('report-view/', views.report_view, name='report_view'),  # Using existing function
]
