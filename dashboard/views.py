from django.shortcuts import render
from django.contrib.auth.decorators import login_required
import os
import json
from etl.models import PatientFact

def home(request):
    return render(request, 'dashboard/landing.html')

@login_required
def dashboard_home(request):
    # Fetch Data Warehouse metrics
    total_patients = PatientFact.objects.count()
    high_risk_patients = PatientFact.objects.filter(target=True).count()
    
    # Read model accuracies
    acc_file = os.path.join('models', 'accuracies.json')
    accuracies = {}
    if os.path.exists(acc_file):
        with open(acc_file, 'r') as f:
            accuracies = json.load(f)
            
    # Prepare chart data for Age vs Target
    age_groups = ['Under 30', '30-39', '40-49', '50-59', '60-69', '70 and above']
    risk_by_age = []
    normal_by_age = []
    
    # We could do this using Django's ORM aggregation, but pure Python is fine for small dataset
    facts = PatientFact.objects.select_related('age_group').all()
    for group in age_groups:
        group_facts = [f for f in facts if f.age_group.age_range == group]
        risk = sum(1 for f in group_facts if f.target)
        normal = len(group_facts) - risk
        risk_by_age.append(risk)
        normal_by_age.append(normal)
        
    context = {
        'total_patients': total_patients,
        'high_risk_patients': high_risk_patients,
        'accuracies': accuracies,
        'chart_data': json.dumps({
            'age_groups': age_groups,
            'risk_by_age': risk_by_age,
            'normal_by_age': normal_by_age,
            'model_names': list(accuracies.keys()),
            'model_accs': list(accuracies.values())
        })
    }
    return render(request, 'dashboard/index.html', context)
