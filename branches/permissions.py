from rest_framework import permissions
from .models import Branch


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
        
        # Managers can only access their own branch
        if hasattr(request.user, 'managed_branch') and request.user.managed_branch:
            return obj == request.user.managed_branch
        
        return False


class IsBranchStaff(permissions.BasePermission):
    """
    Custom permission to only allow staff for their assigned branch.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'staff'
    
    def has_object_permission(self, request, view, obj):
        # Super admins can access any object
        if request.user.role == 'superadmin':
            return True
        
        # Managers can access their managed branch
        if request.user.role == 'manager' and hasattr(request.user, 'managed_branch'):
            return obj == request.user.managed_branch
        
        # Staff can only access their assigned branch
        if request.user.role == 'staff' and request.user.branch:
            return obj == request.user.branch
        
        return False


class CanAccessBranch(permissions.BasePermission):
    """
    Custom permission to check if user can access a specific branch.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        # Super admins can access any branch
        if request.user.role == 'superadmin':
            return True
        
        # Managers can access their managed branch
        if request.user.role == 'manager' and hasattr(request.user, 'managed_branch'):
            return obj == request.user.managed_branch
        
        # Staff can access their assigned branch
        if request.user.role == 'staff' and request.user.branch:
            return obj == request.user.branch
        
        return False


class CanManageBranch(permissions.BasePermission):
    """
    Custom permission to check if user can manage a specific branch.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ['superadmin', 'manager']
    
    def has_object_permission(self, request, view, obj):
        # Super admins can manage any branch
        if request.user.role == 'superadmin':
            return True
        
        # Managers can only manage their own branch
        if request.user.role == 'manager' and hasattr(request.user, 'managed_branch'):
            return obj == request.user.managed_branch
        
        return False 