# doctor_app/views.py - COMPLETE FILE
"""
Doctor App Views
Consultation and Prescription Management
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db.models import Count, Q
from datetime import datetime, timedelta

from .models import (
    Consultation,
    Prescription,
    MedicinePrescription,
    TestPrescription
)
from .serializers import (
    ConsultationSerializer,
    PrescriptionSerializer,
    MedicinePrescriptionSerializer,
    TestPrescriptionSerializer
)
from admin_app.permissions import IsDoctor
from receptionist_app.models import Appointment
from admin_app.models import Staff


class ConsultationViewSet(viewsets.ModelViewSet):
    """Consultation Management ViewSet"""
    queryset = Consultation.objects.select_related(
        'appointment',
        'patient',
        'doctor'
    )
    serializer_class = ConsultationSerializer    # 
    permission_classes = [IsAuthenticated]  # ✅ Added authentication  # COMMENTED FOR TESTING
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by doctor if user is a doctor
        if hasattr(self.request.user, 'role') and self.request.user.role == 'DOCTOR':
            queryset = queryset.filter(doctor=self.request.user)
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def today(self, request):
        """Get today's consultations"""
        today = timezone.now().date()
        
        consultations = self.get_queryset().filter(
            consultation_date=today
        ).order_by('-consultation_time')
        
        serializer = self.get_serializer(consultations, many=True)
        
        return Response({
            'date': today,
            'count': consultations.count(),
            'consultations': serializer.data
        }, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        """Get upcoming consultations"""
        today = timezone.now().date()
        
        consultations = self.get_queryset().filter(
            consultation_date__gte=today,
            status__in=['SCHEDULED', 'IN_PROGRESS']
        ).order_by('consultation_date', 'consultation_time')
        
        serializer = self.get_serializer(consultations, many=True)
        
        return Response({
            'count': consultations.count(),
            'consultations': serializer.data
        }, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Get consultation statistics"""
        queryset = self.get_queryset()
        today = timezone.now().date()
        
        stats = {
            'total': queryset.count(),
            'today': queryset.filter(consultation_date=today).count(),
            'completed': queryset.filter(status='COMPLETED').count(),
            'pending': queryset.filter(status__in=['SCHEDULED', 'IN_PROGRESS']).count(),
            'cancelled': queryset.filter(status='CANCELLED').count()
        }
        
        return Response(stats, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """Mark consultation as completed"""
        consultation = self.get_object()
        consultation.status = 'COMPLETED'
        consultation.save()
        
        return Response({
            'message': 'Consultation marked as completed',
            'consultation_id': consultation.consultation_id,
            'status': consultation.status
        }, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel consultation"""
        consultation = self.get_object()
        consultation.status = 'CANCELLED'
        consultation.save()
        
        return Response({
            'message': 'Consultation cancelled',
            'consultation_id': consultation.consultation_id,
            'status': consultation.status
        }, status=status.HTTP_200_OK)


class PrescriptionViewSet(viewsets.ModelViewSet):
    """Prescription Management ViewSet"""
    queryset = Prescription.objects.select_related(
        'consultation',
        'patient',
        'doctor'
    )
    serializer_class = PrescriptionSerializer    # 
    permission_classes = [IsAuthenticated]  # ✅ Added authentication  # COMMENTED FOR TESTING


class MedicinePrescriptionViewSet(viewsets.ModelViewSet):
    """Medicine Prescription ViewSet"""
    queryset = MedicinePrescription.objects.select_related(
        'prescription',
        'medicine'
    )
    serializer_class = MedicinePrescriptionSerializer    # 
    permission_classes = [IsAuthenticated]  # ✅ Added authentication  # COMMENTED FOR TESTING


class TestPrescriptionViewSet(viewsets.ModelViewSet):
    """Test Prescription ViewSet"""
    queryset = TestPrescription.objects.select_related(
        'prescription',
        'lab_test'
    )
    serializer_class = TestPrescriptionSerializer    # 
    permission_classes = [IsAuthenticated]  # ✅ Added authentication  # COMMENTED FOR TESTING
