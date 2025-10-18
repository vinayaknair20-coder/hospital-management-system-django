from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PatientViewSet, AppointmentViewSet, BillViewSet  # ✅ Check this

router = DefaultRouter()
router.register(r'patients', PatientViewSet, basename='patient')
router.register(r'appointments', AppointmentViewSet, basename='appointment')
router.register(r'bills', BillViewSet, basename='bill')  # ✅ Check this

urlpatterns = [
    path('', include(router.urls)),
]
