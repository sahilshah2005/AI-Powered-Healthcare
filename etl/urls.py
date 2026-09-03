from django.urls import path
from . import views

urlpatterns = [
    path('status/', views.etl_status, name='etl_status'),
    path('warehouse/', views.warehouse_schema, name='warehouse_schema'),
]
