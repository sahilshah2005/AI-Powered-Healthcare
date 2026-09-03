from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Avg, Min, Max, Q, F
from django.conf import settings
import json
import os
from etl.models import (
    PatientFact, DimGender, DimAgeGroup, DimChestPainType, DimRestECG,
    DimCholesterolCategory, DimBPCategory, DimHeartRateCategory, ETLLog
)


def home(request):
    """Landing page — redirect authenticated users to dashboard."""
    if request.user.is_authenticated:
        return redirect('dashboard_home')
    return render(request, 'dashboard/landing.html')


@login_required
def dashboard_home(request):
    """Executive analytics dashboard with dynamic KPIs and charts."""
    # KPI metrics
    total_patients = PatientFact.objects.count()
    high_risk = PatientFact.objects.filter(target=True).count()
    low_risk = total_patients - high_risk
    risk_pct = round((high_risk / total_patients * 100), 1) if total_patients > 0 else 0

    # ETL status
    latest_etl = ETLLog.objects.first()
    etl_status = 'Never Run'
    if latest_etl:
        etl_status = f"{latest_etl.status} — {latest_etl.started_at.strftime('%b %d, %Y %H:%M')}"

    # Model accuracies
    metrics_file = settings.MODEL_DIR / 'model_metrics.json'
    accuracies = {}
    best_model = 'Not Trained'
    if metrics_file.exists():
        with open(metrics_file, 'r') as f:
            metrics = json.load(f)
            accuracies = {name: round(float(data.get('accuracy', 0)), 1)
                          for name, data in metrics.items()}
            # Find best by F1
            best = max(metrics.items(), key=lambda x: x[1].get('f1_score', x[1].get('f1', 0)))
            best_model = best[0]
    else:
        # Fallback to old accuracies.json format
        old_file = settings.MODEL_DIR / 'accuracies.json'
        if old_file.exists():
            with open(old_file, 'r') as f:
                accuracies = json.load(f)

    # Age vs Risk distribution (using ORM aggregation)
    age_risk_data = PatientFact.objects.values(
        age_range=F('age_group__age_range')
    ).annotate(
        total=Count('id'),
        risk=Count('id', filter=Q(target=True)),
        normal=Count('id', filter=Q(target=False))
    ).order_by('age_group__min_age')

    age_groups = [d['age_range'] for d in age_risk_data]
    risk_by_age = [d['risk'] for d in age_risk_data]
    normal_by_age = [d['normal'] for d in age_risk_data]

    # Gender distribution
    gender_data = PatientFact.objects.values(
        name=F('gender__gender_name')
    ).annotate(
        total=Count('id'),
        risk=Count('id', filter=Q(target=True))
    )

    # Clinical stats
    clinical_stats = PatientFact.objects.aggregate(
        avg_age=Avg('age'),
        avg_chol=Avg('chol'),
        avg_bp=Avg('trestbps'),
        avg_hr=Avg('thalach'),
        min_age=Min('age'),
        max_age=Max('age'),
    )

    # Chest pain distribution
    cp_data = PatientFact.objects.values(
        name=F('cp_type__cp_name')
    ).annotate(
        total=Count('id'),
        risk=Count('id', filter=Q(target=True))
    )

    chart_data = {
        'age_groups': age_groups,
        'risk_by_age': risk_by_age,
        'normal_by_age': normal_by_age,
        'model_names': list(accuracies.keys()),
        'model_accs': list(accuracies.values()),
        'gender_labels': [d['name'] for d in gender_data],
        'gender_risk': [d['risk'] for d in gender_data],
        'gender_total': [d['total'] for d in gender_data],
        'cp_labels': [d['name'] for d in cp_data],
        'cp_risk': [d['risk'] for d in cp_data],
        'cp_total': [d['total'] for d in cp_data],
    }

    context = {
        'total_patients': total_patients,
        'high_risk_patients': high_risk,
        'low_risk_patients': low_risk,
        'risk_percentage': risk_pct,
        'etl_status': etl_status,
        'best_model': best_model,
        'accuracies': accuracies,
        'clinical_stats': clinical_stats,
        'chart_data': json.dumps(chart_data),
    }
    return render(request, 'dashboard/index.html', context)


