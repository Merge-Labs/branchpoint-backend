# payments/models.py

from django.db import models
from django.utils import timezone


class MpesaRequest(models.Model):
    phone_number = models.CharField(max_length=15, help_text="Phone number in format 2547XXXXXXXX")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    account_reference = models.CharField(max_length=50)
    transaction_desc = models.CharField(max_length=255)
    # Added status field to MpesaRequest for easier tracking
    status = models.CharField(max_length=20, default='PENDING',
                              choices=[('PENDING', 'Pending'), ('SUCCESS', 'Success'), ('FAILED', 'Failed')])
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.phone_number} - {self.amount} - {self.status} @ {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}"

    def is_recent(self):
        return self.timestamp >= timezone.now() - timezone.timedelta(days=1)
    is_recent.boolean = True
    is_recent.short_description = 'Requested Recently?'

    def get_latest_response(self):
        return self.responses.order_by('-timestamp').first()

    class Meta:
        ordering = ['-timestamp']
        verbose_name = "M-Pesa Request"
        verbose_name_plural = "M-Pesa Requests"


class MpesaResponse(models.Model):
    request = models.ForeignKey(MpesaRequest, on_delete=models.CASCADE, related_name='responses')
    merchant_request_id = models.CharField(max_length=255, blank=True, null=True)
    checkout_request_id = models.CharField(max_length=255, blank=True, null=True)
    response_code = models.CharField(max_length=10, blank=True, null=True)
    response_description = models.CharField(max_length=255, blank=True, null=True)
    customer_message = models.CharField(max_length=255, blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Response to {self.request.phone_number} - Code: {self.response_code or 'Pending'}"

    def is_successful(self):
        return self.response_code == "0"
    is_successful.boolean = True
    is_successful.short_description = 'Success?'

    class Meta:
        ordering = ['-timestamp']
        verbose_name = "M-Pesa Response"
        verbose_name_plural = "M-Pesa Responses"


class MpesaCallback(models.Model):
    # Changed from response to request, but then changed back to response (OneToOneField with MpesaResponse)
    # This is more logical as a callback directly relates to a specific STK push response.
    # The `related_name='callback'` ensures you can access callback from MpesaResponse.
    response = models.OneToOneField(MpesaResponse, on_delete=models.CASCADE, related_name='callback')
    result_code = models.CharField(max_length=10)
    result_description = models.CharField(max_length=255)
    mpesa_receipt_number = models.CharField(max_length=100, blank=True, null=True)
    transaction_date = models.DateTimeField(blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    callback_metadata = models.JSONField(blank=True, null=True, help_text="Raw callback metadata from Safaricom")
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        # Ensure that self.response.request exists before accessing
        request_info = f"request ID {self.response.request.id}" if hasattr(self.response, 'request') else "unknown request"
        return f"Callback for {request_info} - Result: {self.result_code}"

    def is_successful(self):
        return self.result_code == "0"
    is_successful.boolean = True
    is_successful.short_description = "Success?"

    class Meta:
        ordering = ['-timestamp']
        verbose_name = "M-Pesa Callback"
        verbose_name_plural = "M-Pesa Callbacks"