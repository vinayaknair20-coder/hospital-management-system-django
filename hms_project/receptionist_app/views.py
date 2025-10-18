# receptionist_app/views.py

"""
Receptionist App Views
Patient, Appointment & Bill Management
"""

from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from decimal import Decimal

# Import all models
from .models import Patient, Appointment,BillGeneration

# Import all serializers
from .serializers import (
    PatientSerializer,
    AppointmentSerializer,
    BillGenerationSerializer
)

from admin_app.models import Staff


class PatientViewSet(viewsets.ModelViewSet):
    """Patient Management ViewSet"""
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer    # 
    permission_classes = [IsAuthenticated]  # ✅ Added authentication  # COMMENTED FOR TESTING
    
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active', 'Gender', 'Blood_Group']
    search_fields = ['Patient_name', 'Phone_number', 'Email']
    ordering = ['Patient_name']
    
    def get_serializer_class(self):
        if self.action in ['update', 'partial_update']:
            return PatientUpdateSerializer
        return PatientSerializer
    
    @action(detail=False, methods=['get'])
    def search(self, request):
        """Search patients by phone number"""
        phone = request.query_params.get('phone', None)
        if not phone:
            return Response(
                {'error': 'Phone number is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        patients = Patient.objects.filter(Phone_number=phone)
        serializer = self.get_serializer(patients, many=True)
        
        return Response({
            'count': patients.count(),
            'results': serializer.data
        }, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'])
    def disable(self, request, pk=None):
        """Disable a patient"""
        patient = self.get_object()
        patient.is_active = False
        patient.save()
        
        return Response({
            'message': f'Patient {patient.Patient_name} has been disabled'
        }, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'])
    def enable(self, request, pk=None):
        """Enable a patient"""
        patient = self.get_object()
        patient.is_active = True
        patient.save()
        
        return Response({
            'message': f'Patient {patient.Patient_name} has been enabled'
        }, status=status.HTTP_200_OK)


class AppointmentViewSet(viewsets.ModelViewSet):
    """Appointment Management ViewSet"""
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer    # 
    permission_classes = [IsAuthenticated]  # ✅ Added authentication  # COMMENTED FOR TESTING
    
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'appointment_date', 'doctor']
    search_fields = ['patient__Patient_name', 'doctor__staff_name']
    ordering = ['-appointment_date', '-appointment_time']
    
    @action(detail=False, methods=['get'])
    def today(self, request):
        """Get today's appointments"""
        from datetime import date
        today = date.today()
        
        appointments = Appointment.objects.filter(appointment_date=today)
        serializer = self.get_serializer(appointments, many=True)
        
        return Response({
            'date': today,
            'count': appointments.count(),
            'appointments': serializer.data
        }, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        """Get upcoming appointments"""
        from datetime import date
        today = date.today()
        
        appointments = Appointment.objects.filter(
            appointment_date__gte=today,
            status__in=['SCHEDULED', 'CONFIRMED']
        ).order_by('appointment_date', 'appointment_time')
        
        serializer = self.get_serializer(appointments, many=True)
        
        return Response({
            'count': appointments.count(),
            'appointments': serializer.data
        }, status=status.HTTP_200_OK)


# ✅ REMOVED BillGenerationViewSet since model doesn't exist
# You can add it later when you create the BillGeneration model


class DoctorViewSet(viewsets.ReadOnlyModelViewSet):
    """Doctor List ViewSet (Read Only)"""
    queryset = Staff.objects.filter(role='DOCTOR', is_active=True)    # 
    permission_classes = [IsAuthenticated]  # ✅ Added authentication  # COMMENTED FOR TESTING
    
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['staff_name', 'specialization__specialization_name']
    ordering = ['staff_name']
# Add to receptionist_app/views.py

from rest_framework.decorators import action

# receptionist_app/views.py - ADD THIS AT THE END

class BillViewSet(viewsets.ModelViewSet):
    """Bill/Invoice Management ViewSet"""
    queryset = BillGeneration.objects.select_related('patient', 'appointment')
    serializer_class = BillGenerationSerializer    # 
    permission_classes = [IsAuthenticated]  # COMMENTED FOR TESTING
    
    @action(detail=False, methods=['get'])
    def pending(self, request):
        """Get all pending bills"""
        bills = self.queryset.filter(payment_status='PENDING')
        serializer = self.get_serializer(bills, many=True)
        return Response({
            'count': bills.count(),
            'bills': serializer.data
        })
    