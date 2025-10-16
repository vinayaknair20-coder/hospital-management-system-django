from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import LabTest, TestResult
from .serializers import LabTestSerializer, LabTestUpdateSerializer, TestResultSerializer


class LabTestViewSet(viewsets.ModelViewSet):
    queryset = LabTest.objects.all()
    serializer_class = LabTestSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active']
    search_fields = ['test_name']
    ordering = ['test_name']
    
    def get_serializer_class(self):
        if self.action in ['update', 'partial_update']:
            return LabTestUpdateSerializer
        return LabTestSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        active_only = self.request.query_params.get('active_only', None)
        if active_only == 'true':
            queryset = queryset.filter(is_active=True)
        return queryset
    
    @action(detail=True, methods=['post'])
    def disable(self, request, pk=None):
        """Disable a lab test"""
        test = self.get_object()
        test.is_active = False
        test.save()
        return Response({
            'message': f'Lab test {test.test_name} has been disabled'
        })
    
    @action(detail=True, methods=['post'])
    def enable(self, request, pk=None):
        """Enable a lab test"""
        test = self.get_object()
        test.is_active = True
        test.save()
        return Response({
            'message': f'Lab test {test.test_name} has been enabled'
        })


class TestResultViewSet(viewsets.ModelViewSet):
    queryset = TestResult.objects.all()
    serializer_class = TestResultSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'patient', 'test']
    search_fields = ['patient__Patient_name', 'test__test_name']
    ordering = ['-test_date']
    
    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """Mark test result as completed"""
        result = self.get_object()
        result.status = 'completed'
        result.save()
        return Response({
            'message': 'Test result marked as completed',
            'is_normal': result.is_normal
        })
