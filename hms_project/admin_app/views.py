from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Staff, Specialization
from .serializers import StaffSerializer, StaffUpdateSerializer, SpecializationSerializer


class StaffViewSet(viewsets.ModelViewSet):
    queryset = Staff.objects.all()
    serializer_class = StaffSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['role', 'is_active', 'specialization']
    search_fields = ['staff_name', 'Email', 'Phone_number']
    ordering_fields = ['staff_id', 'staff_name', 'joining_date']
    ordering = ['staff_name']
    
    def get_serializer_class(self):
        """Use different serializer for updates"""
        if self.action in ['update', 'partial_update']:
            return StaffUpdateSerializer
        return StaffSerializer
    
    def get_queryset(self):
        """Filter by active status"""
        queryset = super().get_queryset()
        active_only = self.request.query_params.get('active_only', None)
        if active_only == 'true':
            queryset = queryset.filter(is_active=True)
        return queryset
    
    @action(detail=True, methods=['post'])
    def disable(self, request, pk=None):
        """Disable a staff member (soft delete)"""
        staff = self.get_object()
        staff.is_active = False
        staff.save()
        return Response({
            'message': f'{staff.staff_name} has been disabled successfully'
        }, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'])
    def enable(self, request, pk=None):
        """Enable a staff member"""
        staff = self.get_object()
        staff.is_active = True
        staff.save()
        return Response({
            'message': f'{staff.staff_name} has been enabled successfully'
        }, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'])
    def doctors(self, request):
        """Get all active doctors"""
        doctors = Staff.objects.filter(role='DOCTOR', is_active=True)
        serializer = self.get_serializer(doctors, many=True)
        return Response(serializer.data)


class SpecializationViewSet(viewsets.ModelViewSet):
    queryset = Specialization.objects.all()
    serializer_class = SpecializationSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['specialization_name']
    ordering = ['specialization_name']
    
    def get_queryset(self):
        """Filter active specializations"""
        queryset = super().get_queryset()
        active_only = self.request.query_params.get('active_only', None)
        if active_only == 'true':
            queryset = queryset.filter(is_active=True)
        return queryset
    
    @action(detail=True, methods=['post'])
    def disable(self, request, pk=None):
        """Disable a specialization"""
        specialization = self.get_object()
        specialization.is_active = False
        specialization.save()
        return Response({
            'message': f'{specialization.specialization_name} has been disabled'
        }, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'])
    def enable(self, request, pk=None):
        """Enable a specialization"""
        specialization = self.get_object()
        specialization.is_active = True
        specialization.save()
        return Response({
            'message': f'{specialization.specialization_name} has been enabled'
        }, status=status.HTTP_200_OK)
