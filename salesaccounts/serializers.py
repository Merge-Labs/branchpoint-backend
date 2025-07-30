from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import SalesAccount, Deal, ContactActivity

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email']


class DealSerializer(serializers.ModelSerializer):
    class Meta:
        model = Deal
        fields = [
            'id', 'title', 'value', 'stage', 'expected_close_date', 
            'probability', 'created_at', 'updated_at'
        ]


class ContactActivitySerializer(serializers.ModelSerializer):
    performed_by = UserSerializer(read_only=True)
    activity_type_display = serializers.CharField(source='get_activity_type_display', read_only=True)

    class Meta:
        model = ContactActivity
        fields = [
            'id', 'activity_type', 'activity_type_display', 'subject', 
            'description', 'activity_date', 'performed_by'
        ]


class SalesAccountSerializer(serializers.ModelSerializer):
    deals = DealSerializer(many=True, read_only=True)
    activities = ContactActivitySerializer(many=True, read_only=True)
    created_by = UserSerializer(read_only=True)
    assigned_to = UserSerializer(read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    avatar = serializers.CharField(read_only=True)

    class Meta:
        model = SalesAccount
        fields = [
            'id', 'name', 'contact_person', 'email', 'phone', 'location',
            'account_value', 'status', 'status_display', 'deals_count',
            'last_contact_date', 'created_at', 'updated_at', 'created_by',
            'assigned_to', 'deals', 'activities', 'avatar'
        ]


class CreateSalesAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = SalesAccount
        fields = [
            'name', 'contact_person', 'email', 'phone', 'location',
            'account_value', 'status', 'assigned_to'
        ]

    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class UpdateSalesAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = SalesAccount
        fields = [
            'name', 'contact_person', 'email', 'phone', 'location',
            'account_value', 'status', 'assigned_to'
        ]


class CreateDealSerializer(serializers.ModelSerializer):
    class Meta:
        model = Deal
        fields = [
            'title', 'value', 'stage', 'expected_close_date', 'probability'
        ]

    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        validated_data['account'] = self.context['account']
        return super().create(validated_data)


class CreateContactActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactActivity
        fields = [
            'activity_type', 'subject', 'description', 'deal'
        ]

    def create(self, validated_data):
        validated_data['performed_by'] = self.context['request'].user
        validated_data['account'] = self.context['account']
        return super().create(validated_data)


class SalesAccountStatsSerializer(serializers.Serializer):
    total_accounts = serializers.IntegerField()
    active_deals = serializers.IntegerField()
    total_value = serializers.DecimalField(max_digits=12, decimal_places=2)
    conversion_rate = serializers.FloatField() 