from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('analytics/', views.dashboard_home, name='dashboard_home'),
]
