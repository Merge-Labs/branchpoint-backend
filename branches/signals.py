from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import Branch

User = get_user_model()


@receiver(post_save, sender=Branch)
def handle_branch_save(sender, instance, created, **kwargs):
    """
    Handle branch save operations
    """
    if created:
        # New branch created
        pass
    else:
        # Branch updated
        pass


@receiver(pre_delete, sender=Branch)
def handle_branch_delete(sender, instance, **kwargs):
    """
    Handle branch deletion - ensure no associated data
    """
    # Check if branch has associated data
    if instance.total_products > 0 or instance.total_vendors > 0 or instance.total_sales > 0:
        raise Exception("Cannot delete branch with associated products, vendors, or sales")
    
    # Remove manager assignment
    if instance.manager:
        instance.remove_manager()


@receiver(post_save, sender=User)
def handle_user_branch_assignment(sender, instance, **kwargs):
    """
    Handle user branch assignment changes
    """
    # If user is a manager and has a managed_branch, ensure they're assigned to that branch
    if instance.role == 'manager' and hasattr(instance, 'managed_branch') and instance.managed_branch:
        if instance.branch != instance.managed_branch:
            instance.branch = instance.managed_branch
            instance.save(update_fields=['branch'])
    
    # If user is staff and has a branch, ensure they're not managing any branch
    elif instance.role == 'staff' and instance.branch:
        if hasattr(instance, 'managed_branch') and instance.managed_branch:
            instance.managed_branch.manager = None
            instance.managed_branch.save() 