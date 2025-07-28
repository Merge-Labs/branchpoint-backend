from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Vendor
from branches.serializers import BranchSerializer

User = get_user_model()


class VendorSerializer(serializers.ModelSerializer):
    """Basic vendor serializer for reading"""
    branch_name = serializers.CharField(source='branch.name', read_only=True)
    added_by_name = serializers.CharField(source='added_by.profile.full_name', read_only=True)
    total_products = serializers.IntegerField(read_only=True)
    total_purchases = serializers.IntegerField(read_only=True)
    total_spent = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    last_purchase_date = serializers.DateField(read_only=True)
    
    class Meta:
        model = Vendor
        fields = [
            'id', 'name', 'contact_person', 'phone_number', 'email', 'address',
            'description', 'is_active', 'vendor_type', 'payment_terms', 'tax_id',
            'website', 'branch', 'branch_name', 'added_by', 'added_by_name',
            'total_products', 'total_purchases', 'total_spent', 'last_purchase_date',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class VendorCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating vendors (BranchManagers only)"""
    
    class Meta:
        model = Vendor
        fields = [
            'name', 'contact_person', 'phone_number', 'email', 'address',
            'description', 'is_active', 'vendor_type', 'payment_terms', 'tax_id',
            'website'
        ]
    
    def validate_name(self, value):
        """Ensure vendor name is unique within the branch"""
        request = self.context.get('request')
        if request and hasattr(request.user, 'managed_branch') and request.user.managed_branch:
            branch = request.user.managed_branch
            if Vendor.objects.filter(name=value, branch=branch).exists():
                raise serializers.ValidationError('A vendor with this name already exists in your branch.')
        return value
    
    def create(self, validated_data):
        request = self.context.get('request')
        if not request or request.user.role != 'manager':
            raise serializers.ValidationError('Only branch managers can create vendors.')
        
        if not hasattr(request.user, 'managed_branch') or not request.user.managed_branch:
            raise serializers.ValidationError('You must be assigned to a branch to create vendors.')
        
        validated_data['branch'] = request.user.managed_branch
        validated_data['added_by'] = request.user
        
        return super().create(validated_data)


class VendorUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating vendors (BranchManagers only)"""
    
    class Meta:
        model = Vendor
        fields = [
            'name', 'contact_person', 'phone_number', 'email', 'address',
            'description', 'is_active', 'vendor_type', 'payment_terms', 'tax_id',
            'website'
        ]
    
    def validate_name(self, value):
        """Ensure vendor name is unique within the branch (excluding current instance)"""
        request = self.context.get('request')
        instance = self.instance
        
        if request and hasattr(request.user, 'managed_branch') and request.user.managed_branch:
            branch = request.user.managed_branch
            if Vendor.objects.filter(name=value, branch=branch).exclude(id=instance.id).exists():
                raise serializers.ValidationError('A vendor with this name already exists in your branch.')
        return value
    
    def update(self, instance, validated_data):
        request = self.context.get('request')
        if not request or request.user.role != 'manager':
            raise serializers.ValidationError('Only branch managers can update vendors.')
        
        if not instance.can_be_managed_by(request.user):
            raise serializers.ValidationError('You can only update vendors in your managed branch.')
        
        return super().update(instance, validated_data)


class VendorStatsSerializer(serializers.ModelSerializer):
    """Serializer for vendor statistics"""
    stats = serializers.SerializerMethodField()
    
    class Meta:
        model = Vendor
        fields = ['id', 'name', 'branch_name', 'stats']
    
    def get_stats(self, obj):
        return obj.get_stats()


class VendorProductSerializer(serializers.ModelSerializer):
    """Serializer for vendor with their products"""
    products = serializers.SerializerMethodField()
    
    class Meta:
        model = Vendor
        fields = ['id', 'name', 'products']
    
    def get_products(self, obj):
        try:
            products = obj.products.all()
            return [
                {
                    'id': product.id,
                    'name': product.name,
                    'sku': getattr(product, 'sku', ''),
                    'price': getattr(product, 'price', 0),
                    'is_active': getattr(product, 'is_active', True)
                }
                for product in products
            ]
        except:
            return []


class VendorPurchaseSerializer(serializers.ModelSerializer):
    """Serializer for vendor with their purchases"""
    purchases = serializers.SerializerMethodField()
    
    class Meta:
        model = Vendor
        fields = ['id', 'name', 'purchases']
    
    def get_purchases(self, obj):
        try:
            purchases = obj.purchases.all()[:10]  # Limit to last 10 purchases
            return [
                {
                    'id': purchase.id,
                    'purchase_date': purchase.purchase_date,
                    'total_amount': purchase.total_amount,
                    'status': getattr(purchase, 'status', ''),
                    'reference': getattr(purchase, 'reference', '')
                }
                for purchase in purchases
            ]
        except:
            return []


class VendorSearchSerializer(serializers.ModelSerializer):
    """Serializer for vendor search results"""
    branch_name = serializers.CharField(source='branch.name', read_only=True)
    
    class Meta:
        model = Vendor
        fields = ['id', 'name', 'contact_person', 'phone_number', 'email', 'vendor_type', 'branch_name', 'is_active'] 