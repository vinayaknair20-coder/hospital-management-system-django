"""
PHARMACIST APP UTILITIES
Helper functions for pharmacy operations with comprehensive validation
"""

from django.utils import timezone
from django.db.models import Sum, Q, F
from django.db import transaction
from datetime import timedelta, date
from decimal import Decimal, InvalidOperation
import logging
from django.db import models

from .models import (
    Medicine, MedicineStock, StockAlert, Prescription, 
    PrescriptionItem, Sale, SaleItem
)

# Set up logging
logger = logging.getLogger(__name__)


def generate_stock_alerts():
    """
    Generate stock alerts for low stock, expiring medicines, etc.
    This function has comprehensive validation and error handling
    """
    try:
        with transaction.atomic():
            # Clear old resolved alerts (older than 30 days)
            old_alerts = StockAlert.objects.filter(
                is_resolved=True,
                resolved_at__lt=timezone.now() - timedelta(days=30)
            )
            deleted_count = old_alerts.count()
            old_alerts.delete()
            
            if deleted_count > 0:
                logger.info(f"Cleaned up {deleted_count} old resolved alerts")
            
            alerts_created = 0
            
            # Check each active medicine for stock issues
            active_medicines = Medicine.objects.filter(is_active=True)
            
            for medicine in active_medicines:
                # LOW STOCK ALERT
                if medicine.is_low_stock and medicine.total_quantity > 0:
                    alert, created = StockAlert.objects.get_or_create(
                        medicine=medicine,
                        alert_type='LOW_STOCK',
                        is_resolved=False,
                        defaults={
                            'message': f'{medicine.medicine_name} is running low. Current stock: {medicine.total_quantity}, Reorder level: {medicine.reorder_level}'
                        }
                    )
                    if created:
                        alerts_created += 1
                        logger.info(f"Low stock alert created for {medicine.medicine_name}")
                
                # OUT OF STOCK ALERT
                elif medicine.is_out_of_stock:
                    alert, created = StockAlert.objects.get_or_create(
                        medicine=medicine,
                        alert_type='OUT_OF_STOCK',
                        is_resolved=False,
                        defaults={
                            'message': f'{medicine.medicine_name} is completely out of stock!'
                        }
                    )
                    if created:
                        alerts_created += 1
                        logger.warning(f"Out of stock alert created for {medicine.medicine_name}")
            
            # Check individual stock batches for expiry issues
            today = timezone.now().date()
            thirty_days_later = today + timedelta(days=30)
            
            # EXPIRING SOON ALERTS
            expiring_batches = MedicineStock.objects.filter(
                quantity_available__gt=0,
                is_damaged=False,
                expiry_date__lte=thirty_days_later,
                expiry_date__gt=today
            )
            
            for batch in expiring_batches:
                alert, created = StockAlert.objects.get_or_create(
                    medicine=batch.medicine,
                    stock_batch=batch,
                    alert_type='EXPIRING_SOON',
                    is_resolved=False,
                    defaults={
                        'message': f'{batch.medicine.medicine_name} (Batch: {batch.batch_number}) expires on {batch.expiry_date} ({batch.days_to_expiry} days remaining). Quantity: {batch.quantity_available}'
                    }
                )
                if created:
                    alerts_created += 1
                    logger.info(f"Expiring soon alert created for {batch.medicine.medicine_name} batch {batch.batch_number}")
            
            # EXPIRED ALERTS
            expired_batches = MedicineStock.objects.filter(
                quantity_available__gt=0,
                is_damaged=False,
                expiry_date__lt=today
            )
            
            for batch in expired_batches:
                alert, created = StockAlert.objects.get_or_create(
                    medicine=batch.medicine,
                    stock_batch=batch,
                    alert_type='EXPIRED',
                    is_resolved=False,
                    defaults={
                        'message': f'{batch.medicine.medicine_name} (Batch: {batch.batch_number}) expired on {batch.expiry_date}. Quantity: {batch.quantity_available} - REMOVE FROM SALE!'
                    }
                )
                if created:
                    alerts_created += 1
                    logger.warning(f"Expired stock alert created for {batch.medicine.medicine_name} batch {batch.batch_number}")
            
            # DAMAGED STOCK ALERTS
            damaged_batches = MedicineStock.objects.filter(
                quantity_available__gt=0,
                is_damaged=True
            )
            
            for batch in damaged_batches:
                alert, created = StockAlert.objects.get_or_create(
                    medicine=batch.medicine,
                    stock_batch=batch,
                    alert_type='DAMAGED',
                    is_resolved=False,
                    defaults={
                        'message': f'{batch.medicine.medicine_name} (Batch: {batch.batch_number}) is marked as damaged. Quantity: {batch.quantity_available}. Reason: {batch.damage_notes}'
                    }
                )
                if created:
                    alerts_created += 1
                    logger.info(f"Damaged stock alert created for {batch.medicine.medicine_name} batch {batch.batch_number}")
            
            logger.info(f"Stock alert generation completed. Created {alerts_created} new alerts")
            return {'success': True, 'alerts_created': alerts_created}
            
    except Exception as e:
        logger.error(f"Error generating stock alerts: {str(e)}")
        return {'success': False, 'error': str(e)}


