from django.contrib import admin
from .models import (
    DimGender, DimAgeGroup, DimChestPainType, DimRestECG,
    DimCholesterolCategory, DimBPCategory, DimHeartRateCategory, DimTime,
    PatientFact, ETLLog
)


@admin.register(DimGender)
class DimGenderAdmin(admin.ModelAdmin):
    list_display = ['id', 'gender_name']


@admin.register(DimAgeGroup)
class DimAgeGroupAdmin(admin.ModelAdmin):
    list_display = ['id', 'age_range', 'min_age', 'max_age']
    ordering = ['min_age']


@admin.register(DimChestPainType)
class DimChestPainTypeAdmin(admin.ModelAdmin):
    list_display = ['id', 'cp_code', 'cp_name']


@admin.register(DimRestECG)
class DimRestECGAdmin(admin.ModelAdmin):
    list_display = ['id', 'ecg_code', 'ecg_result']


@admin.register(DimCholesterolCategory)
class DimCholesterolCategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'category_name', 'min_value', 'max_value']


@admin.register(DimBPCategory)
class DimBPCategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'category_name', 'min_value', 'max_value']


@admin.register(DimHeartRateCategory)
class DimHeartRateCategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'category_name', 'min_value', 'max_value']


@admin.register(DimTime)
class DimTimeAdmin(admin.ModelAdmin):
    list_display = ['id', 'etl_date', 'year', 'month', 'quarter']


@admin.register(PatientFact)
class PatientFactAdmin(admin.ModelAdmin):
    list_display = ['id', 'age', 'gender', 'cp_type', 'target', 'etl_batch_id']
    list_filter = ['gender', 'target', 'age_group', 'cp_type']
    search_fields = ['age', 'etl_batch_id']


@admin.register(ETLLog)
class ETLLogAdmin(admin.ModelAdmin):
    list_display = ['batch_id', 'status', 'records_extracted', 'records_loaded',
                    'duration_seconds', 'started_at']
    list_filter = ['status']
    readonly_fields = ['batch_id', 'started_at', 'completed_at', 'status',
                       'records_extracted', 'records_validated', 'records_invalid',
                       'duplicates_detected', 'records_transformed', 'records_loaded',
                       'missing_values_handled', 'duration_seconds', 'error_message',
                       'data_quality_report']
