from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    StaffListCreateView, StaffDetailView,
    DoctorListCreateView, DoctorDetailView,
    SpecializationListCreateView,
    RegisterView, CustomTokenObtainPairView,
    admin_dashboard, doctor_dashboard, receptionist_dashboard
)

urlpatterns = [
    # ---------- Auth ----------
    path("register/", RegisterView.as_view(), name="register"),   # Admin creates users
    path("token/", CustomTokenObtainPairView.as_view(), name="token_obtain_pair"),  # Login
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),

    # ---------- Staff Management (Admin only) ----------
    path("staff/", StaffListCreateView.as_view(), name="staff-list-create"),
    path("staff/<int:pk>/", StaffDetailView.as_view(), name="staff-detail"),

    # ---------- Doctor Management (Admin only) ----------
    path("doctors/", DoctorListCreateView.as_view(), name="doctor-list-create"),
    path("doctors/<int:pk>/", DoctorDetailView.as_view(), name="doctor-detail"),

    # ---------- Specialization Management (Admin only) ----------
    path("specializations/", SpecializationListCreateView.as_view(), name="specialization-list-create"),

    # ---------- Dashboards ----------
    path("admin-dashboard/", admin_dashboard, name="admin-dashboard"),
    path("doctor-dashboard/", doctor_dashboard, name="doctor-dashboard"),
    path("receptionist-dashboard/", receptionist_dashboard, name="receptionist-dashboard"),
    #path("pharmacist-dashboard/", pharmacist_dashboard, name="pharmacist-dashboard"),
    #path("lab-technician-dashboard/", lab_technician_dashboard, name="lab-technician-dashboard"),
]