@login_required
def olap_analytics(request):
    """OLAP Analytics — roll-up, drill-down, slice, dice operations."""
    # Get filter parameters
    filters = {}
    age_group = request.GET.get('age_group')
    sex = request.GET.get('sex')
    cp_type = request.GET.get('cp_type')
    target = request.GET.get('target')
    chol_cat = request.GET.get('chol_category')
    bp_cat = request.GET.get('bp_category')

    queryset = PatientFact.objects.select_related(
        'gender', 'age_group', 'cp_type', 'rest_ecg',
        'chol_category', 'bp_category', 'hr_category'
    )

    active_filters = []
    if age_group:
        queryset = queryset.filter(age_group__age_range=age_group)
        filters['age_group'] = age_group
        active_filters.append(f'Age: {age_group}')
    if sex:
        queryset = queryset.filter(gender__gender_name=sex)
        filters['sex'] = sex
        active_filters.append(f'Gender: {sex}')
    if cp_type:
        queryset = queryset.filter(cp_type__cp_name=cp_type)
        filters['cp_type'] = cp_type
        active_filters.append(f'Chest Pain: {cp_type}')
    if target is not None and target != '':
        queryset = queryset.filter(target=(target == '1'))
        filters['target'] = target
        active_filters.append(f'Target: {"Heart Disease" if target == "1" else "Normal"}')
    if chol_cat:
        queryset = queryset.filter(chol_category__category_name=chol_cat)
        filters['chol_category'] = chol_cat
        active_filters.append(f'Cholesterol: {chol_cat}')
    if bp_cat:
        queryset = queryset.filter(bp_category__category_name=bp_cat)
        filters['bp_category'] = bp_cat
        active_filters.append(f'BP: {bp_cat}')

    total_filtered = queryset.count()

    # OLAP Operations
    # Roll-up: individual → age_group → all
    rollup_by_age = queryset.values(
        age_range=F('age_group__age_range')
    ).annotate(
        count=Count('id'),
        risk_count=Count('id', filter=Q(target=True)),
        avg_chol=Avg('chol'),
        avg_bp=Avg('trestbps'),
        avg_hr=Avg('thalach'),
    ).order_by('age_group__min_age')

    # Drill-down: by gender within current filters
    drilldown_gender = queryset.values(
        gender_name=F('gender__gender_name')
    ).annotate(
        count=Count('id'),
        risk_count=Count('id', filter=Q(target=True)),
        avg_age=Avg('age'),
        avg_chol=Avg('chol'),
    )

    # Drill-down: by chest pain type
    drilldown_cp = queryset.values(
        cp_name=F('cp_type__cp_name')
    ).annotate(
        count=Count('id'),
        risk_count=Count('id', filter=Q(target=True)),
        avg_age=Avg('age'),
    )

    # Summary stats
    summary = queryset.aggregate(
        avg_age=Avg('age'),
        avg_chol=Avg('chol'),
        avg_bp=Avg('trestbps'),
        avg_hr=Avg('thalach'),
        total_risk=Count('id', filter=Q(target=True)),
    )

    # Dimension values for filter dropdowns
    all_age_groups = list(DimAgeGroup.objects.order_by('min_age').values_list('age_range', flat=True))
    all_genders = list(DimGender.objects.values_list('gender_name', flat=True))
    all_cp_types = list(DimChestPainType.objects.values_list('cp_name', flat=True))
    all_chol_cats = list(DimCholesterolCategory.objects.values_list('category_name', flat=True))
    all_bp_cats = list(DimBPCategory.objects.values_list('category_name', flat=True))

    # Chart data
    olap_chart = {
        'rollup_labels': [d['age_range'] for d in rollup_by_age],
        'rollup_counts': [d['count'] for d in rollup_by_age],
        'rollup_risk': [d['risk_count'] for d in rollup_by_age],
        'gender_labels': [d['gender_name'] for d in drilldown_gender],
        'gender_counts': [d['count'] for d in drilldown_gender],
        'gender_risk': [d['risk_count'] for d in drilldown_gender],
        'cp_labels': [d['cp_name'] for d in drilldown_cp],
        'cp_counts': [d['count'] for d in drilldown_cp],
        'cp_risk': [d['risk_count'] for d in drilldown_cp],
    }

    context = {
        'filters': filters,
        'active_filters': active_filters,
        'total_filtered': total_filtered,
        'rollup_data': list(rollup_by_age),
        'drilldown_gender': list(drilldown_gender),
        'drilldown_cp': list(drilldown_cp),
        'summary': summary,
        'all_age_groups': all_age_groups,
        'all_genders': all_genders,
        'all_cp_types': all_cp_types,
        'all_chol_cats': all_chol_cats,
        'all_bp_cats': all_bp_cats,
        'olap_chart': json.dumps(olap_chart),
    }
    return render(request, 'dashboard/olap.html', context)


