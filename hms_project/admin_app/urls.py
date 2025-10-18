# admin_app/urls.py - WORKING VERSION

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import StaffViewSet  # Only import ViewSet

router = DefaultRouter()
router.register(r'staff', StaffViewSet, basename='staff')

app_name = 'admin_app'

urlpatterns = [
    path('', include(router.urls)),
]
