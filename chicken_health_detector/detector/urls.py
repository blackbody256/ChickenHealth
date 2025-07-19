from django.urls import path
from . import views

urlpatterns = [
    path('', views.upload_image, name='upload'),
    path('result/<uuid:analysis_id>/', views.result, name='result'),
    path('history/', views.history, name='history'),
    path('delete/<uuid:analysis_id>/', views.delete_analysis, name='delete_analysis'),
    path('api/status/', views.api_status, name='api_status'),
    path('result/<uuid:analysis_id>/', views.result_detail, name='result'),
    path('delete/<uuid:analysis_id>/', views.delete_analysis, name='delete_analysis'),
    path('history/', views.history, name='history'),
]