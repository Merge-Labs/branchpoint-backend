from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Branch

User = get_user_model()


class BranchSerializer(serializers.ModelSerializer):
    """Basic branch serializer for reading"""
    manager_name = serializers.CharField(source='manager.profile.full_name', read_only=True)
    manager_email = serializers.CharField(source='manager.email', read_only=True)
    staff_count = serializers.IntegerField(read_only=True)
    total_products = serializers.IntegerField(read_only=True)
    total_vendors = serializers.IntegerField(read_only=True)
    total_sales = serializers.IntegerField(read_only=True)
    total_revenue = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = Branch
        fields = [
            'id', 'name', 'location', 'description', 'is_active',
            'manager', 'manager_name', 'manager_email',
            'staff_count', 'total_products', 'total_vendors', 
            'total_sales', 'total_revenue',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class BranchCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating branches"""
    manager_id = serializers.IntegerField(required=False, write_only=True)
    
    class Meta:
        model = Branch
        fields = ['name', 'location', 'description', 'is_active', 'manager_id']
    
    def validate_name(self, value):
        """Ensure branch name is unique"""
        if Branch.objects.filter(name=value).exists():
            raise serializers.ValidationError('Branch with this name already exists.')
        return value
    
    def validate_manager_id(self, value):
        """Validate manager assignment"""
        if value:
            try:
                user = User.objects.get(id=value)
                if user.role != 'manager':
                    raise serializers.ValidationError('User must have role "manager"')
                if hasattr(user, 'managed_branch') and user.managed_branch:
                    raise serializers.ValidationError('User is already managing another branch')
            except User.DoesNotExist:
                raise serializers.ValidationError('User not found')
        return value
    
    def create(self, validated_data):
        manager_id = validated_data.pop('manager_id', None)
        branch = Branch.objects.create(**validated_data)
        
        if manager_id:
            user = User.objects.get(id=manager_id)
            branch.assign_manager(user)
        
        return branch


class BranchUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating branches"""
    manager_id = serializers.IntegerField(required=False, write_only=True)
    
    class Meta:
        model = Branch
        fields = ['name', 'location', 'description', 'is_active', 'manager_id']
    
    def validate_name(self, value):
        """Ensure branch name is unique (excluding current instance)"""
        instance = self.instance
        if Branch.objects.filter(name=value).exclude(id=instance.id).exists():
            raise serializers.ValidationError('Branch with this name already exists.')
        return value
    
    def validate_manager_id(self, value):
        """Validate manager assignment"""
        if value:
            try:
                user = User.objects.get(id=value)
                if user.role != 'manager':
                    raise serializers.ValidationError('User must have role "manager"')
                # Allow reassigning to same branch
                if hasattr(user, 'managed_branch') and user.managed_branch and user.managed_branch != self.instance:
                    raise serializers.ValidationError('User is already managing another branch')
            except User.DoesNotExist:
                raise serializers.ValidationError('User not found')
        return value
    
    def update(self, instance, validated_data):
        manager_id = validated_data.pop('manager_id', None)
        
        # Update branch fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Handle manager assignment
        if manager_id is not None:
            if manager_id:
                user = User.objects.get(id=manager_id)
                instance.assign_manager(user)
            else:
                instance.remove_manager()
        
        return instance


class BranchStatsSerializer(serializers.ModelSerializer):
    """Serializer for branch statistics"""
    stats = serializers.SerializerMethodField()
    
    class Meta:
        model = Branch
        fields = ['id', 'name', 'stats']
    
    def get_stats(self, obj):
        return obj.get_stats()


class BranchStaffSerializer(serializers.ModelSerializer):
    """Serializer for branch staff list"""
    staff = serializers.SerializerMethodField()
    
    class Meta:
        model = Branch
        fields = ['id', 'name', 'staff']
    
    def get_staff(self, obj):
        staff_list = obj.get_staff_list()
        return [
            {
                'id': user.id,
                'email': user.email,
                'full_name': user.profile.full_name if hasattr(user, 'profile') else '',
                'phone': user.profile.phone if hasattr(user, 'profile') else '',
                'date_joined': user.date_joined,
                'is_active': user.is_active
            }
            for user in staff_list
        ]


class ManagerAssignmentSerializer(serializers.Serializer):
    """Serializer for assigning managers to branches"""
    manager_id = serializers.IntegerField()
    
    def validate_manager_id(self, value):
        try:
            user = User.objects.get(id=value)
            if user.role != 'manager':
                raise serializers.ValidationError('User must have role "manager"')
            return value
        except User.DoesNotExist:
            raise serializers.ValidationError('User not found')
    
    def assign_manager(self, branch):
        user = User.objects.get(id=self.validated_data['manager_id'])
        branch.assign_manager(user)
        return branch


class AvailableManagerSerializer(serializers.ModelSerializer):
    """Serializer for available managers (not assigned to any branch)"""
    full_name = serializers.CharField(source='profile.full_name', read_only=True)
    email = serializers.CharField(read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'email', 'full_name', 'date_joined'] 