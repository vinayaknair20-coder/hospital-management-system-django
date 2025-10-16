"""
PHARMACIST APP VIEWS
Django REST Framework viewsets with comprehensive validation and business logic
"""

from rest_framework import viewsets, status, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError, PermissionDenied
from django.db.models import Q, Sum, Count, F, Avg
from django.utils import timezone
from django.db import transaction
from datetime import timedelta
from decimal import Decimal
import logging

from .models import *
from .serializers import *
from .permissions import IsPharmacistOrReadOnly, IsPharmacist
from .utils import generate_stock_alerts, process_medicine_dispensing, get_stock_summary

# Set up logging
logger = logging.getLogger(__name__)


class MedicineCategoryViewSet(viewsets.ModelViewSet):
    """Medicine category management"""
    
    queryset = MedicineCategory.objects.all()
    serializer_class = MedicineCategorySerializer
    permission_classes = [IsPharmacistOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']
    
    def get_queryset(self):
        """Filter queryset with validation"""
        queryset = super().get_queryset()
        
        # Filter by active status
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            if is_active.lower() in ['true', '1']:
                queryset = queryset.filter(is_active=True)
            elif is_active.lower() in ['false', '0']:
                queryset = queryset.filter(is_active=False)
        
        return queryset
    
    def perform_create(self, serializer):
        """Create with logging"""
        logger.info(f"Creating category: {serializer.validated_data.get('name')} by {self.request.user.username}")
        serializer.save()
    
    def perform_destroy(self, instance):
        """Delete with validation"""
        if instance.medicine_set.exists():
            raise ValidationError("Cannot delete category that has medicines assigned to it.")
        
        logger.info(f"Deleting category: {instance.name} by {self.request.user.username}")
        super().perform_destroy(instance)
    
    @action(detail=True, methods=['post'])
    def toggle_active(self, request, pk=None):
        """Toggle category active status"""
        category = self.get_object()
        
        if category.is_active:
            # Check for active medicines before deactivating
            active_medicines = category.medicine_set.filter(is_active=True).count()
            if active_medicines > 0:
                return Response(
                    {'error': f'Cannot deactivate category with {active_medicines} active medicines'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        category.is_active = not category.is_active
        category.save()
        
        action_word = 'activated' if category.is_active else 'deactivated'
        return Response({'message': f'Category {action_word} successfully'})


class SupplierViewSet(viewsets.ModelViewSet):
    """Supplier management"""
    
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer
    permission_classes = [IsPharmacistOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'contact_person', 'email']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']
    
    def get_queryset(self):
        """Filter suppliers"""
        queryset = super().get_queryset()
        
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            if is_active.lower() in ['true', '1']:
                queryset = queryset.filter(is_active=True)
            elif is_active.lower() in ['false', '0']:
                queryset = queryset.filter(is_active=False)
        
        return queryset
    
    @action(detail=True, methods=['get'])
    def supplies(self, request, pk=None):
        """Get supplies from this supplier"""
        supplier = self.get_object()
        
        supplies = MedicineStock.objects.filter(supplier=supplier).select_related('medicine')
        
        # Paginate results
        page = self.paginate_queryset(supplies)
        if page is not None:
            serializer = MedicineStockSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = MedicineStockSerializer(supplies, many=True)
        return Response(serializer.data)


class MedicineViewSet(viewsets.ModelViewSet):
    """Medicine management - core functionality as per PDF requirements"""
    
    queryset = Medicine.objects.select_related('category').all()
    serializer_class = MedicineSerializer
    permission_classes = [IsPharmacistOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['medicine_code', 'medicine_name', 'generic_name', 'company_name']  # PDF: Search by Medicine Code & Name
    ordering_fields = ['medicine_name', 'company_name', 'unit_price', 'total_quantity', 'created_at']
    ordering = ['medicine_name']
    
    def get_queryset(self):
        """Advanced filtering with validation"""
        queryset = super().get_queryset()
        params = self.request.query_params
        
        # Filter by active status (PDF: Enable/Disable functionality)
        is_active = params.get('is_active')
        if is_active is not None:
            if is_active.lower() in ['true', '1']:
                queryset = queryset.filter(is_active=True)
            elif is_active.lower() in ['false', '0']:
                queryset = queryset.filter(is_active=False)
        
        # Filter by category
        category_id = params.get('category')
        if category_id:
            try:
                category_id = int(category_id)
                queryset = queryset.filter(category_id=category_id)
            except ValueError:
                raise ValidationError("Invalid category ID.")
        
        # Price range filtering
        min_price = params.get('min_price')
        max_price = params.get('max_price')
        
        if min_price:
            try:
                min_price = Decimal(min_price)
                if min_price < 0:
                    raise ValidationError("Minimum price cannot be negative.")
                queryset = queryset.filter(unit_price__gte=min_price)
            except (ValueError, InvalidOperation):
                raise ValidationError("Invalid minimum price format.")
        
        if max_price:
            try:
                max_price = Decimal(max_price)
                if max_price <= 0:
                    raise ValidationError("Maximum price must be positive.")
                if min_price and max_price < min_price:
                    raise ValidationError("Maximum price cannot be less than minimum price.")
                queryset = queryset.filter(unit_price__lte=max_price)
            except (ValueError, InvalidOperation):
                raise ValidationError("Invalid maximum price format.")
        
        # Low stock filtering
        low_stock = params.get('low_stock')
        if low_stock and low_stock.lower() in ['true', '1']:
            # Filter medicines where total_quantity <= reorder_level
            queryset = queryset.filter(total_quantity__lte=F('reorder_level'))
        
        return queryset
    
    def perform_create(self, serializer):
        """Create medicine with logging"""
        medicine_data = serializer.validated_data
        logger.info(f"Creating medicine: {medicine_data['medicine_name']} by {self.request.user.username}")
        serializer.save()
    
    def perform_update(self, serializer):
        """Update medicine - PDF: Only Quantity and Price can be edited"""
        instance = self.get_object()
        
        # Log what fields are being updated
        updated_fields = list(serializer.validated_data.keys())
        logger.info(f"Updating medicine {instance.medicine_name}: {updated_fields} by {self.request.user.username}")
        
        serializer.save()
    
    def perform_destroy(self, instance):
        """Delete/disable medicine"""
        # Instead of deleting, disable the medicine (as per PDF requirements)
        instance.is_active = False
        instance.save()
        logger.info(f"Disabled medicine: {instance.medicine_name} by {self.request.user.username}")
    
    @action(detail=False, methods=['get'])
    def low_stock(self, request):
        """Get medicines with low stock (below reorder level)"""
        threshold = request.query_params.get('threshold')
        
        if threshold:
            try:
                threshold = int(threshold)
                if threshold < 1 or threshold > 1000:
                    raise ValidationError("Threshold must be between 1 and 1000.")
            except ValueError:
                raise ValidationError("Invalid threshold format.")
        
        # Get medicines where total_quantity <= reorder_level (or custom threshold)
        if threshold:
            low_stock_medicines = Medicine.objects.filter(
                is_active=True,
                total_quantity__lte=threshold
            )
        else:
            low_stock_medicines = Medicine.objects.filter(
                is_active=True,
                total_quantity__lte=F('reorder_level')
            )
        
        serializer = self.get_serializer(low_stock_medicines, many=True)
        
        return Response({
            'count': low_stock_medicines.count(),
            'threshold': threshold or 'reorder_level',
            'medicines': serializer.data
        })
    
    @action(detail=False, methods=['get'])
    def out_of_stock(self, request):
        """Get medicines that are completely out of stock"""
        out_of_stock_medicines = Medicine.objects.filter(
            is_active=True,
            total_quantity=0
        )
        
        serializer = self.get_serializer(out_of_stock_medicines, many=True)
        
        return Response({
            'count': out_of_stock_medicines.count(),
            'medicines': serializer.data
        })
    
    @action(detail=False, methods=['get'])
    def expiring_soon(self, request):
        """Get medicines with batches expiring soon"""
        days = request.query_params.get('days', 30)
        try:
            days = int(days)
            if days < 1 or days > 365:
                raise ValidationError("Days must be between 1 and 365.")
        except ValueError:
            raise ValidationError("Invalid days format.")
        
        cutoff_date = timezone.now().date() + timedelta(days=days)
        
        # Get medicines with expiring batches
        medicines_with_expiring_stock = Medicine.objects.filter(
            is_active=True,
            stock_batches__expiry_date__lte=cutoff_date,
            stock_batches__expiry_date__gt=timezone.now().date(),
            stock_batches__quantity_available__gt=0
        ).distinct()
        
        serializer = self.get_serializer(medicines_with_expiring_stock, many=True)
        
        return Response({
            'count': medicines_with_expiring_stock.count(),
            'days': days,
            'cutoff_date': cutoff_date,
            'medicines': serializer.data
        })
    
    @action(detail=True, methods=['get'])
    def stock_batches(self, request, pk=None):
        """Get all stock batches for a medicine"""
        medicine = self.get_object()
        
        batches = medicine.stock_batches.all().order_by('expiry_date')
        
        # Filter by status
        status_filter = request.query_params.get('status')
        if status_filter == 'available':
            batches = batches.filter(
                quantity_available__gt=0,
                is_damaged=False,
                expiry_date__gt=timezone.now().date()
            )
        elif status_filter == 'expired':
            batches = batches.filter(expiry_date__lt=timezone.now().date())
        elif status_filter == 'damaged':
            batches = batches.filter(is_damaged=True)
        
        serializer = MedicineStockSerializer(batches, many=True)
        
        return Response({
            'medicine': medicine.medicine_name,
            'total_batches': batches.count(),
            'status_filter': status_filter,
            'batches': serializer.data
        })
    
    @action(detail=True, methods=['post'])
    def toggle_active(self, request, pk=None):
        """Enable/Disable medicine (as per PDF requirements)"""
        medicine = self.get_object()
        
        if medicine.is_active:
            # Check if there are pending prescriptions before disabling
            pending_prescriptions = PrescriptionItem.objects.filter(
                medicine=medicine,
                prescription__status='PENDING'
            ).count()
            
            if pending_prescriptions > 0:
                return Response(
                    {'error': f'Cannot disable medicine with {pending_prescriptions} pending prescriptions'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        medicine.is_active = not medicine.is_active
        medicine.save()
        
        action_word = 'enabled' if medicine.is_active else 'disabled'
        logger.info(f"Medicine {medicine.medicine_name} {action_word} by {request.user.username}")
        
        return Response({'message': f'Medicine {action_word} successfully'})


class MedicineStockViewSet(viewsets.ModelViewSet):
    """Medicine stock/inventory management"""
    
    queryset = MedicineStock.objects.select_related('medicine', 'supplier').all()
    serializer_class = MedicineStockSerializer
    permission_classes = [IsPharmacistOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['medicine__medicine_name', 'batch_number', 'supplier__name']
    ordering_fields = ['expiry_date', 'received_date', 'quantity_available']
    ordering = ['expiry_date']
    
    def get_queryset(self):
        """Filter stock with validation"""
        queryset = super().get_queryset()
        params = self.request.query_params
        
        # Filter by medicine
        medicine_id = params.get('medicine')
        if medicine_id:
            try:
                medicine_id = int(medicine_id)
                queryset = queryset.filter(medicine_id=medicine_id)
            except ValueError:
                raise ValidationError("Invalid medicine ID.")
        
        # Filter by supplier
        supplier_id = params.get('supplier')
        if supplier_id:
            try:
                supplier_id = int(supplier_id)
                queryset = queryset.filter(supplier_id=supplier_id)
            except ValueError:
                raise ValidationError("Invalid supplier ID.")
        
        # Filter by expiry status
        expiry_status = params.get('expiry_status')
        today = timezone.now().date()
        
        if expiry_status == 'expired':
            queryset = queryset.filter(expiry_date__lt=today)
        elif expiry_status == 'expiring_soon':
            days = int(params.get('days', 30))
            cutoff_date = today + timedelta(days=days)
            queryset = queryset.filter(
                expiry_date__lte=cutoff_date,
                expiry_date__gte=today
            )
        elif expiry_status == 'valid':
            queryset = queryset.filter(expiry_date__gt=today)
        
        # Filter by availability
        availability = params.get('availability')
        if availability == 'available':
            queryset = queryset.filter(quantity_available__gt=0)
        elif availability == 'out_of_stock':
            queryset = queryset.filter(quantity_available=0)
        
        # Filter by damage status
        is_damaged = params.get('is_damaged')
        if is_damaged is not None:
            if is_damaged.lower() in ['true', '1']:
                queryset = queryset.filter(is_damaged=True)
            elif is_damaged.lower() in ['false', '0']:
                queryset = queryset.filter(is_damaged=False)
        
        return queryset
    
    def perform_create(self, serializer):
        """Create stock with automatic alert generation"""
        stock_data = serializer.validated_data
        logger.info(f"Adding stock: {stock_data['medicine'].medicine_name} batch {stock_data['batch_number']} by {self.request.user.username}")
        
        with transaction.atomic():
            serializer.save()
            # Generate stock alerts after adding new stock
            generate_stock_alerts()
    
    @action(detail=False, methods=['get'])
    def expired(self, request):
        """Get all expired stock"""
        expired_stock = MedicineStock.objects.filter(
            expiry_date__lt=timezone.now().date(),
            quantity_available__gt=0
        ).select_related('medicine', 'supplier')
        
        serializer = self.get_serializer(expired_stock, many=True)
        
        return Response({
            'count': expired_stock.count(),
            'total_expired_quantity': expired_stock.aggregate(
                total=Sum('quantity_available')
            )['total'] or 0,
            'expired_stock': serializer.data
        })
    
    @action(detail=False, methods=['get'])
    def expiring_soon(self, request):
        """Get stock expiring within specified days"""
        days = int(request.query_params.get('days', 30))
        if days < 1 or days > 365:
            raise ValidationError("Days must be between 1 and 365.")
        
        cutoff_date = timezone.now().date() + timedelta(days=days)
        
        expiring_stock = MedicineStock.objects.filter(
            expiry_date__lte=cutoff_date,
            expiry_date__gt=timezone.now().date(),
            quantity_available__gt=0
        ).select_related('medicine', 'supplier')
        
        serializer = self.get_serializer(expiring_stock, many=True)
        
        return Response({
            'count': expiring_stock.count(),
            'days': days,
            'cutoff_date': cutoff_date,
            'total_expiring_quantity': expiring_stock.aggregate(
                total=Sum('quantity_available')
            )['total'] or 0,
            'expiring_stock': serializer.data
        })
    
    @action(detail=True, methods=['post'])
    def mark_damaged(self, request, pk=None):
        """Mark stock batch as damaged"""
        stock = self.get_object()
        damage_reason = request.data.get('damage_reason', '').strip()
        
        if not damage_reason:
            raise ValidationError("Damage reason is required.")
        
        stock.is_damaged = True
        stock.damage_notes = damage_reason
        stock.save()
        
        # Update medicine total quantity
        stock.update_medicine_total_quantity()
        
        logger.info(f"Stock batch {stock.batch_number} marked as damaged by {request.user.username}")
        
        return Response({'message': 'Stock marked as damaged successfully'})



# CONTINUING FROM PREVIOUS views.py...

class StockAlertViewSet(viewsets.ReadOnlyModelViewSet):
    """Stock alerts management"""
    
    queryset = StockAlert.objects.select_related('medicine', 'stock_batch').filter(is_resolved=False)
    serializer_class = StockAlertSerializer
    permission_classes = [IsPharmacist]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['created_at', 'alert_type']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Filter alerts with validation"""
        queryset = super().get_queryset()
        params = self.request.query_params
        
        # Filter by alert type
        alert_type = params.get('alert_type')
        if alert_type:
            valid_types = ['LOW_STOCK', 'OUT_OF_STOCK', 'EXPIRING_SOON', 'EXPIRED', 'DAMAGED']
            if alert_type.upper() in valid_types:
                queryset = queryset.filter(alert_type=alert_type.upper())
            else:
                raise ValidationError(f"Invalid alert type. Valid types: {', '.join(valid_types)}")
        
        # Filter by resolved status
        is_resolved = params.get('is_resolved')
        if is_resolved is not None:
            if is_resolved.lower() in ['true', '1']:
                queryset = StockAlert.objects.filter(is_resolved=True)
            elif is_resolved.lower() in ['false', '0']:
                queryset = queryset.filter(is_resolved=False)
        
        return queryset.order_by('-created_at')
    
    @action(detail=True, methods=['post'])
    def resolve(self, request, pk=None):
        """Mark alert as resolved"""
        alert = self.get_object()
        
        alert.is_resolved = True
        alert.resolved_at = timezone.now()
        alert.resolved_by = request.user
        alert.save()
        
        logger.info(f"Alert {alert.id} resolved by {request.user.username}")
        
        return Response({'message': 'Alert resolved successfully'})
    
    @action(detail=False, methods=['get'])
    def critical(self, request):
        """Get critical alerts (OUT_OF_STOCK and EXPIRED)"""
        critical_alerts = self.get_queryset().filter(
            alert_type__in=['OUT_OF_STOCK', 'EXPIRED']
        )
        
        serializer = self.get_serializer(critical_alerts, many=True)
        
        return Response({
            'count': critical_alerts.count(),
            'critical_alerts': serializer.data
        })
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get alert summary by type"""
        queryset = self.get_queryset()
        
        summary = queryset.values('alert_type').annotate(
            count=Count('id')
        ).order_by('alert_type')
        
        total_alerts = queryset.count()
        
        return Response({
            'total_alerts': total_alerts,
            'alert_breakdown': list(summary)
        })


class PrescriptionViewSet(viewsets.ModelViewSet):
    """Prescription management"""
    
    queryset = Prescription.objects.prefetch_related('items__medicine').all()
    serializer_class = PrescriptionSerializer
    permission_classes = [IsPharmacist]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['prescription_code', 'patient_name', 'doctor_name', 'patient_phone']
    ordering_fields = ['prescription_date', 'total_amount', 'patient_name']
    ordering = ['-prescription_date']
    
    def get_queryset(self):
        """Filter prescriptions with validation"""
        queryset = super().get_queryset()
        params = self.request.query_params
        
        # Filter by status
        status_filter = params.get('status')
        if status_filter:
            valid_statuses = ['PENDING', 'PARTIALLY_DISPENSED', 'FULLY_DISPENSED', 'CANCELLED']
            if status_filter.upper() in valid_statuses:
                queryset = queryset.filter(status=status_filter.upper())
            else:
                raise ValidationError(f"Invalid status. Valid statuses: {', '.join(valid_statuses)}")
        
        # Filter by date range
        start_date = params.get('start_date')
        end_date = params.get('end_date')
        
        if start_date:
            try:
                start_date = timezone.datetime.strptime(start_date, '%Y-%m-%d').date()
                queryset = queryset.filter(prescription_date__date__gte=start_date)
            except ValueError:
                raise ValidationError("Invalid start_date format. Use YYYY-MM-DD.")
        
        if end_date:
            try:
                end_date = timezone.datetime.strptime(end_date, '%Y-%m-%d').date()
                queryset = queryset.filter(prescription_date__date__lte=end_date)
            except ValueError:
                raise ValidationError("Invalid end_date format. Use YYYY-MM-DD.")
        
        # Filter by patient age range
        min_age = params.get('min_age')
        max_age = params.get('max_age')
        
        if min_age:
            try:
                min_age = int(min_age)
                if min_age < 0:
                    raise ValidationError("Minimum age cannot be negative.")
                queryset = queryset.filter(patient_age__gte=min_age)
            except ValueError:
                raise ValidationError("Invalid minimum age format.")
        
        if max_age:
            try:
                max_age = int(max_age)
                if max_age > 150:
                    raise ValidationError("Maximum age cannot exceed 150.")
                queryset = queryset.filter(patient_age__lte=max_age)
            except ValueError:
                raise ValidationError("Invalid maximum age format.")
        
        return queryset
    
    def perform_create(self, serializer):
        """Create prescription with validation"""
        prescription_data = serializer.validated_data
        logger.info(f"Creating prescription for {prescription_data['patient_name']} by {self.request.user.username}")
        serializer.save()
    
    @action(detail=False, methods=['get'])
    def pending(self, request):
        """Get all pending prescriptions"""
        pending_prescriptions = self.get_queryset().filter(status='PENDING')
        
        serializer = self.get_serializer(pending_prescriptions, many=True)
        
        return Response({
            'count': pending_prescriptions.count(),
            'prescriptions': serializer.data
        })
    
    @action(detail=True, methods=['post'])
    def dispense_medicine(self, request, pk=None):
        """Dispense medicine from prescription"""
        prescription = self.get_object()
        
        if prescription.status == 'FULLY_DISPENSED':
            return Response(
                {'error': 'Prescription is already fully dispensed'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if prescription.status == 'CANCELLED':
            return Response(
                {'error': 'Cannot dispense from cancelled prescription'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = DispenseMedicineSerializer(data=request.data)
        
        if serializer.is_valid():
            try:
                with transaction.atomic():
                    result = process_medicine_dispensing(
                        prescription,
                        serializer.validated_data,
                        request.user
                    )
                    
                    # Generate stock alerts after dispensing
                    generate_stock_alerts()
                    
                    logger.info(f"Medicine dispensed from prescription {prescription.prescription_code} by {request.user.username}")
                    
                    return Response(result, status=status.HTTP_200_OK)
                    
            except Exception as e:
                logger.error(f"Error dispensing medicine: {str(e)}")
                return Response(
                    {'error': str(e)}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel prescription"""
        prescription = self.get_object()
        
        if prescription.status == 'FULLY_DISPENSED':
            return Response(
                {'error': 'Cannot cancel fully dispensed prescription'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        reason = request.data.get('reason', '').strip()
        if not reason:
            raise ValidationError("Cancellation reason is required.")
        
        prescription.status = 'CANCELLED'
        prescription.save()
        
        logger.info(f"Prescription {prescription.prescription_code} cancelled by {request.user.username}: {reason}")
        
        return Response({'message': 'Prescription cancelled successfully'})
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Get prescription statistics"""
        queryset = self.get_queryset()
        
        today = timezone.now().date()
        
        stats = {
            'total_prescriptions': queryset.count(),
            'today_prescriptions': queryset.filter(prescription_date__date=today).count(),
            'pending_prescriptions': queryset.filter(status='PENDING').count(),
            'fully_dispensed': queryset.filter(status='FULLY_DISPENSED').count(),
            'partially_dispensed': queryset.filter(status='PARTIALLY_DISPENSED').count(),
            'cancelled': queryset.filter(status='CANCELLED').count(),
            'total_amount': queryset.aggregate(total=Sum('total_amount'))['total'] or 0,
            'average_patient_age': queryset.aggregate(avg=Avg('patient_age'))['avg'] or 0,
        }
        
        return Response(stats)


class SaleViewSet(viewsets.ModelViewSet):
    """Sales management"""
    
    queryset = Sale.objects.select_related('pharmacist', 'prescription').prefetch_related('items__medicine').all()
    serializer_class = SaleSerializer
    permission_classes = [IsPharmacist]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['sale_code', 'customer_name', 'customer_phone']
    ordering_fields = ['sale_date', 'total_amount', 'customer_name']
    ordering = ['-sale_date']
    
    def get_queryset(self):
        """Filter sales with validation"""
        queryset = super().get_queryset()
        params = self.request.query_params
        
        # Filter by completion status
        is_completed = params.get('is_completed')
        if is_completed is not None:
            if is_completed.lower() in ['true', '1']:
                queryset = queryset.filter(is_completed=True)
            elif is_completed.lower() in ['false', '0']:
                queryset = queryset.filter(is_completed=False)
        
        # Filter by payment method
        payment_method = params.get('payment_method')
        if payment_method:
            valid_methods = ['CASH', 'CARD', 'UPI', 'INSURANCE']
            if payment_method.upper() in valid_methods:
                queryset = queryset.filter(payment_method=payment_method.upper())
            else:
                raise ValidationError(f"Invalid payment method. Valid methods: {', '.join(valid_methods)}")
        
        # Filter by pharmacist
        pharmacist_id = params.get('pharmacist')
        if pharmacist_id:
            try:
                pharmacist_id = int(pharmacist_id)
                queryset = queryset.filter(pharmacist_id=pharmacist_id)
            except ValueError:
                raise ValidationError("Invalid pharmacist ID.")
        
        # Filter by date range
        start_date = params.get('start_date')
        end_date = params.get('end_date')
        
        if start_date:
            try:
                start_date = timezone.datetime.strptime(start_date, '%Y-%m-%d').date()
                queryset = queryset.filter(sale_date__date__gte=start_date)
            except ValueError:
                raise ValidationError("Invalid start_date format. Use YYYY-MM-DD.")
        
        if end_date:
            try:
                end_date = timezone.datetime.strptime(end_date, '%Y-%m-%d').date()
                queryset = queryset.filter(sale_date__date__lte=end_date)
            except ValueError:
                raise ValidationError("Invalid end_date format. Use YYYY-MM-DD.")
        
        # Filter by amount range
        min_amount = params.get('min_amount')
        max_amount = params.get('max_amount')
        
        if min_amount:
            try:
                min_amount = Decimal(min_amount)
                queryset = queryset.filter(total_amount__gte=min_amount)
            except (ValueError, InvalidOperation):
                raise ValidationError("Invalid minimum amount format.")
        
        if max_amount:
            try:
                max_amount = Decimal(max_amount)
                queryset = queryset.filter(total_amount__lte=max_amount)
            except (ValueError, InvalidOperation):
                raise ValidationError("Invalid maximum amount format.")
        
        return queryset
    
    def perform_create(self, serializer):
        """Create sale with pharmacist assignment"""
        validated_data = serializer.validated_data
        validated_data['pharmacist'] = self.request.user
        
        logger.info(f"Creating sale for {validated_data['customer_name']} by {self.request.user.username}")
        serializer.save(pharmacist=self.request.user)
    
    @action(detail=False, methods=['get'])
    def daily_sales(self, request):
        """Get today's sales report"""
        date_str = request.query_params.get('date')
        
        if date_str:
            try:
                target_date = timezone.datetime.strptime(date_str, '%Y-%m-%d').date()
            except ValueError:
                raise ValidationError("Invalid date format. Use YYYY-MM-DD.")
        else:
            target_date = timezone.now().date()
        
        daily_sales = self.get_queryset().filter(sale_date__date=target_date)
        
        serializer = self.get_serializer(daily_sales, many=True)
        
        total_amount = daily_sales.aggregate(total=Sum('total_amount'))['total'] or 0
        completed_sales = daily_sales.filter(is_completed=True)
        completed_amount = completed_sales.aggregate(total=Sum('total_amount'))['total'] or 0
        
        return Response({
            'date': target_date,
            'total_sales': daily_sales.count(),
            'completed_sales': completed_sales.count(),
            'pending_sales': daily_sales.filter(is_completed=False).count(),
            'total_amount': total_amount,
            'completed_amount': completed_amount,
            'average_sale_amount': total_amount / daily_sales.count() if daily_sales.count() > 0 else 0,
            'sales': serializer.data
        })
    
    @action(detail=False, methods=['get'])
    def monthly_report(self, request):
        """Get monthly sales report"""
        year = request.query_params.get('year')
        month = request.query_params.get('month')
        
        if year and month:
            try:
                year = int(year)
                month = int(month)
                if month < 1 or month > 12:
                    raise ValidationError("Month must be between 1 and 12.")
                
                start_date = timezone.datetime(year, month, 1).date()
                if month == 12:
                    end_date = timezone.datetime(year + 1, 1, 1).date()
                else:
                    end_date = timezone.datetime(year, month + 1, 1).date()
            except ValueError:
                raise ValidationError("Invalid year or month format.")
        else:
            # Current month
            now = timezone.now()
            start_date = now.replace(day=1).date()
            next_month = start_date.replace(month=start_date.month + 1) if start_date.month < 12 else start_date.replace(year=start_date.year + 1, month=1)
            end_date = next_month
        
        monthly_sales = self.get_queryset().filter(
            sale_date__date__gte=start_date,
            sale_date__date__lt=end_date
        )
        
        # Group by payment method
        payment_breakdown = monthly_sales.values('payment_method').annotate(
            count=Count('id'),
            total_amount=Sum('total_amount')
        ).order_by('payment_method')
        
        # Group by day
        daily_breakdown = monthly_sales.extra(
            select={'day': 'DATE(sale_date)'}
        ).values('day').annotate(
            count=Count('id'),
            total_amount=Sum('total_amount')
        ).order_by('day')
        
        stats = {
            'period': f"{start_date} to {end_date}",
            'total_sales': monthly_sales.count(),
            'completed_sales': monthly_sales.filter(is_completed=True).count(),
            'total_amount': monthly_sales.aggregate(total=Sum('total_amount'))['total'] or 0,
            'average_daily_sales': monthly_sales.count() / ((end_date - start_date).days or 1),
            'payment_method_breakdown': list(payment_breakdown),
            'daily_breakdown': list(daily_breakdown),
            'top_customers': monthly_sales.values('customer_name').annotate(
                total_purchases=Count('id'),
                total_spent=Sum('total_amount')
            ).order_by('-total_spent')[:10]
        }
        
        return Response(stats)
    
    @action(detail=True, methods=['post'])
    def complete_sale(self, request, pk=None):
        """Complete a sale transaction"""
        sale = self.get_object()
        
        if sale.is_completed:
            return Response(
                {'error': 'Sale is already completed'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate payment information
        amount_paid = request.data.get('amount_paid')
        if not amount_paid:
            raise ValidationError("Amount paid is required.")
        
        try:
            amount_paid = Decimal(str(amount_paid))
            if amount_paid < sale.total_amount:
                raise ValidationError("Amount paid must be at least equal to total amount.")
        except (ValueError, InvalidOperation):
            raise ValidationError("Invalid amount paid format.")
        
        # Calculate change
        change_amount = amount_paid - sale.total_amount
        
        # Update sale
        sale.is_completed = True
        sale.save()
        
        logger.info(f"Sale {sale.sale_code} completed by {request.user.username}")
        
        return Response({
            'message': 'Sale completed successfully',
            'amount_paid': amount_paid,
            'change_amount': change_amount,
            'total_amount': sale.total_amount
        })


# Dashboard and reporting views
class DashboardViewSet(viewsets.ViewSet):
    """Pharmacy dashboard with key metrics"""
    
    permission_classes = [IsPharmacist]
    
    @action(detail=False, methods=['get'])
    def overview(self, request):
        """Get dashboard overview"""
        today = timezone.now().date()
        
        # Medicine statistics
        total_medicines = Medicine.objects.filter(is_active=True).count()
        low_stock_medicines = Medicine.objects.filter(
            is_active=True,
            total_quantity__lte=F('reorder_level')
        ).count()
        out_of_stock_medicines = Medicine.objects.filter(
            is_active=True,
            total_quantity=0
        ).count()
        
        # Stock statistics
        expired_batches = MedicineStock.objects.filter(
            expiry_date__lt=today,
            quantity_available__gt=0
        ).count()
        expiring_soon = MedicineStock.objects.filter(
            expiry_date__lte=today + timedelta(days=30),
            expiry_date__gt=today,
            quantity_available__gt=0
        ).count()
        
        # Sales statistics
        today_sales = Sale.objects.filter(sale_date__date=today)
        today_sales_count = today_sales.count()
        today_sales_amount = today_sales.aggregate(total=Sum('total_amount'))['total'] or 0
        
        # Prescription statistics
        pending_prescriptions = Prescription.objects.filter(status='PENDING').count()
        
        # Alert statistics
        active_alerts = StockAlert.objects.filter(is_resolved=False).count()
        critical_alerts = StockAlert.objects.filter(
            is_resolved=False,
            alert_type__in=['OUT_OF_STOCK', 'EXPIRED']
        ).count()
        
        return Response({
            'medicines': {
                'total': total_medicines,
                'low_stock': low_stock_medicines,
                'out_of_stock': out_of_stock_medicines,
                'low_stock_percentage': (low_stock_medicines / total_medicines * 100) if total_medicines > 0 else 0
            },
            'inventory': {
                'expired_batches': expired_batches,
                'expiring_soon': expiring_soon,
                'total_stock_value': get_stock_summary().get('total_value', 0)
            },
            'sales': {
                'today_count': today_sales_count,
                'today_amount': today_sales_amount,
                'completed_today': today_sales.filter(is_completed=True).count()
            },
            'prescriptions': {
                'pending': pending_prescriptions
            },
            'alerts': {
                'active': active_alerts,
                'critical': critical_alerts
            }
        })
    
    @action(detail=False, methods=['get'])
    def recent_activities(self, request):
        """Get recent pharmacy activities"""
        limit = int(request.query_params.get('limit', 10))
        if limit < 1 or limit > 50:
            raise ValidationError("Limit must be between 1 and 50.")
        
        # Recent sales
        recent_sales = Sale.objects.select_related('pharmacist').order_by('-sale_date')[:limit]
        
        # Recent prescriptions
        recent_prescriptions = Prescription.objects.order_by('-prescription_date')[:limit]
        
        # Recent stock additions
        recent_stock = MedicineStock.objects.select_related('medicine', 'supplier').order_by('-received_date')[:limit]
        
        # Recent alerts
        recent_alerts = StockAlert.objects.select_related('medicine').order_by('-created_at')[:limit]
        
        return Response({
            'recent_sales': SaleSerializer(recent_sales, many=True).data,
            'recent_prescriptions': PrescriptionSerializer(recent_prescriptions, many=True).data,
            'recent_stock': MedicineStockSerializer(recent_stock, many=True).data,
            'recent_alerts': StockAlertSerializer(recent_alerts, many=True).data
        })

