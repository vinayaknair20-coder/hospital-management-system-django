from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.views import TokenObtainPairView

from .models import Staff, Doctor, Specialization
from .serializers import (
    StaffSerializer,
    DoctorSerializer,
    SpecializationSerializer,
    CustomTokenObtainPairSerializer,
)

User = get_user_model()


# ==============================
# Auth Views
# ==============================
class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class RegisterView(generics.CreateAPIView):
    """
    Admin creates staff accounts.
    """
    queryset = Staff.objects.all()
    serializer_class = StaffSerializer
    permission_classes = [permissions.IsAdminUser]


# ==============================
# Staff Views
# ==============================
class StaffListCreateView(generics.ListCreateAPIView):
    queryset = Staff.objects.all()
    serializer_class = StaffSerializer
    permission_classes = [permissions.IsAuthenticated]


class StaffDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Staff.objects.all()
    serializer_class = StaffSerializer
    permission_classes = [permissions.IsAuthenticated]


# ==============================
# Doctor Views
# ==============================
class DoctorListCreateView(generics.ListCreateAPIView):
    queryset = Doctor.objects.all()
    serializer_class = DoctorSerializer
    permission_classes = [permissions.IsAuthenticated]


class DoctorDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Doctor.objects.all()
    serializer_class = DoctorSerializer
    permission_classes = [permissions.IsAuthenticated]


# ==============================
# Specialization Views
# ==============================
class SpecializationListCreateView(generics.ListCreateAPIView):
    queryset = Specialization.objects.all()
    serializer_class = SpecializationSerializer
    permission_classes = [permissions.IsAuthenticated]


# ==============================
# Dashboards
# ==============================
@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def admin_dashboard(request):
    return Response({
        "message": "Welcome to the Admin Dashboard",
        "total_staff": Staff.objects.count(),
        "total_doctors": Doctor.objects.count(),
        "total_specializations": Specialization.objects.count(),
    })


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def doctor_dashboard(request):
    return Response({
        "message": "Welcome to the Doctor Dashboard",
        "your_profile": DoctorSerializer(
            Doctor.objects.filter(staff=request.user).first()
        ).data if request.user.role == Staff.Roles.DOCTOR else None
    })


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def receptionist_dashboard(request):
    return Response({
        "message": "Welcome to the Receptionist Dashboard",
        "role": request.user.role,
    })