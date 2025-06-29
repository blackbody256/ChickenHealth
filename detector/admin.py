from django.contrib import admin
from .models import ChickenAnalysis
# Register your models here.

@admin.register(ChickenAnalysis)
class ChickenAnalysisAdmin(admin.ModelAdmin):
    list_display = ['id', 'predicted_disease', 'confidence_score', 'analysis_date']
    list_filter = ['predicted_disease', 'analysis_date']
    readonly_fields = ['id', 'analysis_date']
    search_fields = ['predicted_disease']
