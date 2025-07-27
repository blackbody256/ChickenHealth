from django.urls import path
from . import views

app_name = 'diagnosis'

urlpatterns = [
    path('', views.upload_predict, name='index'),
    path('upload/', views.upload_predict, name='upload_predict'),
    path('results/<str:predicted_class>/<str:confidence>/<path:uploaded_image_url>/', 
         views.results_view, name='results_view'),
    path('history/', views.diagnosis_history, name='history'),
    path('detail/<int:diagnosis_id>/', views.diagnosis_detail, name='detail'),
    path('reanalyze/<int:diagnosis_id>/', views.reanalyze_diagnosis, name='reanalyze'),
]