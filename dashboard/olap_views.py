from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db import models
from django.db.models import Count, Avg, F
from etl.models import PatientFact, DimAgeGroup, DimGender, DimChestPainType, DimCholesterolCategory, DimBPCategory

@login_required
def olap_analytics(request):
    # Base queryset
    qs = PatientFact.objects.select_related(
        'age_group', 'gender', 'cp_type', 'chol_category', 'bp_category'
    ).all()

    # Get filters
    filters = {
        'age_group': request.GET.get('age_group'),
        'sex': request.GET.get('sex'),
        'cp_type': request.GET.get('cp_type'),
        'target': request.GET.get('target'),
        'chol_category': request.GET.get('chol_category'),
        'bp_category': request.GET.get('bp_category'),
    }

    # Apply filters (SLICE & DICE)
    if filters['age_group']:
        qs = qs.filter(age_group__age_range=filters['age_group'])
    if filters['sex']:
        qs = qs.filter(gender__gender_name=filters['sex'])
    if filters['cp_type']:
        qs = qs.filter(cp_type__cp_name=filters['cp_type'])
    if filters['target']:
        target_val = filters['target'].lower() == 'true'
        qs = qs.filter(target=target_val)
    if filters['chol_category']:
        qs = qs.filter(chol_category__category_name=filters['chol_category'])
    if filters['bp_category']:
        qs = qs.filter(bp_category__category_name=filters['bp_category'])

    # Total records matching filters
    total_records = qs.count()

    # Summary Statistics
    summary_stats = qs.aggregate(
        avg_age=Avg('age'),
        avg_chol=Avg('chol'),
        avg_trestbps=Avg('trestbps'),
        avg_thalach=Avg('thalach')
    )

    # ROLL-UP: Aggregate by age_group
    rollup_data = list(qs.values(
        group=F('age_group__age_range')
    ).annotate(
        count=Count('id'),
        avg_chol=Avg('chol'),
        avg_bp=Avg('trestbps')
    ).order_by('group'))

    # DRILL-DOWN: From age_group to detailed breakdown by sex and cp_type
    drilldown_data = list(qs.values(
        age_group_name=F('age_group__age_range'),
        gender_name=F('gender__gender_name'),
        cp_name=F('cp_type__cp_name')
    ).annotate(
        count=Count('id'),
        target_true_count=Count('id', filter=models.Q(target=True))
    ).order_by('age_group_name', 'gender_name', 'cp_name')[:100]) # Limit to 100 for display

    # Dropdown options
    options = {
        'age_groups': DimAgeGroup.objects.values_list('age_range', flat=True).distinct(),
        'genders': DimGender.objects.values_list('gender_name', flat=True).distinct(),
        'cp_types': DimChestPainType.objects.values_list('cp_name', flat=True).distinct(),
        'chol_categories': DimCholesterolCategory.objects.values_list('category_name', flat=True).distinct(),
        'bp_categories': DimBPCategory.objects.values_list('category_name', flat=True).distinct(),
    }

    context = {
        'filters': filters,
        'total_records': total_records,
        'summary_stats': summary_stats,
        'rollup_data': rollup_data,
        'drilldown_data': drilldown_data,
        'options': options
    }

    return render(request, 'dashboard/olap.html', context)
