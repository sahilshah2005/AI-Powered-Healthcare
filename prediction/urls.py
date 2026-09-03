from django.urls import path
from . import views

urlpatterns = [
    path('predict/', views.predict_heart_disease, name='predict'),
    path('history/', views.prediction_history, name='prediction_history'),
    path('history/<int:pk>/', views.prediction_detail, name='prediction_detail'),
    path('comparison/', views.model_comparison, name='model_comparison'),
    path('batch/', views.batch_predict, name='batch_predict'),
]
