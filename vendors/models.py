from django.db import models
from django.core.exceptions import ValidationError
from django.db.models import Count, Sum
from branches.models import Branch
from accounts.models import User

class Vendor(models.Model):
    """
    Vendor model scoped to a specific branch and added by a user.
    Only BranchManagers can create/edit vendors in their branch.
    """
    name = models.CharField(max_length=100)
    contact_person = models.CharField(max_length=100, blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    address = models.TextField(blank=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    vendor_type = models.CharField(
        max_length=50,
        choices=[
            ('supplier', 'Supplier'),
            ('service_provider', 'Service Provider'),
            ('contractor', 'Contractor'),
            ('other', 'Other')
        ],
        default='supplier'
    )
    payment_terms = models.CharField(max_length=100, blank=True)
    tax_id = models.CharField(max_length=50, blank=True)
    website = models.URLField(blank=True)

    branch = models.ForeignKey(
        Branch,
        on_delete=models.CASCADE,
        related_name='vendors'
    )
    added_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='vendors_added'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('name', 'branch')
        ordering = ['-created_at']
        verbose_name_plural = 'Vendors'

    def __str__(self):
        return f"{self.name} ({self.branch.name})"

    def clean(self):
        """Custom validation"""
        if self.email and not self.email.strip():
            self.email = ''
        
        # Ensure vendor name is unique within the branch
        if Vendor.objects.filter(name=self.name, branch=self.branch).exclude(id=self.id).exists():
            raise ValidationError('A vendor with this name already exists in this branch.')

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    @property
    def total_products(self):
        """Get count of products supplied by this vendor"""
        try:
            return self.products.count()
        except:
            return 0

    @property
    def total_purchases(self):
        """Get count of purchases from this vendor"""
        try:
            return self.purchases.count()
        except:
            return 0

    @property
    def total_spent(self):
        """Get total amount spent with this vendor"""
        try:
            return self.purchases.aggregate(total=Sum('total_amount'))['total'] or 0
        except:
            return 0

    @property
    def last_purchase_date(self):
        """Get the date of the last purchase from this vendor"""
        try:
            last_purchase = self.purchases.order_by('-purchase_date').first()
            return last_purchase.purchase_date if last_purchase else None
        except:
            return None

    def get_stats(self):
        """Get comprehensive vendor statistics"""
        return {
            'total_products': self.total_products,
            'total_purchases': self.total_purchases,
            'total_spent': self.total_spent,
            'last_purchase_date': self.last_purchase_date,
        }

    def is_accessible_by(self, user):
        """Check if user can access this vendor"""
        if user.role == 'superadmin':
            return True
        elif user.role == 'manager':
            return user.managed_branch == self.branch
        elif user.role == 'staff':
            return user.branch == self.branch
        return False

    def can_be_managed_by(self, user):
        """Check if user can manage this vendor (only BranchManagers)"""
        if user.role == 'manager':
            return user.managed_branch == self.branch
        return False
