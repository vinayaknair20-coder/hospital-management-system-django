# pharmacist_app/views.py - COMPLETE FILE
"""
Pharmacist App Views
Medicine and Stock Management
"""

from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Sum, F
from datetime import date, timedelta

from .models import Medicine, MedicineCategory, MedicineBatch, StockMovement
from .serializers import (
    MedicineSerializer,
    MedicineUpdateSerializer,
    MedicineDetailSerializer,
    MedicineCategorySerializer,
    MedicineBatchSerializer,
    StockMovementSerializer
)


class MedicineCategoryViewSet(viewsets.ModelViewSet):
    """Medicine Category ViewSet"""
    queryset = MedicineCategory.objects.all()
    serializer_class = MedicineCategorySerializer    # 
    permission_classes = [IsAuthenticated]  # ✅ Added authentication  # COMMENTED FOR TESTING
    
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['category_name', 'description']
    ordering = ['category_name']


class MedicineViewSet(viewsets.ModelViewSet):
    """Medicine Management ViewSet"""
    queryset = Medicine.objects.select_related('category').prefetch_related('batches')
    serializer_class = MedicineSerializer    # 
    permission_classes = [IsAuthenticated]  # ✅ Added authentication  # COMMENTED FOR TESTING
    
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active', 'category']
    search_fields = ['medicine_name', 'generic_name', 'company_name']
    ordering = ['medicine_name']
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return MedicineDetailSerializer
        elif self.action in ['update', 'partial_update']:
            return MedicineUpdateSerializer
        return MedicineSerializer
    
    @action(detail=False, methods=['get'])
    def search(self, request):
        """Search medicine by code or name"""
        code = request.query_params.get('code', None)
        name = request.query_params.get('name', None)
        
        if not code and not name:
            return Response(
                {'error': 'Either code or name parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        queryset = Medicine.objects.all()
        
        if code:
            queryset = queryset.filter(medicine_id=code)
        if name:
            queryset = queryset.filter(
                Q(medicine_name__icontains=name) |
                Q(generic_name__icontains=name)
            )
        
        serializer = self.get_serializer(queryset, many=True)
        
        return Response({
            'count': queryset.count(),
            'results': serializer.data
        }, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'])
    def low_stock(self, request):
        """Get medicines with low stock"""
        medicines = Medicine.objects.filter(
            quantity_in_stock__lte=F('reorder_level'),
            is_active=True
        ).order_by('quantity_in_stock')
        
        serializer = self.get_serializer(medicines, many=True)
        
        return Response({
            'count': medicines.count(),
            'medicines': serializer.data
        }, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'])
    def disable(self, request, pk=None):
        """Disable a medicine"""
        medicine = self.get_object()
        medicine.is_active = False
        medicine.save()
        
        return Response({
            'message': f'Medicine {medicine.medicine_name} has been disabled'
        }, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'])
    def enable(self, request, pk=None):
        """Enable a medicine"""
        medicine = self.get_object()
        medicine.is_active = True
        medicine.save()
        
        return Response({
            'message': f'Medicine {medicine.medicine_name} has been enabled'
        }, status=status.HTTP_200_OK)


class MedicineBatchViewSet(viewsets.ModelViewSet):
    """Medicine Batch ViewSet"""
    queryset = MedicineBatch.objects.select_related('medicine')
    serializer_class = MedicineBatchSerializer    # 
    permission_classes = [IsAuthenticated]  # ✅ Added authentication  # COMMENTED FOR TESTING
    
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['medicine', 'is_active']
    ordering = ['-expiry_date']
    
    @action(detail=False, methods=['get'])
    def expiring_soon(self, request):
        """Get batches expiring in next 3 months"""
        today = date.today()
        three_months = today + timedelta(days=90)
        
        batches = MedicineBatch.objects.filter(
            expiry_date__lte=three_months,
            expiry_date__gte=today,
            is_active=True
        ).order_by('expiry_date')
        
        serializer = self.get_serializer(batches, many=True)
        
        return Response({
            'count': batches.count(),
            'batches': serializer.data
        }, status=status.HTTP_200_OK)


class StockMovementViewSet(viewsets.ModelViewSet):
    """Stock Movement ViewSet"""
    queryset = StockMovement.objects.select_related('medicine', 'performed_by')
    serializer_class = StockMovementSerializer    # 
    permission_classes = [IsAuthenticated]  # ✅ Added authentication  # COMMENTED FOR TESTING
    
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['medicine', 'movement_type', 'movement_date']
    ordering = ['-movement_date', '-movement_time']


# Add these imports at the top
from rest_framework.decorators import api_view, permission_classes

# Add these two functions at the BOTTOM of views.py

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_stats(request):
    """Get dashboard statistics for pharmacist"""
    # Count from your actual models
    total_medicines = Medicine.objects.filter(is_active=True).count()
    low_stock_items = Medicine.objects.filter(
        quantity_in_stock__lte=F('reorder_level'),
        is_active=True
    ).count()
    
    today = date.today()
    three_months = today + timedelta(days=90)
    expiring_medicines = MedicineBatch.objects.filter(
        expiry_date__lte=three_months,
        expiry_date__gte=today,
        is_active=True
    ).count()
    
    stats = {
        'totalMedicines': total_medicines,
        'pendingPrescriptions': 0,  # You'll add this when you create prescriptions model
        'lowStockItems': low_stock_items,
        'expiringMedicines': expiring_medicines
    }
    return Response(stats, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def prescription_list(request):
    """Get list of prescriptions (placeholder)"""
    # For now, return empty list - add prescription model later
    prescriptions = []
    return Response(prescriptions, status=status.HTTP_200_OK)
