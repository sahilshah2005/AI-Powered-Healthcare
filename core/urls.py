from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('dashboard/', include('dashboard.urls')),
    path('prediction/', include('prediction.urls')),
    path('mining/', include('data_mining.urls')),
    path('etl/', include('etl.urls')),
    path('', include(('dashboard.urls', 'dashboard_root'))),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
