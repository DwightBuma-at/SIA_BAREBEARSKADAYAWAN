from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),  # Admin site
    path('', include('myApp.urls')),  # Includes the app's URLs for regular pages
    path('api/', include('myApp.api_urls')),  # Includes the API endpoints
    
]

# Add this to serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
