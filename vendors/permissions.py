from rest_framework import permissions
from .models import Vendor


class IsSuperAdmin(permissions.BasePermission):
    """
    Custom permission to only allow super admins.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'superadmin'


class IsManager(permissions.BasePermission):
    """
    Custom permission to only allow managers.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'manager'


class IsManagerOrSuperAdmin(permissions.BasePermission):
    """
    Custom permission to only allow managers or super admins.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ['manager', 'superadmin']


class IsBranchManager(permissions.BasePermission):
    """
    Custom permission to only allow branch managers for their branch.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'manager'
    
    def has_object_permission(self, request, view, obj):
        # Super admins can access any object
        if request.user.role == 'superadmin':
            return True
        
        # Managers can only access objects from their branch
        if hasattr(request.user, 'managed_branch') and request.user.managed_branch:
            return obj.branch == request.user.managed_branch
        
        return False


class CanAccessVendor(permissions.BasePermission):
    """
    Custom permission to check if user can access a specific vendor.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        # Super admins can access any vendor
        if request.user.role == 'superadmin':
            return True
        
        # Managers can access vendors from their managed branch
        if request.user.role == 'manager' and hasattr(request.user, 'managed_branch'):
            return obj.branch == request.user.managed_branch
        
        # Staff can access vendors from their assigned branch
        if request.user.role == 'staff' and request.user.branch:
            return obj.branch == request.user.branch
        
        return False


class CanManageVendor(permissions.BasePermission):
    """
    Custom permission to check if user can manage a specific vendor (only BranchManagers).
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'manager'
    
    def has_object_permission(self, request, view, obj):
        # Only managers can manage vendors
        if request.user.role == 'manager' and hasattr(request.user, 'managed_branch'):
            return obj.branch == request.user.managed_branch
        
        return False


class CanCreateVendor(permissions.BasePermission):
    """
    Custom permission to check if user can create vendors (only BranchManagers).
    """
    def has_permission(self, request, view):
        if request.user.role != 'manager':
            return False
        
        # Check if user is assigned to a branch
        if not hasattr(request.user, 'managed_branch') or not request.user.managed_branch:
            return False
        
        return True 