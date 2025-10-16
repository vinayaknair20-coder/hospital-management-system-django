from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Consultation, Prescription, MedicinePrescription, TestPrescription
from .serializers import (ConsultationSerializer, PrescriptionSerializer, 
                          MedicinePrescriptionSerializer, TestPrescriptionSerializer)


class ConsultationViewSet(viewsets.ModelViewSet):
    queryset = Consultation.objects.all()
    serializer_class = ConsultationSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['appointment__doctor_id', 'appointment__Patient_id']
    search_fields = ['symptoms', 'diagnosis', 'appointment__Patient_id__Patient_name']
    ordering = ['-consultation_date']
    
    @action(detail=False, methods=['get'])
    def by_doctor(self, request):
        """Get consultations by doctor ID"""
        doctor_id = request.query_params.get('doctor_id')
        if not doctor_id:
            return Response({'error': 'doctor_id parameter required'}, status=400)
        
        consultations = self.queryset.filter(appointment__doctor_id=doctor_id)
        serializer = self.get_serializer(consultations, many=True)
        return Response(serializer.data)


class PrescriptionViewSet(viewsets.ModelViewSet):
    queryset = Prescription.objects.all()
    serializer_class = PrescriptionSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['consultation']
    ordering = ['-prescription_date']


class MedicinePrescriptionViewSet(viewsets.ModelViewSet):
    queryset = MedicinePrescription.objects.all()
    serializer_class = MedicinePrescriptionSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['prescription']
    search_fields = ['medicine_name']


class TestPrescriptionViewSet(viewsets.ModelViewSet):
    queryset = TestPrescription.objects.all()
    serializer_class = TestPrescriptionSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['prescription']
    search_fields = ['test_name']
