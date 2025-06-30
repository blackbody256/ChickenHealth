from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse

from .models import ChickenAnalysis


@admin.register(ChickenAnalysis)
class ChickenAnalysisAdmin(admin.ModelAdmin):
    list_display = ['id_short', 'image_thumbnail', 'predicted_disease', 'confidence_score', 'analysis_date', 'view_result_link']
    list_filter = ['predicted_disease', 'analysis_date', 'confidence_score']
    readonly_fields = ['id', 'analysis_date', 'image_preview']
    search_fields = ['predicted_disease', 'id']
    ordering = ['-analysis_date']
    list_per_page = 20
    
    def id_short(self, obj):
        """Display shortened ID for better readability"""
        return str(obj.id)[:8] + '...'
    id_short.short_description = 'ID'
    
    def image_thumbnail(self, obj):
        """Display small thumbnail of the image"""
        if obj.image:
            return format_html(
                '<img src="{}" style="width: 50px; height: 50px; object-fit: cover;" />',
                obj.image.url
            )
        return "No Image"
    image_thumbnail.short_description = 'Thumbnail'
    
    def image_preview(self, obj):
        """Display larger image preview in detail view"""
        if obj.image:
            return format_html(
                '<img src="{}" style="max-width: 300px; max-height: 300px;" />',
                obj.image.url
            )
        return "No Image"
    image_preview.short_description = 'Image Preview'
    
    def view_result_link(self, obj):
        """Add link to view result page"""
        url = reverse('result', args=[obj.id])
        return format_html('<a href="{}" target="_blank">View Result</a>', url)
    view_result_link.short_description = 'Result'
    
    fieldsets = (
        ('Analysis Information', {
            'fields': ('id', 'analysis_date', 'predicted_disease', 'confidence_score')
        }),
        ('Image', {
            'fields': ('image', 'image_preview')
        }),
    )