def process_medicine_dispensing(prescription, dispense_data, pharmacist):
    """
    Process medicine dispensing from prescription with comprehensive validation
    """
    try:
        with transaction.atomic():
            prescription_item_id = dispense_data['prescription_item_id']
            quantity_to_dispense = dispense_data['quantity_to_dispense']
            batch_number = dispense_data['batch_number']
            
            # Validate prescription item exists and belongs to prescription
            try:
                prescription_item = PrescriptionItem.objects.select_for_update().get(
                    id=prescription_item_id,
                    prescription=prescription
                )
            except PrescriptionItem.DoesNotExist:
                raise ValueError(f"Invalid prescription item ID: {prescription_item_id}")
            
            # Validate quantity to dispense
            remaining_quantity = prescription_item.remaining_quantity
            if quantity_to_dispense > remaining_quantity:
                raise ValueError(f"Cannot dispense {quantity_to_dispense}. Only {remaining_quantity} remaining to dispense.")
            
            if quantity_to_dispense <= 0:
                raise ValueError("Quantity to dispense must be greater than 0.")
            
            # Validate and get stock batch
            try:
                stock_batch = MedicineStock.objects.select_for_update().get(
                    medicine=prescription_item.medicine,
                    batch_number=batch_number,
                    quantity_available__gte=quantity_to_dispense,
                    is_damaged=False
                )
            except MedicineStock.DoesNotExist:
                raise ValueError(f"Insufficient stock for batch {batch_number} or batch not found.")
            
            # Validate stock is not expired
            if stock_batch.is_expired:
                raise ValueError(f"Cannot dispense expired medicine (Batch: {batch_number}, Expired: {stock_batch.expiry_date})")
            
            # Validate medicine is active
            if not prescription_item.medicine.is_active:
                raise ValueError(f"Cannot dispense inactive medicine: {prescription_item.medicine.medicine_name}")
            
            # Update stock quantity
            original_stock = stock_batch.quantity_available
            stock_batch.quantity_available -= quantity_to_dispense
            stock_batch.save()
            
            # Update prescription item
            prescription_item.quantity_dispensed += quantity_to_dispense
            prescription_item.save()
            
            # Update medicine total quantity
            stock_batch.update_medicine_total_quantity()
            
            # Create or update sale record
            sale, created = Sale.objects.get_or_create(
                prescription=prescription,
                defaults={
                    'customer_name': prescription.patient_name,
                    'customer_phone': prescription.patient_phone,
                    'pharmacist': pharmacist,
                    'subtotal': Decimal('0.00'),
                    'discount_amount': Decimal('0.00'),
                    'tax_amount': Decimal('0.00'),
                    'total_amount': Decimal('0.00'),
                    'payment_method': 'CASH',
                    'is_completed': False
                }
            )
            
            # Add sale item
            item_subtotal = quantity_to_dispense * prescription_item.unit_price
            
            sale_item = SaleItem.objects.create(
                sale=sale,
                medicine=prescription_item.medicine,
                stock_batch=stock_batch,
                quantity=quantity_to_dispense,
                unit_price=prescription_item.unit_price,
                subtotal=item_subtotal
            )
            
            # Update sale totals
            sale.subtotal = sale.items.aggregate(
                total=Sum('subtotal')
            )['total'] or Decimal('0.00')
            
            # Calculate tax (12% GST)
            taxable_amount = sale.subtotal - sale.discount_amount
            sale.tax_amount = (taxable_amount * Decimal('0.12')).quantize(Decimal('0.01'))
            
            # Calculate total
            sale.total_amount = sale.subtotal + sale.tax_amount - sale.discount_amount
            sale.save()
            
            # Update prescription status
            all_items_fully_dispensed = all(
                item.is_fully_dispensed for item in prescription.items.all()
            )
            
            if all_items_fully_dispensed:
                prescription.status = 'FULLY_DISPENSED'
            else:
                prescription.status = 'PARTIALLY_DISPENSED'
            
            # Update prescription total amount
            prescription.total_amount = sum(
                item.quantity_dispensed * item.unit_price 
                for item in prescription.items.all()
            )
            prescription.save()
            
            # Generate new stock alerts
            generate_stock_alerts()
            
            result = {
                'success': True,
                'message': 'Medicine dispensed successfully',
                'dispensed_quantity': quantity_to_dispense,
                'remaining_to_dispense': prescription_item.remaining_quantity,
                'batch_remaining_stock': stock_batch.quantity_available,
                'original_batch_stock': original_stock,
                'sale_code': sale.sale_code,
                'sale_item_subtotal': float(item_subtotal),
                'prescription_status': prescription.status,
                'prescription_total': float(prescription.total_amount)
            }
            
            logger.info(f"Successfully dispensed {quantity_to_dispense} units of {prescription_item.medicine.medicine_name} from prescription {prescription.prescription_code}")
            
            return result
            
    except Exception as e:
        logger.error(f"Error processing medicine dispensing: {str(e)}")
        raise ValueError(f"Failed to dispense medicine: {str(e)}")


