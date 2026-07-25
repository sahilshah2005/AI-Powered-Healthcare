from django.urls import path
from . import views

urlpatterns = [
    path('predict/', views.predict_heart_disease, name='predict'),
]
