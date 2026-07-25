from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .utils import run_kmeans, run_apriori

@login_required
def mining_dashboard(request):
    # Run K-Means Clustering
    kmeans_data = run_kmeans()
    
    # Run Apriori Association Rules
    rules = run_apriori()
    
    context = {
        'clusters': kmeans_data.get('samples', []),
        'cluster_summary': kmeans_data.get('summary', {}),
        'rules': rules
    }
    
    return render(request, 'data_mining/mining.html', context)
