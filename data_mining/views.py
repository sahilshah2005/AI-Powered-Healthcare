from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from .utils import run_kmeans, run_apriori

@login_required
def clustering_view(request):
    n_clusters = request.GET.get('n_clusters')
    if n_clusters:
        try:
            n_clusters = int(n_clusters)
        except ValueError:
            n_clusters = None

    cache_key = f'clustering_results_{n_clusters}'
    results = cache.get(cache_key)

    if not results:
        results = run_kmeans(n_clusters=n_clusters)
        cache.set(cache_key, results, 300) # 5 minutes

    context = {
        'samples': results.get('samples', []),
        'summary': results.get('summary', {}),
        'profiles': results.get('profiles', {}),
        'elbow_data': results.get('elbow_data', {}),
        'cluster_centers': results.get('cluster_centers', {}),
        'selected_k': n_clusters or 3
    }

    return render(request, 'data_mining/clustering.html', context)

@login_required
def association_rules_view(request):
    try:
        min_support = float(request.GET.get('min_support', 0.1))
    except ValueError:
        min_support = 0.1
        
    try:
        min_confidence = float(request.GET.get('min_confidence', 0.6))
    except ValueError:
        min_confidence = 0.6
        
    try:
        min_lift = float(request.GET.get('min_lift', 1.0))
    except ValueError:
        min_lift = 1.0

    consequent_filter = request.GET.get('consequent', '')

    cache_key = f'apriori_{min_support}_{min_confidence}_{min_lift}'
    rules = cache.get(cache_key)

    if rules is None:
        rules = run_apriori(min_support=min_support, min_confidence=min_confidence, min_lift=min_lift)
        cache.set(cache_key, rules, 300) # 5 minutes

    if consequent_filter:
        filtered_rules = [r for r in rules if any(consequent_filter.lower() in c.lower() for c in r['consequents'])]
    else:
        filtered_rules = rules

    context = {
        'rules': filtered_rules,
        'min_support': min_support,
        'min_confidence': min_confidence,
        'min_lift': min_lift,
        'consequent_filter': consequent_filter,
        'total_rules': len(filtered_rules)
    }

    return render(request, 'data_mining/association_rules.html', context)
