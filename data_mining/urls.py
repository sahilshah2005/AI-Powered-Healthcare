from django.urls import path
from . import views

urlpatterns = [
    path('clustering/', views.clustering_view, name='clustering'),
    path('association-rules/', views.association_rules_view, name='association_rules'),
]
