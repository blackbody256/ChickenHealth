from django.db import models
from django.utils import timezone
import uuid

# Create your models here.
class ChickenAnalysis(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    image = models.ImageField(upload_to='chicken_images/')
    predicted_disease = models.CharField(max_length=100, blank=True)
    confidence_score = models.FloatField(default=0.0)
    analysis_date = models.DateTimeField(default=timezone.now)
    
    class Meta: # Meta class to define model options like ordering, verbose name, etc.
        ordering = ['-analysis_date']  # Order by analysis date, newest first
    
    def __str__(self):
        return f'Analysis {self.id} - {self.predicted_disease} ({self.confidence_score:.2f}) on {self.analysis_date.strftime("%Y-%m-%d %H:%M:%S")}'