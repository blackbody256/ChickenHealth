from django.urls import path
from . import views

urlpatterns = [
    path('', views.upload_predict, name='index'),
    path('results/<str:predicted_class>/<str:confidence>/<path:uploaded_image_url>/', views.results_view, name='results_view'),
]