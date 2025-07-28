# payments/serializers.py

from rest_framework import serializers
from .models import MpesaRequest, MpesaResponse, MpesaCallback


class MpesaCallbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = MpesaCallback
        fields = [
            'id',
            # 'response' field removed here because it's the foreign key to MpesaResponse,
            # and is usually handled in the nested serializer MpesaResponseSerializer
            # or in the view when creating the callback.
            'result_code',
            'result_description',
            'mpesa_receipt_number',
            'transaction_date',
            'phone_number',
            'amount',
            'timestamp'
        ]
        read_only_fields = ['id', 'timestamp']

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        # Ensure amount is string representation for consistency
        rep['amount'] = str(instance.amount) if instance.amount is not None else None
        # Format transaction_date
        rep['transaction_date'] = instance.transaction_date.isoformat() if instance.transaction_date else None
        return rep


class MpesaRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = MpesaRequest
        fields = [
            'id',
            'phone_number',
            'amount',
            'account_reference',
            'transaction_desc',
            'timestamp',
            'status' # Include the new status field
        ]
        read_only_fields = ['id', 'timestamp', 'status'] # Status is updated by the system

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['amount'] = str(instance.amount) # Ensure amount is string representation
        return rep


class MpesaResponseSerializer(serializers.ModelSerializer):
    request = MpesaRequestSerializer(read_only=True)  # Now shows full request data
    callback = MpesaCallbackSerializer(read_only=True) # Nested callback serializer

    class Meta:
        model = MpesaResponse
        fields = [
            'id',
            'request',
            'merchant_request_id',
            'checkout_request_id',
            'response_code',
            'response_description',
            'customer_message',
            'timestamp',
            'callback'
        ]
        read_only_fields = ['id', 'timestamp']

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        return rep


class MpesaRequestDetailSerializer(serializers.ModelSerializer):
    responses = MpesaResponseSerializer(many=True, read_only=True)

    class Meta:
        model = MpesaRequest
        fields = [
            'id',
            'phone_number',
            'amount',
            'account_reference',
            'transaction_desc',
            'timestamp',
            'status', # Include the new status field
            'responses'
        ]
        read_only_fields = ['id', 'timestamp', 'status']

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['amount'] = str(instance.amount)
        return rep