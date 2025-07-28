from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser, PermissionsMixin, BaseUserManager
)
from django.utils import timezone


# ───────────────────────────────────────────────
# Constants
# ───────────────────────────────────────────────
ROLE_CHOICES = [
    ('superadmin', 'SuperAdmin'),
    ('manager', 'BranchManager'),
    ('staff', 'Staff'),
]

# ───────────────────────────────────────────────
# Custom User Manager
# ───────────────────────────────────────────────
class UserManager(BaseUserManager):
    def create_user(self, email, password=None, role='staff', **extra_fields):
        if not email:
            raise ValueError("Users must have an email address")

        email = self.normalize_email(email)
        user = self.model(email=email, role=role, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(email, password, role='superadmin', **extra_fields)


# ───────────────────────────────────────────────
# User Model
# ───────────────────────────────────────────────
class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='staff')
    branch = models.ForeignKey(
        'branches.Branch', on_delete=models.SET_NULL,
        null=True, blank=True,
        help_text="Only applicable for Branch Managers and Staff"
    )
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)  # for admin site access
    created_at = models.DateTimeField(default=timezone.now)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return f"{self.email} ({self.role})"


# ───────────────────────────────────────────────
# User Profile (Optional Extension)
# ───────────────────────────────────────────────
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    full_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
    photo = models.ImageField(upload_to='profiles/', null=True, blank=True)

    def __str__(self):
        return self.full_name

    class Meta:
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"
