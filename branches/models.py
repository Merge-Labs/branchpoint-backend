from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db.models import Count, Sum
from django.utils import timezone


class Branch(models.Model):
    name = models.CharField(max_length=100, unique=True)
    location = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    manager = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="managed_branch",
        limit_choices_to={"role": "manager"}
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'Branches'

    def __str__(self):
        return self.name

    def clean(self):
        """Custom validation"""
        if self.manager and self.manager.role != 'manager':
            raise ValidationError('Manager must have role "manager"')
        
        if self.manager and self.manager.branch != self:
            raise ValidationError('Manager must be assigned to this branch')

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    @property
    def staff_count(self):
        """Get count of staff assigned to this branch"""
        return self.users.filter(role='staff').count()

    @property
    def total_products(self):
        """Get count of products in this branch"""
        try:
            return self.products.count()
        except:
            return 0

    @property
    def total_vendors(self):
        """Get count of vendors in this branch"""
        try:
            return self.vendors.count()
        except:
            return 0

    @property
    def total_sales(self):
        """Get count of sales in this branch"""
        try:
            return self.sales.count()
        except:
            return 0

    @property
    def total_revenue(self):
        """Get total revenue from sales in this branch"""
        try:
            return self.sales.aggregate(total=Sum('total_amount'))['total'] or 0
        except:
            return 0

    def get_stats(self):
        """Get comprehensive branch statistics"""
        return {
            'staff_count': self.staff_count,
            'total_products': self.total_products,
            'total_vendors': self.total_vendors,
            'total_sales': self.total_sales,
            'total_revenue': self.total_revenue,
        }

    def assign_manager(self, user):
        """Assign a manager to this branch"""
        if user.role != 'manager':
            raise ValidationError('User must have role "manager"')
        
        # Remove user from any other branch management
        if hasattr(user, 'managed_branch') and user.managed_branch:
            user.managed_branch.manager = None
            user.managed_branch.save()
        
        # Assign to this branch
        self.manager = user
        user.branch = self
        self.save()
        user.save()

    def remove_manager(self):
        """Remove manager from this branch"""
        if self.manager:
            manager = self.manager
            self.manager = None
            self.save()
            
            # Remove manager from branch assignment
            manager.branch = None
            manager.save()

    def get_staff_list(self):
        """Get list of staff assigned to this branch"""
        return self.users.filter(role='staff').select_related('profile')

    def is_accessible_by(self, user):
        """Check if user can access this branch"""
        if user.role == 'superadmin':
            return True
        elif user.role == 'manager':
            return user.managed_branch == self
        elif user.role == 'staff':
            return user.branch == self
        return False
