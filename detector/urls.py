from django.urls import path
from . import views

urlpatterns = [
    path('', views.upload_image, name='upload'),
    path('result/<uuid:analysis_id>/', views.result, name='result'),
    path('history/', views.history, name='history'),
]