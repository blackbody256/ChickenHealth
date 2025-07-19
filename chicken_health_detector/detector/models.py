from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from django.urls import reverse
import uuid
import os

def get_upload_path(instance, filename):
    """Generate upload path with date organization"""
    date_str = timezone.now().strftime('%Y/%m/%d')
    return f'chicken_images/{date_str}/{instance.id}_{filename}'

# Create your models here.
class ChickenAnalysis(models.Model):
    DISEASE_CHOICES = [
        ('Healthy', 'Healthy'),
        ('Coccidiosis', 'Coccidiosis'),
        ('Salmonella', 'Salmonella'),
        ('Newcastle Disease', 'Newcastle Disease'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    image = models.ImageField(
        upload_to=get_upload_path,
        help_text="Upload an image of chicken droppings for analysis"
    )
    predicted_disease = models.CharField(
        max_length=100, 
        blank=True,
        choices=DISEASE_CHOICES,
        help_text="Predicted disease from ML analysis"
    )
    confidence_score = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)],
        help_text="Confidence score as percentage (0-100)"
    )
    analysis_date = models.DateTimeField(
        default=timezone.now,
        help_text="When the analysis was performed"
    )
    
    class Meta:
        ordering = ['-analysis_date']
        verbose_name = 'Chicken Analysis'
        verbose_name_plural = 'Chicken Analyses'
        indexes = [
            models.Index(fields=['-analysis_date']),
            models.Index(fields=['predicted_disease']),
        ]
    
    def __str__(self):
        return f'Analysis {str(self.id)[:8]} - {self.predicted_disease} ({self.confidence_score:.1f}%)'
    
    def get_absolute_url(self):
        """Return URL to view this analysis result"""
        return reverse('result', args=[self.id])
    
    def delete(self, *args, **kwargs):
        """Override delete to also remove image file"""
        if self.image and os.path.exists(self.image.path):
            os.remove(self.image.path)
        super().delete(*args, **kwargs)
    
    @property
    def is_healthy(self):
        """Check if analysis indicates healthy chicken"""
        return self.predicted_disease == 'Healthy'
    
    @property
    def needs_attention(self):
        """Check if analysis indicates disease requiring attention"""
        return self.predicted_disease and self.predicted_disease != 'Healthy'
    
    @property
    def confidence_level(self):
        """Return human-readable confidence level"""
        if self.confidence_score >= 80:
            return 'High'
        elif self.confidence_score >= 60:
            return 'Medium'
        else:
            return 'Low'