# admin_app/permissions.py - CORRECTED VERSION

from rest_framework.permissions import BasePermission
from .models import Staff


class IsAdmin(BasePermission):
    """Allow only staff with role=Admin."""
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and hasattr(request.user, "role")  # ✅ Check 'role' directly
            and request.user.role == Staff.Roles.ADMIN  # ✅ No .staff needed
        )


class IsDoctor(BasePermission):
    """Allow only staff with role=Doctor."""
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and hasattr(request.user, "role")
            and request.user.role == Staff.Roles.DOCTOR
        )


class IsReceptionist(BasePermission):
    """Allow only staff with role=Receptionist."""
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and hasattr(request.user, "role")
            and request.user.role == Staff.Roles.RECEPTIONIST
        )


class IsPharmacist(BasePermission):
    """Allow only staff with role=Pharmacist."""
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and hasattr(request.user, "role")  # ✅ CHANGED THIS
            and request.user.role == Staff.Roles.PHARMACIST  # ✅ CHANGED THIS
        )


class IsLabTechnician(BasePermission):
    """Allow only staff with role=Lab Technician."""
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and hasattr(request.user, "role")
            and request.user.role == Staff.Roles.LAB_TECHNICIAN
        )
