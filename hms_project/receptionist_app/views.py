from django.shortcuts import render
from rest_framework import viewsets
# from admin_app.models import Doctor
from .models import Patient,Doctor, Appointment, Bill_Generation
from .serializers import PatientSerializer, AppointmentSerializer, BillGenerationSerializer,DoctorSerializer
# List all specializations


# Create your views here.

class PatientViewSet(viewsets.ModelViewSet):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer

class AppointmentViewSet(viewsets.ModelViewSet):
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer

class BillGenerationViewSet(viewsets.ModelViewSet):
    queryset = Bill_Generation.objects.all()
    serializer_class = BillGenerationSerializer


    def get_queryset(self):
        queryset = Doctor.objects.all()
        specialization_id = self.request.query_params.get('specialization')
        if specialization_id:
            queryset = queryset.filter(specialization_id=specialization_id)
        return queryset
