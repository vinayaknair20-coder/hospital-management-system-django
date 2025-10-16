from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    PatientViewSet,
    AppointmentViewSet,
    BillGenerationViewSet,
    DoctorViewSet
)

# Create a router and register viewsets
router = DefaultRouter()
router.register(r'patients', PatientViewSet, basename='patient')
router.register(r'appointments', AppointmentViewSet, basename='appointment')
router.register(r'bills', BillGenerationViewSet, basename='bill')
router.register(r'doctors', DoctorViewSet, basename='doctor')

app_name = 'receptionist_app'

urlpatterns = [
    # Router URLs
    path('', include(router.urls)),
]

# Available endpoints:
# Patients:
#   GET/POST /patients/ - List/Create patients
#   GET/PUT/PATCH/DELETE /patients/{id}/ - Retrieve/Update/Delete patient
#   GET /patients/{id}/appointments/ - Get patient appointments
#   GET /patients/{id}/bills/ - Get patient bills
#
# Appointments:
#   GET/POST /appointments/ - List/Create appointments
#   GET/PUT/PATCH/DELETE /appointments/{id}/ - Retrieve/Update/Delete appointment
#   POST /appointments/{id}/cancel/ - Cancel appointment
#   POST /appointments/{id}/complete/ - Complete appointment
#
# Bills:
#   GET/POST /bills/ - List/Create bills
#   GET/PUT/PATCH/DELETE /bills/{id}/ - Retrieve/Update/Delete bill
#   GET /bills/by_token/?token=PAT123 - Get bill by token
#
# Doctors:
#   GET /doctors/ - List doctors
#   GET /doctors/{id}/ - Retrieve doctor details
