from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('dashboard/', include('dashboard.urls')),
    path('prediction/', include('prediction.urls')),
    path('mining/', include('data_mining.urls')),
    path('', include('dashboard.urls')), # Dashboard will also handle home
]
