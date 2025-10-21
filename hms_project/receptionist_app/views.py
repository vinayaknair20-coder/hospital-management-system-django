from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Patient, Appointment, Bill_Generation
from .serializers import (
    PatientSerializer, PatientUpdateSerializer,
    AppointmentSerializer, BillGenerationSerializer, DoctorSerializer
)
from admin_app.models import Staff


class PatientViewSet(viewsets.ModelViewSet):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['Gender', 'Blood_Group', 'is_active']
    search_fields = ['Patient_name', 'Phone_number', 'Email']
    ordering_fields = ['Patient_id', 'Patient_name']
    ordering = ['Patient_name']
    
    def get_serializer_class(self):
        """Use different serializer for updates"""
        if self.action in ['update', 'partial_update']:
            return PatientUpdateSerializer
        return PatientSerializer
    
    def get_queryset(self):
        """Filter active patients"""
        queryset = super().get_queryset()
        active_only = self.request.query_params.get('active_only', None)
        if active_only == 'true':
            queryset = queryset.filter(is_active=True)
        return queryset
    
    @action(detail=True, methods=['post'])
    def disable(self, request, pk=None):
        """Disable a patient (soft delete)"""
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
    
    @action(detail=False, methods=['get'])
    def search_by_phone(self, request):
        """Search patient by phone number"""
        phone = request.query_params.get('phone', None)
        if not phone:
            return Response({'error': 'Phone number required'}, status=status.HTTP_400_BAD_REQUEST)
        
        patients = Patient.objects.filter(Phone_number=phone, is_active=True)
        serializer = self.get_serializer(patients, many=True)
        return Response(serializer.data)


class AppointmentViewSet(viewsets.ModelViewSet):
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'Appointment_date', 'doctor_id']
    search_fields = ['Patient_id__Patient_name', 'doctor_id__staff_name']
    ordering_fields = ['Appointment_date', 'Appointment_time']
    ordering = ['-Appointment_date']

    # ✅ Use only AppointmentSerializer (since it handles creation too)
    def get_serializer_class(self):
        return AppointmentSerializer

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel an appointment"""
        appointment = self.get_object()
        if appointment.status == 'completed':
            return Response(
                {'error': 'Cannot cancel completed appointment'},
                status=status.HTTP_400_BAD_REQUEST
            )
        appointment.status = 'cancelled'
        appointment.save()
        return Response({'message': 'Appointment cancelled successfully'})
    
    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """Mark appointment as completed"""
        appointment = self.get_object()
        if appointment.status == 'cancelled':
            return Response(
                {'error': 'Cannot complete cancelled appointment'},
                status=status.HTTP_400_BAD_REQUEST
            )
        appointment.status = 'completed'
        appointment.save()
        return Response({'message': 'Appointment marked as completed'})


class BillGenerationViewSet(viewsets.ModelViewSet):
    queryset = Bill_Generation.objects.all()
    serializer_class = BillGenerationSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['Patient_id', 'Appointment_id']
    search_fields = ['Token', 'Patient_id__Patient_name']
    
    @action(detail=False, methods=['get'], url_path='search-token')
    def search_by_token(self, request):
        """Search bill by token"""
        token = request.query_params.get('token', None)
        if not token:
            return Response({'error': 'Token required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            bill = Bill_Generation.objects.get(Token=token)
            serializer = self.get_serializer(bill)
            return Response(serializer.data)
        except Bill_Generation.DoesNotExist:
            return Response({'error': 'Bill not found'}, status=status.HTTP_404_NOT_FOUND)


class DoctorViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = DoctorSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['staff_name', 'Email']
    
    def get_queryset(self):
        queryset = Staff.objects.filter(role='DOCTOR', is_active=True)
        specialization_id = self.request.query_params.get('specialization')
        if specialization_id:
            queryset = queryset.filter(specialization_id=specialization_id)
        return queryset
