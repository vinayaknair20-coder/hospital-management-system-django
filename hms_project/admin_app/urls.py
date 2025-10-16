from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import StaffViewSet, SpecializationViewSet

router = DefaultRouter()
router.register(r'staff', StaffViewSet, basename='staff')
router.register(r'specializations', SpecializationViewSet, basename='specialization')

urlpatterns = [
    path('', include(router.urls)),
]
