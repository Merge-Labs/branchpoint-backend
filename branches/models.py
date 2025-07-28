from django.db import models
from django.conf import settings


class Branch(models.Model):
    """
    Represents a physical or logical branch managed by a Branch Manager.
    """
    name = models.CharField(max_length=100, unique=True)
    location = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class StaffAssignment(models.Model):
    """
    Optional: Connect staff explicitly to a branch.
    Could be useful for audit history or supporting multi-branch staff in future.
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'staff'}
    )
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE)
    assigned_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email} → {self.branch.name}"
