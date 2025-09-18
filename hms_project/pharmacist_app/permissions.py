"""
PHARMACIST APP PERMISSIONS
Custom permission classes for pharmacy operations
"""

from rest_framework import permissions
from django.contrib.auth.models import Group


class IsPharmacist(permissions.BasePermission):
    """
    Permission for pharmacist-only actions
    """
    
    def has_permission(self, request, view):
        """Check if user is authenticated and is a pharmacist"""
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Super users have all permissions
        if request.user.is_superuser:
            return True
        
        # Check if user is in Pharmacist group or is staff
        return (
            request.user.groups.filter(name='Pharmacist').exists() or 
            request.user.is_staff
        )
    
    def has_object_permission(self, request, view, obj):
        """Object-level permission check"""
        return self.has_permission(request, view)


class IsPharmacistOrReadOnly(permissions.BasePermission):
    """
    Permission that allows read access to anyone but write access only to pharmacists
    """
    
    def has_permission(self, request, view):
        """Check permissions based on request method"""
        # Read permissions for any authenticated user
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated
        
        # Write permissions only for pharmacists
        if not request.user or not request.user.is_authenticated:
            return False
        
        if request.user.is_superuser:
            return True
        
        return (
            request.user.groups.filter(name='Pharmacist').exists() or 
            request.user.is_staff
        )
    
    def has_object_permission(self, request, view, obj):
        """Object-level permissions"""
        # Read permissions for any authenticated user
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated
        
        # Write permissions only for pharmacists
        return self.has_permission(request, view)


class IsSaleOwnerOrPharmacist(permissions.BasePermission):
    """
    Permission for sale objects - only the pharmacist who created it or any pharmacist can modify
    """
    
    def has_permission(self, request, view):
        """Basic permission check"""
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        """Object-level permission for sales"""
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Super users have all permissions
        if request.user.is_superuser:
            return True
        
        # Read permissions for any authenticated user
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions for the pharmacist who created the sale or any pharmacist
        if hasattr(obj, 'pharmacist') and obj.pharmacist == request.user:
            return True
        
        return (
            request.user.groups.filter(name='Pharmacist').exists() or 
            request.user.is_staff
        )


class IsOwnerOrPharmacist(permissions.BasePermission):
    """
    Generic permission for objects with an owner field
    """
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        if not request.user or not request.user.is_authenticated:
            return False
        
        if request.user.is_superuser:
            return True
        
        # Check if user is the owner
        owner_fields = ['created_by', 'user', 'pharmacist', 'resolved_by']
        for field in owner_fields:
            if hasattr(obj, field):
                owner = getattr(obj, field)
                if owner == request.user:
                    return True
        
        # Check if user is a pharmacist
        return (
            request.user.groups.filter(name='Pharmacist').exists() or 
            request.user.is_staff
        )


class CanDispenseMedicine(permissions.BasePermission):
    """
    Special permission for medicine dispensing operations
    """
    
    def has_permission(self, request, view):
        """Check if user can dispense medicines"""
        if not request.user or not request.user.is_authenticated:
            return False
        
        if request.user.is_superuser:
            return True
        
        # Only pharmacists can dispense medicines
        return (
            request.user.groups.filter(name='Pharmacist').exists() or 
            request.user.is_staff
        )
    
    def has_object_permission(self, request, view, obj):
        """Object-level permission for dispensing"""
        return self.has_permission(request, view)


class CanManageStock(permissions.BasePermission):
    """
    Permission for stock management operations
    """
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        if request.user.is_superuser:
            return True
        
        # Read access for authenticated users
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write access only for pharmacists and stock managers
        return (
            request.user.groups.filter(name__in=['Pharmacist', 'Stock Manager']).exists() or 
            request.user.is_staff
        )
