from django.db import models
from django.conf import settings

class Branch(models.Model):
    name = models.CharField(max_length=100, unique=True)
    location = models.CharField(max_length=255, blank=True)
    manager = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="managed_branch",
        limit_choices_to={"role": "manager"}
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