@login_required
def system_info(request):
    """System information page showing actual application state."""
    import pandas as pd
    import sklearn
    import django

    # Dataset info
    dataset_path = settings.DATASET_DIR / 'heart_disease.csv'
    dataset_info = {'exists': False}
    if dataset_path.exists():
        df = pd.read_csv(dataset_path)
        dataset_info = {
            'exists': True,
            'filename': 'heart_disease.csv',
            'rows': len(df),
            'columns': len(df.columns),
            'column_names': list(df.columns),
            'missing_values': int(df.isnull().sum().sum()),
            'file_size_kb': round(dataset_path.stat().st_size / 1024, 1),
        }

    # Model info
    model_info = {}
    metrics_file = settings.MODEL_DIR / 'model_metrics.json'
    if metrics_file.exists():
        with open(metrics_file, 'r') as f:
            model_info = json.load(f)

    # Check for model files
    model_files = []
    if settings.MODEL_DIR.exists():
        model_files = [f.name for f in settings.MODEL_DIR.iterdir() if f.suffix == '.pkl']

    # ETL info
    latest_etl = ETLLog.objects.first()
    etl_count = ETLLog.objects.count()

    # Warehouse stats
    warehouse_stats = {
        'total_facts': PatientFact.objects.count(),
        'dimensions': {
            'DimGender': DimGender.objects.count(),
            'DimAgeGroup': DimAgeGroup.objects.count(),
            'DimChestPainType': DimChestPainType.objects.count(),
            'DimRestECG': DimRestECG.objects.count(),
            'DimCholesterolCategory': DimCholesterolCategory.objects.count(),
            'DimBPCategory': DimBPCategory.objects.count(),
            'DimHeartRateCategory': DimHeartRateCategory.objects.count(),
        }
    }

    # Mining techniques
    mining_techniques = [
        {'name': 'Classification', 'algorithms': ['Logistic Regression', 'Decision Tree', 'Gaussian Naive Bayes', 'Random Forest']},
        {'name': 'Clustering', 'algorithms': ['K-Means']},
        {'name': 'Association Rule Mining', 'algorithms': ['Apriori']},
    ]

    context = {
        'dataset_info': dataset_info,
        'model_info': model_info,
        'model_files': model_files,
        'latest_etl': latest_etl,
        'etl_count': etl_count,
        'warehouse_stats': warehouse_stats,
        'mining_techniques': mining_techniques,
        'django_version': django.get_version(),
        'sklearn_version': sklearn.__version__,
        'python_version': f'{__import__("sys").version}',
        'db_engine': settings.DATABASES['default']['ENGINE'].split('.')[-1],
    }
    return render(request, 'dashboard/system_info.html', context)
