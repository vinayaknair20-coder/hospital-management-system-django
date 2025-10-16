from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import LabTestViewSet, TestResultViewSet

router = DefaultRouter()
router.register(r'lab-tests', LabTestViewSet, basename='lab-test')
router.register(r'test-results', TestResultViewSet, basename='test-result')

urlpatterns = [
    path('', include(router.urls)),
]