def get_stock_summary():
    """
    Get comprehensive stock summary with validation
    """
    try:
        today = timezone.now().date()
        
        # Basic counts
        total_medicines = Medicine.objects.filter(is_active=True).count()
        total_categories = Medicine.objects.filter(is_active=True).values('category').distinct().count()
        total_suppliers = MedicineStock.objects.values('supplier').distinct().count()
        
        # Stock status counts
        low_stock_medicines = Medicine.objects.filter(
            is_active=True,
            total_quantity__lte=F('reorder_level'),
            total_quantity__gt=0
        ).count()
        
        out_of_stock_medicines = Medicine.objects.filter(
            is_active=True,
            total_quantity=0
        ).count()
        
        # Expiry analysis
        expired_batches = MedicineStock.objects.filter(
            expiry_date__lt=today,
            quantity_available__gt=0,
            is_damaged=False
        )
        
        expiring_soon_batches = MedicineStock.objects.filter(
            expiry_date__lte=today + timedelta(days=30),
            expiry_date__gt=today,
            quantity_available__gt=0,
            is_damaged=False
        )
        
        # Value calculations
        total_stock_value = MedicineStock.objects.filter(
            quantity_available__gt=0,
            is_damaged=False,
            expiry_date__gt=today
        ).aggregate(
            total_value=Sum(F('quantity_available') * F('unit_cost'))
        )['total_value'] or Decimal('0.00')
        
        expired_value = expired_batches.aggregate(
            expired_value=Sum(F('quantity_available') * F('unit_cost'))
        )['expired_value'] or Decimal('0.00')
        
        # Damaged stock
        damaged_batches = MedicineStock.objects.filter(
            is_damaged=True,
            quantity_available__gt=0
        )
        
        damaged_value = damaged_batches.aggregate(
            damaged_value=Sum(F('quantity_available') * F('unit_cost'))
        )['damaged_value'] or Decimal('0.00')
        
        # Alert counts
        active_alerts = StockAlert.objects.filter(is_resolved=False).count()
        critical_alerts = StockAlert.objects.filter(
            is_resolved=False,
            alert_type__in=['OUT_OF_STOCK', 'EXPIRED']
        ).count()
        
        summary = {
            'overview': {
                'total_medicines': total_medicines,
                'total_categories': total_categories,
                'total_suppliers': total_suppliers,
                'last_updated': timezone.now().isoformat()
            },
            'stock_status': {
                'normal_stock': total_medicines - low_stock_medicines - out_of_stock_medicines,
                'low_stock': low_stock_medicines,
                'out_of_stock': out_of_stock_medicines,
                'low_stock_percentage': (low_stock_medicines / total_medicines * 100) if total_medicines > 0 else 0
            },
            'expiry_analysis': {
                'expired_batches': expired_batches.count(),
                'expiring_soon_batches': expiring_soon_batches.count(),
                'expired_quantity': expired_batches.aggregate(qty=Sum('quantity_available'))['qty'] or 0,
                'expiring_soon_quantity': expiring_soon_batches.aggregate(qty=Sum('quantity_available'))['qty'] or 0
            },
            'value_analysis': {
                'total_stock_value': float(total_stock_value),
                'expired_value': float(expired_value),
                'damaged_value': float(damaged_value),
                'usable_value': float(total_stock_value - expired_value - damaged_value)
            },
            'damage_analysis': {
                'damaged_batches': damaged_batches.count(),
                'damaged_quantity': damaged_batches.aggregate(qty=Sum('quantity_available'))['qty'] or 0
            },
            'alerts': {
                'active_alerts': active_alerts,
                'critical_alerts': critical_alerts
            }
        }
        
        logger.info("Stock summary generated successfully")
        return summary
        
    except Exception as e:
        logger.error(f"Error generating stock summary: {str(e)}")
        return {
            'error': str(e),
            'success': False
        }


