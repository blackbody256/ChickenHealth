from django.db import models
from users.models import User

class Diagnosis(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='diagnoses/')
    disease_name = models.CharField(max_length=255)
    confidence = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.username} - {self.disease_name} ({self.timestamp.strftime('%Y-%m-%d %H:%M')})'