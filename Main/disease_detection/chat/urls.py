from django.urls import path
from . import views

app_name = 'chat'

urlpatterns = [
    path('', views.chat_dashboard, name='dashboard'),  # Main chat dashboard
    path('<int:user_id>/', views.chat_dashboard, name='open_chat'),  # Open chat with specific user
]