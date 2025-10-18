from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import LabTestViewSet, TestResultViewSet  # ✅ Check if TestResultViewSet exists

router = DefaultRouter()
router.register(r'tests', LabTestViewSet, basename='lab-test')
router.register(r'results', TestResultViewSet, basename='test-result')  # ✅ Add if missing

urlpatterns = [
    path('', include(router.urls)),
]
