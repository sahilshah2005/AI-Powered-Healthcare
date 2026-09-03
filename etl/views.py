from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.conf import settings
import json
import os
from .models import ETLLog, PatientFact, DimGender, DimAgeGroup, DimChestPainType, DimRestECG


@login_required
def etl_status(request):
    """ETL Pipeline monitoring and status page."""
    # Get ETL execution history
    etl_logs = ETLLog.objects.all()[:10]

    # Get latest ETL log
    latest_log = ETLLog.objects.first()

    # Current warehouse stats
    total_facts = PatientFact.objects.count()
    dim_stats = {
        'genders': DimGender.objects.count(),
        'age_groups': DimAgeGroup.objects.count(),
        'chest_pain_types': DimChestPainType.objects.count(),
        'rest_ecg_types': DimRestECG.objects.count(),
    }

    # Data quality from latest run
    quality_report = {}
    if latest_log and latest_log.data_quality_report:
        quality_report = latest_log.data_quality_report

    context = {
        'etl_logs': etl_logs,
        'latest_log': latest_log,
        'total_facts': total_facts,
        'dim_stats': dim_stats,
        'quality_report': quality_report,
    }
    return render(request, 'etl/status.html', context)


@login_required
def warehouse_schema(request):
    """Data Warehouse star schema visualization."""
    # Get actual schema statistics
    schema_info = {
        'fact_table': {
            'name': 'PatientFact',
            'record_count': PatientFact.objects.count(),
            'fields': [f.name for f in PatientFact._meta.get_fields() if hasattr(f, 'column')],
        },
        'dimensions': [
            {'name': 'DimGender', 'count': DimGender.objects.count(),
             'values': list(DimGender.objects.values_list('gender_name', flat=True))},
            {'name': 'DimAgeGroup', 'count': DimAgeGroup.objects.count(),
             'values': list(DimAgeGroup.objects.order_by('min_age').values_list('age_range', flat=True))},
            {'name': 'DimChestPainType', 'count': DimChestPainType.objects.count(),
             'values': list(DimChestPainType.objects.values_list('cp_name', flat=True))},
            {'name': 'DimRestECG', 'count': DimRestECG.objects.count(),
             'values': list(DimRestECG.objects.values_list('ecg_result', flat=True))},
        ],
    }

    context = {
        'schema_info': schema_info,
        'schema_json': json.dumps(schema_info, default=str),
    }
    return render(request, 'warehouse/schema.html', context)
