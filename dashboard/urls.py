from django.urls import path
from . import views
from . import olap_views

urlpatterns = [
    path('', views.home, name='home'),
    path('analytics/', views.dashboard_home, name='dashboard_home'),
    path('olap/', olap_views.olap_analytics, name='olap_analytics'),
    path('system-info/', views.system_info, name='system_info'),
]