def validate_stock_operation(medicine_id, quantity, operation_type='add'):
    """
    Validate stock operations before executing
    """
    try:
        # Validate medicine exists and is active
        try:
            medicine = Medicine.objects.get(id=medicine_id, is_active=True)
        except Medicine.DoesNotExist:
            raise ValueError(f"Medicine with ID {medicine_id} not found or inactive.")
        
        # Validate quantity
        try:
            quantity = int(quantity)
            if quantity <= 0:
                raise ValueError("Quantity must be greater than 0.")
            if quantity > 999999:
                raise ValueError("Quantity cannot exceed 999,999.")
        except (ValueError, TypeError):
            raise ValueError("Invalid quantity format.")
        
        # Operation-specific validation
        if operation_type == 'subtract':
            if quantity > medicine.total_quantity:
                raise ValueError(f"Cannot subtract {quantity}. Only {medicine.total_quantity} available.")
        
        return {
            'success': True,
            'medicine': medicine,
            'validated_quantity': quantity
        }
        
    except Exception as e:
        logger.error(f"Stock operation validation failed: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }


def calculate_medicine_metrics(medicine_id, days=30):
    """
    Calculate various metrics for a specific medicine
    """
    try:
        medicine = Medicine.objects.get(id=medicine_id)
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=days)
        
        # Sales metrics
        sales_data = SaleItem.objects.filter(
            medicine=medicine,
            sale__sale_date__date__gte=start_date,
            sale__is_completed=True
        ).aggregate(
            total_quantity_sold=Sum('quantity'),
            total_sales_value=Sum('subtotal'),
            number_of_sales=Count('id')
        )
        
        # Prescription metrics
        prescription_data = PrescriptionItem.objects.filter(
            medicine=medicine,
            prescription__prescription_date__date__gte=start_date
        ).aggregate(
            total_prescribed=Sum('quantity_prescribed'),
            total_dispensed=Sum('quantity_dispensed'),
            number_of_prescriptions=Count('id')
        )
        
        # Stock metrics
        current_stock = medicine.total_quantity
        stock_batches = medicine.stock_batches.filter(
            quantity_available__gt=0,
            is_damaged=False
        ).count()
        
        # Calculate turnover rate
        avg_stock = current_stock  # Simplified - could be improved with historical data
        turnover_rate = (sales_data['total_quantity_sold'] or 0) / avg_stock if avg_stock > 0 else 0
        
        # Calculate days of stock remaining
        avg_daily_sales = (sales_data['total_quantity_sold'] or 0) / days
        days_remaining = current_stock / avg_daily_sales if avg_daily_sales > 0 else float('inf')
        
        metrics = {
            'medicine_name': medicine.medicine_name,
            'period_days': days,
            'current_stock': current_stock,
            'stock_batches': stock_batches,
            'sales': {
                'quantity_sold': sales_data['total_quantity_sold'] or 0,
                'sales_value': float(sales_data['total_sales_value'] or 0),
                'number_of_sales': sales_data['number_of_sales'] or 0,
                'average_sale_quantity': (sales_data['total_quantity_sold'] or 0) / (sales_data['number_of_sales'] or 1)
            },
            'prescriptions': {
                'total_prescribed': prescription_data['total_prescribed'] or 0,
                'total_dispensed': prescription_data['total_dispensed'] or 0,
                'dispensing_rate': (prescription_data['total_dispensed'] or 0) / (prescription_data['total_prescribed'] or 1) * 100,
                'number_of_prescriptions': prescription_data['number_of_prescriptions'] or 0
            },
            'performance': {
                'turnover_rate': round(turnover_rate, 2),
                'avg_daily_sales': round(avg_daily_sales, 2),
                'estimated_days_remaining': round(days_remaining, 1) if days_remaining != float('inf') else 'No sales data'
            }
        }
        
        return metrics
        
    except Exception as e:
        logger.error(f"Error calculating medicine metrics: {str(e)}")
        return {'error': str(e)}


