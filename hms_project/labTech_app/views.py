# labTech_app/views.py - COMPLETE FILE
"""
Lab Technician App Views
Lab Test and Result Management
"""

from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

from .models import LabTest, TestResult
from .serializers import (
    LabTestSerializer,
    LabTestUpdateSerializer,
    TestResultSerializer
)


class LabTestViewSet(viewsets.ModelViewSet):
    """Lab Test Management ViewSet"""
    queryset = LabTest.objects.all()
    serializer_class = LabTestSerializer    # 
    permission_classes = [IsAuthenticated]  # ✅ Added authentication  # COMMENTED FOR TESTING
    
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
            'message': f'Lab test {test.test_name} has been disabled',
            'test_id': test.test_id,
            'is_active': test.is_active
        }, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'])
    def enable(self, request, pk=None):
        """Enable a lab test"""
        test = self.get_object()
        test.is_active = True
        test.save()
        
        return Response({
            'message': f'Lab test {test.test_name} has been enabled',
            'test_id': test.test_id,
            'is_active': test.is_active
        }, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Get lab test statistics"""
        total_tests = LabTest.objects.count()
        active_tests = LabTest.objects.filter(is_active=True).count()
        
        return Response({
            'total_tests': total_tests,
            'active_tests': active_tests,
            'inactive_tests': total_tests - active_tests
        }, status=status.HTTP_200_OK)


class TestResultViewSet(viewsets.ModelViewSet):
    """Test Result Management ViewSet"""
    queryset = TestResult.objects.select_related(
        'consultation',
        'lab_test',
        'performed_by'
    )
    serializer_class = TestResultSerializer    # 
    permission_classes = [IsAuthenticated]  # ✅ Added authentication  # COMMENTED FOR TESTING
    
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['lab_test', 'result_status', 'test_date']
    ordering = ['-test_date']
    
    @action(detail=False, methods=['get'])
    def pending(self, request):
        """Get pending test results"""
        pending_results = TestResult.objects.filter(
            result_status='PENDING'
        ).order_by('test_date')
        
        serializer = self.get_serializer(pending_results, many=True)
        
        return Response({
            'count': pending_results.count(),
            'results': serializer.data
        }, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """Mark test result as completed"""
        test_result = self.get_object()
        test_result.result_status = 'COMPLETED'
        test_result.save()
        
        return Response({
            'message': 'Test result marked as completed',
            'result_id': test_result.result_id,
            'result_status': test_result.result_status
        }, status=status.HTTP_200_OK)
