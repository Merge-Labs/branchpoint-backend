from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator

User = get_user_model()

class SalesAccount(models.Model):
    STATUS_CHOICES = [
        ('prospect', 'Prospect'),
        ('active', 'Active'),
        ('negotiation', 'Negotiation'),
        ('closed', 'Closed'),
    ]

    # Company Information
    name = models.CharField(max_length=150, help_text="Company name")
    contact_person = models.CharField(max_length=100, help_text="Primary contact person")
    email = models.EmailField(help_text="Primary contact email")
    phone = models.CharField(max_length=20, blank=True, null=True, help_text="Contact phone number")
    location = models.CharField(max_length=200, blank=True, null=True, help_text="Company location/address")
    
    # Account Details
    account_value = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        default=0.00,
        validators=[MinValueValidator(0.00)],
        help_text="Total account value in currency"
    )
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='prospect',
        help_text="Current account status"
    )
    
    # Tracking
    deals_count = models.PositiveIntegerField(default=0, help_text="Number of active deals")
    last_contact_date = models.DateField(auto_now_add=True, help_text="Date of last contact")
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='created_sales_accounts'
    )
    assigned_to = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='assigned_sales_accounts'
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Sales Account"
        verbose_name_plural = "Sales Accounts"

    def __str__(self):
        return f"{self.name} - {self.contact_person}"

    @property
    def avatar(self):
        """Generate avatar initials from company name"""
        words = self.name.split()
        if len(words) >= 2:
            return f"{words[0][0]}{words[1][0]}".upper()
        return self.name[:2].upper()

    def update_last_contact(self):
        """Update the last contact date to today"""
        from django.utils import timezone
        self.last_contact_date = timezone.now().date()
        self.save(update_fields=['last_contact_date'])


class Deal(models.Model):
    DEAL_STAGE_CHOICES = [
        ('prospecting', 'Prospecting'),
        ('qualification', 'Qualification'),
        ('proposal', 'Proposal'),
        ('negotiation', 'Negotiation'),
        ('closed_won', 'Closed Won'),
        ('closed_lost', 'Closed Lost'),
    ]

    account = models.ForeignKey(
        SalesAccount, 
        on_delete=models.CASCADE, 
        related_name='deals'
    )
    title = models.CharField(max_length=200, help_text="Deal title/description")
    value = models.DecimalField(
        max_digits=12, 
        decimal_places=2,
        validators=[MinValueValidator(0.00)],
        help_text="Deal value"
    )
    stage = models.CharField(
        max_length=20, 
        choices=DEAL_STAGE_CHOICES, 
        default='prospecting'
    )
    expected_close_date = models.DateField(null=True, blank=True)
    probability = models.PositiveIntegerField(
        default=0, 
        validators=[MinValueValidator(0), MinValueValidator(100)],
        help_text="Probability percentage (0-100)"
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='created_deals'
    )

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.account.name}"

    def save(self, *args, **kwargs):
        # Update account deals count when deal is saved
        super().save(*args, **kwargs)
        self.update_account_deals_count()

    def update_account_deals_count(self):
        """Update the deals count on the associated account"""
        active_deals = self.account.deals.filter(
            stage__in=['prospecting', 'qualification', 'proposal', 'negotiation']
        ).count()
        self.account.deals_count = active_deals
        self.account.save(update_fields=['deals_count'])


class ContactActivity(models.Model):
    ACTIVITY_TYPES = [
        ('call', 'Phone Call'),
        ('email', 'Email'),
        ('meeting', 'Meeting'),
        ('note', 'Note'),
        ('proposal', 'Proposal Sent'),
    ]

    account = models.ForeignKey(
        SalesAccount, 
        on_delete=models.CASCADE, 
        related_name='activities'
    )
    activity_type = models.CharField(max_length=20, choices=ACTIVITY_TYPES)
    subject = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    activity_date = models.DateTimeField(auto_now_add=True)
    
    # Optional deal association
    deal = models.ForeignKey(
        Deal, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='activities'
    )
    
    # User who performed the activity
    performed_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='sales_activities'
    )

    class Meta:
        ordering = ['-activity_date']
        verbose_name = "Contact Activity"
        verbose_name_plural = "Contact Activities"

    def __str__(self):
        return f"{self.get_activity_type_display()} - {self.account.name}"

    def save(self, *args, **kwargs):
        # Update account's last contact date when activity is created
        super().save(*args, **kwargs)
        if not self.pk:  # Only on creation
            self.account.update_last_contact()
