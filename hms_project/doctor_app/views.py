from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets, filters, status
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Consultation, Prescription, TestPrescription, MedicinePrescription
from .serializers import (
    ConsultationSerializer,
    PrescriptionSerializer,
    TestPrescriptionSerializer,
    MedicinePrescriptionSerializer,
)


class ConsultationViewSet(viewsets.ModelViewSet):
    queryset = Consultation.objects.all().select_related("appointment")
    serializer_class = ConsultationSerializer
    # permission_classes = [IsAuthenticated]

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['symptoms', 'diagnosis', 'appointment__patient__Patient_name']
    ordering_fields = ['consultation_date']
    filterset_fields = {
        'appointment__doctor__id': ['exact'],
        'appointment__patient__id': ['exact'],
    }

    @action(detail=False, methods=['get'], url_path='my-appointments')
    def my_appointments(self, request):
        """
        Return appointments for the logged-in doctor.

        NOTE: This assumes your Doctor model has a OneToOne or ForeignKey linking it to the Django User model,
        for example: Doctor.user = models.OneToOneField(User, ...) OR Doctor.user_id field.
        If you do not have that mapping, you can pass ?doctor_id=<id> as a fallback.
        """
        user = request.user

        # Try to find a doctor linked to this user (common pattern)
        doctor_qs = None
        try:
            # common field name: 'user' on Doctor model
            from admin_app.models import Doctor as AdminDoctorModel  # adjust path if needed
            doctor_qs = AdminDoctorModel.objects.filter(user=user)
        except Exception:
            doctor_qs = None

        doctor_id = None
        if doctor_qs and doctor_qs.exists():
            doctor_id = doctor_qs.first().id
        else:
            # Fallback: allow ?doctor_id=<id>
            doctor_id = request.query_params.get("doctor_id")

        if not doctor_id:
            return Response(
                {"detail": "Doctor not found for this user; provide ?doctor_id=<id> as fallback."},
                status=status.HTTP_400_BAD_REQUEST
            )

        qs = self.queryset.filter(appointment__doctor__id=doctor_id)
        page = self.paginate_queryset(qs)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)


class PrescriptionViewSet(viewsets.ModelViewSet):
    queryset = Prescription.objects.all().select_related("consultation__appointment")
    serializer_class = PrescriptionSerializer
    # permission_classes = [IsAuthenticated]

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = [
        'consultation__appointment__doctor__DoctorName',
        'consultation__appointment__patient__Patient_name',
    ]
    filterset_fields = {
        'id': ['exact'],
        'consultation__appointment__doctor__id': ['exact'],
        'consultation__appointment__patient__id': ['exact'],
    }
    ordering_fields = ['prescription_date']
    ordering = ['-prescription_date']

    @action(detail=False, methods=['get'], url_path='by-doctor/(?P<doctor_id>[^/.]+)')
    def by_doctor(self, request, doctor_id=None):
        """
        Return all prescriptions for the specified doctor id.
        """
        qs = self.queryset.filter(consultation__appointment__doctor__id=doctor_id)
        page = self.paginate_queryset(qs)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='by-patient/(?P<patient_id>[^/.]+)')
    def by_patient(self, request, patient_id=None):
        qs = self.queryset.filter(consultation__appointment__patient__id=patient_id)
        page = self.paginate_queryset(qs)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)


class TestPrescriptionViewSet(viewsets.ModelViewSet):
    queryset = TestPrescription.objects.all().select_related("prescription")
    serializer_class = TestPrescriptionSerializer
    # permission_classes = [IsAuthenticated]


class MedicinePrescriptionViewSet(viewsets.ModelViewSet):
    queryset = MedicinePrescription.objects.all().select_related("prescription", "medicine")
    serializer_class = MedicinePrescriptionSerializer
    # permission_classes = [IsAuthenticated]
