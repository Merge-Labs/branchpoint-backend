from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from .models import Vendor


@receiver(post_save, sender=Vendor)
def handle_vendor_save(sender, instance, created, **kwargs):
    """
    Handle vendor save operations
    """
    if created:
        # New vendor created
        pass
    else:
        # Vendor updated
        pass


@receiver(pre_delete, sender=Vendor)
def handle_vendor_delete(sender, instance, **kwargs):
    """
    Handle vendor deletion - ensure no associated data
    """
    # Check if vendor has associated data
    if instance.total_products > 0 or instance.total_purchases > 0:
        raise Exception("Cannot delete vendor with associated products or purchases") 