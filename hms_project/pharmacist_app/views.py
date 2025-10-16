from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Medicine, MedicineStock
from .serializers import MedicineSerializer, MedicineUpdateSerializer, MedicineStockSerializer


class MedicineViewSet(viewsets.ModelViewSet):
    queryset = Medicine.objects.all()
    serializer_class = MedicineSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active', 'company_name']
    search_fields = ['medicine_name', 'generic_name', 'company_name']
    ordering = ['medicine_name']
    
    def get_serializer_class(self):
        if self.action in ['update', 'partial_update']:
            return MedicineUpdateSerializer
        return MedicineSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        active_only = self.request.query_params.get('active_only', None)
        if active_only == 'true':
            queryset = queryset.filter(is_active=True)
        return queryset
    
    @action(detail=True, methods=['post'])
    def disable(self, request, pk=None):
        """Disable a medicine"""
        medicine = self.get_object()
        medicine.is_active = False
        medicine.save()
        return Response({
            'message': f'{medicine.medicine_name} has been disabled'
        })
    
    @action(detail=True, methods=['post'])
    def enable(self, request, pk=None):
        """Enable a medicine"""
        medicine = self.get_object()
        medicine.is_active = True
        medicine.save()
        return Response({
            'message': f'{medicine.medicine_name} has been enabled'
        })
    
    @action(detail=False, methods=['get'])
    def low_stock(self, request):
        """Get medicines with low stock"""
        medicines = Medicine.objects.filter(
            quantity_in_stock__lte=models.F('reorder_level'),
            is_active=True
        )
        serializer = self.get_serializer(medicines, many=True)
        return Response(serializer.data)


class MedicineStockViewSet(viewsets.ModelViewSet):
    queryset = MedicineStock.objects.all()
    serializer_class = MedicineStockSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['medicine']
    search_fields = ['batch_number', 'medicine__medicine_name']
    ordering = ['-received_date']
    
    @action(detail=False, methods=['get'])
    def expired(self, request):
        """Get expired medicine batches"""
        from datetime import date
        expired_batches = MedicineStock.objects.filter(expiry_date__lte=date.today())
        serializer = self.get_serializer(expired_batches, many=True)
        return Response(serializer.data)
