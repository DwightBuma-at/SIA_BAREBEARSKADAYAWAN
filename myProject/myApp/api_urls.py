# myApp/api_urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AdminInventoryViewSet

# Create a router and register the AdminInventoryViewSet
router = DefaultRouter()
router.register(r'admininventory', AdminInventoryViewSet)

# Include the router's URLs in your api_urls.py
urlpatterns = [
    path('', include(router.urls)),  # Includes all API endpoints defined in the router
]
