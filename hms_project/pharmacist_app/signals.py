"""
PHARMACIST APP SIGNALS
Django signals for automatic processing and validation
"""

from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from django.utils import timezone
import logging

from .models import MedicineStock, Sale, SaleItem, Medicine, StockAlert
from .utils import generate_stock_alerts

# Set up logging
logger = logging.getLogger(__name__)


@receiver(post_save, sender=MedicineStock)
def update_medicine_stock_on_save(sender, instance, created, **kwargs):
    """Update medicine total quantity when stock is saved"""
    try:
        if instance.medicine:
            instance.update_medicine_total_quantity()
            
            if created:
                logger.info(f"New stock added: {instance.medicine.medicine_name} - Batch {instance.batch_number}")
                # Generate alerts for new stock
                generate_stock_alerts()
    except Exception as e:
        logger.error(f"Error updating medicine stock: {str(e)}")


@receiver(post_delete, sender=MedicineStock)
def update_medicine_stock_on_delete(sender, instance, **kwargs):
    """Update medicine total quantity when stock is deleted"""
    try:
        if instance.medicine:
            # Recalculate total quantity for the medicine
            total = instance.medicine.stock_batches.filter(
                quantity_available__gt=0,
                is_damaged=False,
                expiry_date__gt=timezone.now().date()
            ).aggregate(
                total=models.Sum('quantity_available')
            )['total'] or 0
            
            instance.medicine.total_quantity = total
            instance.medicine.save(update_fields=['total_quantity'])
            
            logger.info(f"Stock deleted: Updated {instance.medicine.medicine_name} total quantity to {total}")
    except Exception as e:
        logger.error(f"Error updating medicine stock on delete: {str(e)}")


@receiver(post_save, sender=Sale)
def process_sale_completion(sender, instance, created, **kwargs):
    """Process sale completion and generate alerts"""
    try:
        if instance.is_completed and not created:
            # Sale was just completed
            logger.info(f"Sale completed: {instance.sale_code} - Total: ₹{instance.total_amount}")
            
            # Generate stock alerts after sale completion
            generate_stock_alerts()
    except Exception as e:
        logger.error(f"Error processing sale completion: {str(e)}")


@receiver(post_save, sender=SaleItem)
def update_stock_on_sale(sender, instance, created, **kwargs):
    """Update stock when sale item is created"""
    try:
        if created and instance.stock_batch:
            # Stock quantity was already updated in the model's save method
            # Just log the transaction
            logger.info(f"Stock updated via sale: {instance.medicine.medicine_name} - "
                       f"Sold {instance.quantity} from batch {instance.stock_batch.batch_number}")
    except Exception as e:
        logger.error(f"Error updating stock on sale: {str(e)}")


@receiver(pre_save, sender=Medicine)
def log_medicine_changes(sender, instance, **kwargs):
    """Log important changes to medicine records"""
    try:
        if instance.pk:  # Updating existing medicine
            try:
                original = Medicine.objects.get(pk=instance.pk)
                
                # Log status changes
                if original.is_active != instance.is_active:
                    status = "activated" if instance.is_active else "deactivated"
                    logger.info(f"Medicine {status}: {instance.medicine_name}")
                
                # Log price changes
                if original.unit_price != instance.unit_price:
                    logger.info(f"Price changed for {instance.medicine_name}: "
                               f"₹{original.unit_price} → ₹{instance.unit_price}")
                
                # Log reorder level changes
                if original.reorder_level != instance.reorder_level:
                    logger.info(f"Reorder level changed for {instance.medicine_name}: "
                               f"{original.reorder_level} → {instance.reorder_level}")
                    
            except Medicine.DoesNotExist:
                pass  # New medicine
    except Exception as e:
        logger.error(f"Error logging medicine changes: {str(e)}")


@receiver(post_save, sender=StockAlert)
def log_alert_creation(sender, instance, created, **kwargs):
    """Log when new alerts are created"""
    try:
        if created:
            logger.warning(f"New {instance.alert_type} alert: {instance.message}")
            
            # For critical alerts, could send notifications here
            if instance.alert_type in ['OUT_OF_STOCK', 'EXPIRED']:
                logger.critical(f"CRITICAL ALERT: {instance.message}")
    except Exception as e:
        logger.error(f"Error logging alert creation: {str(e)}")


# Custom signal for low stock detection
from django.dispatch import Signal

low_stock_detected = Signal()
out_of_stock_detected = Signal()


@receiver(low_stock_detected)
def handle_low_stock(sender, medicine, **kwargs):
    """Handle low stock situations"""
    try:
        logger.warning(f"Low stock detected: {medicine.medicine_name} - "
                      f"Current: {medicine.total_quantity}, Reorder level: {medicine.reorder_level}")
        
        # Could trigger automatic reordering here
        # Could send email notifications here
    except Exception as e:
        logger.error(f"Error handling low stock: {str(e)}")


@receiver(out_of_stock_detected)
def handle_out_of_stock(sender, medicine, **kwargs):
    """Handle out of stock situations"""
    try:
        logger.critical(f"OUT OF STOCK: {medicine.medicine_name}")
        
        # Could disable the medicine temporarily
        # Could send urgent notifications here
    except Exception as e:
        logger.error(f"Error handling out of stock: {str(e)}")
