from django.urls import path
from . import views

urlpatterns = [
    path('', views.mining_dashboard, name='mining_dashboard'),
]