# Utility functions for data validation
def validate_phone_format(phone):
    """Validate phone number format"""
    import re
    if not phone:
        return False
    cleaned = re.sub(r'\D', '', str(phone))
    return len(cleaned) == 10 and cleaned[0] != '0'


def validate_price_format(price):
    """Validate price format"""
    try:
        price_decimal = Decimal(str(price))
        return price_decimal > 0 and price_decimal <= Decimal('999999.99')
    except (ValueError, InvalidOperation):
        return False


def validate_date_range(start_date, end_date):
    """Validate date range"""
    if not start_date or not end_date:
        return False
    
    try:
        if isinstance(start_date, str):
            start_date = timezone.datetime.strptime(start_date, '%Y-%m-%d').date()
        if isinstance(end_date, str):
            end_date = timezone.datetime.strptime(end_date, '%Y-%m-%d').date()
        
        return start_date <= end_date and start_date <= timezone.now().date()
    except ValueError:
        return False


def format_currency(amount):
    """Format amount as currency"""
    try:
        return f"₹{Decimal(str(amount)):,.2f}"
    except (ValueError, InvalidOperation):
        return "₹0.00"


def get_medicine_search_results(query, limit=10):
    """Search medicines with comprehensive filtering"""
    if not query or len(query.strip()) < 2:
        return []
    
    query = query.strip()
    
    # Search by medicine code, name, generic name, company
    medicines = Medicine.objects.filter(
        Q(medicine_code__icontains=query) |
        Q(medicine_name__icontains=query) |
        Q(generic_name__icontains=query) |
        Q(company_name__icontains=query),
        is_active=True
    ).select_related('category')[:limit]
    
    return [
        {
            'id': medicine.id,
            'medicine_code': medicine.medicine_code,
            'medicine_name': medicine.medicine_name,
            'generic_name': medicine.generic_name,
            'company_name': medicine.company_name,
            'unit_price': float(medicine.unit_price),
            'total_quantity': medicine.total_quantity,
            'is_low_stock': medicine.is_low_stock,
            'category': medicine.category.name
        }
        for medicine in medicines
    ]
