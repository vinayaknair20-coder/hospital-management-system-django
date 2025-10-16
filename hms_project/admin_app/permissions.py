from rest_framework.permissions import BasePermission
from .models import Staff


class IsAdmin(BasePermission):
    """Allow only staff with role=Admin."""
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and hasattr(request.user, "staff")
            and request.user.staff.role == Staff.Roles.ADMIN
        )


class IsDoctor(BasePermission):
    """Allow only staff with role=Doctor."""
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and hasattr(request.user, "staff")
            and request.user.staff.role == Staff.Roles.DOCTOR
        )


class IsReceptionist(BasePermission):
    """Allow only staff with role=Receptionist."""
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and hasattr(request.user, "staff")
            and request.user.staff.role == Staff.Roles.RECEPTIONIST
        )


class IsPharmacist(BasePermission):
    """Allow only staff with role=Pharmacist."""
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and hasattr(request.user, "staff")
            and request.user.staff.role == Staff.Roles.PHARMACIST
        )


class IsLabTechnician(BasePermission):
    """Allow only staff with role=Lab Technician."""
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and hasattr(request.user, "staff")
            and request.user.staff.role == Staff.Roles.LAB_TECHNICIAN
        )