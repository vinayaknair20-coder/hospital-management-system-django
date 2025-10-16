from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (ConsultationViewSet, PrescriptionViewSet, 
                    MedicinePrescriptionViewSet, TestPrescriptionViewSet)

router = DefaultRouter()
router.register(r'consultations', ConsultationViewSet, basename='consultation')
router.register(r'prescriptions', PrescriptionViewSet, basename='prescription')
router.register(r'medicine-prescriptions', MedicinePrescriptionViewSet, basename='medicine-prescription')
router.register(r'test-prescriptions', TestPrescriptionViewSet, basename='test-prescription')

urlpatterns = [
    path('', include(router.urls)),
]
