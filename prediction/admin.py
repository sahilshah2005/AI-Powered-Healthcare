from django.contrib import admin
from .models import PredictionHistory

@admin.register(PredictionHistory)
class PredictionHistoryAdmin(admin.ModelAdmin):
    list_display = ('user', 'model_used', 'prediction_label', 'probability', 'created_at')
    list_filter = ('model_used', 'prediction', 'created_at')
    search_fields = ('user__username',)
