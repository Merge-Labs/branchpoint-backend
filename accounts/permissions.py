from rest_framework import permissions


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


class IsOwnerOrManager(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object or managers.
    """
    def has_object_permission(self, request, view, obj):
        # Managers and super admins can access any object
        if request.user.role in ['manager', 'superadmin']:
            return True
        
        # Users can only access their own objects
        return obj == request.user or getattr(obj, 'user', None) == request.user


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
        if hasattr(obj, 'branch'):
            return obj.branch == request.user.branch
        elif hasattr(obj, 'user') and hasattr(obj.user, 'branch'):
            return obj.user.branch == request.user.branch
        
        return False 