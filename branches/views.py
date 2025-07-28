from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.db.models import Q
from .models import Branch
from .serializers import (
    BranchSerializer, BranchCreateSerializer, BranchUpdateSerializer,
    BranchStatsSerializer, BranchStaffSerializer, ManagerAssignmentSerializer,
    AvailableManagerSerializer
)
from accounts.permissions import IsSuperAdmin, IsManagerOrSuperAdmin, IsBranchManager

User = get_user_model()


class BranchListView(generics.ListCreateAPIView):
    """List all branches and create new ones (SuperAdmin only)"""
    serializer_class = BranchSerializer
    permission_classes = [IsSuperAdmin]
    
    def get_queryset(self):
        return Branch.objects.all()
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return BranchCreateSerializer
        return BranchSerializer


class BranchDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Get, update, or delete a specific branch (SuperAdmin only)"""
    queryset = Branch.objects.all()
    serializer_class = BranchSerializer
    permission_classes = [IsSuperAdmin]
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return BranchUpdateSerializer
        return BranchSerializer
    
    def destroy(self, request, *args, **kwargs):
        branch = self.get_object()
        
        # Check if branch has associated data
        if branch.total_products > 0 or branch.total_vendors > 0 or branch.total_sales > 0:
            return Response({
                'error': True,
                'message': 'Cannot delete branch with associated products, vendors, or sales'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Remove manager assignment
        if branch.manager:
            branch.remove_manager()
        
        return super().destroy(request, *args, **kwargs)


class MyBranchView(generics.RetrieveAPIView):
    """Get current user's assigned branch (Manager/Staff)"""
    serializer_class = BranchSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        user = self.request.user
        
        if user.role == 'manager':
            if hasattr(user, 'managed_branch') and user.managed_branch:
                return user.managed_branch
            else:
                return Response({
                    'error': True,
                    'message': 'No branch assigned'
                }, status=status.HTTP_404_NOT_FOUND)
        elif user.role == 'staff':
            if user.branch:
                return user.branch
            else:
                return Response({
                    'error': True,
                    'message': 'No branch assigned'
                }, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({
                'error': True,
                'message': 'Access denied'
            }, status=status.HTTP_403_FORBIDDEN)


class BranchStatsView(generics.RetrieveAPIView):
    """Get branch statistics"""
    serializer_class = BranchStatsSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        user = self.request.user
        branch_id = self.kwargs.get('pk')
        
        if user.role == 'superadmin':
            return get_object_or_404(Branch, id=branch_id)
        elif user.role == 'manager':
            if hasattr(user, 'managed_branch') and user.managed_branch and user.managed_branch.id == branch_id:
                return user.managed_branch
        elif user.role == 'staff':
            if user.branch and user.branch.id == branch_id:
                return user.branch
        
        return Response({
            'error': True,
            'message': 'Access denied'
        }, status=status.HTTP_403_FORBIDDEN)


class BranchStaffView(generics.RetrieveAPIView):
    """Get staff list for a branch"""
    serializer_class = BranchStaffSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        user = self.request.user
        branch_id = self.kwargs.get('pk')
        
        if user.role == 'superadmin':
            return get_object_or_404(Branch, id=branch_id)
        elif user.role == 'manager':
            if hasattr(user, 'managed_branch') and user.managed_branch and user.managed_branch.id == branch_id:
                return user.managed_branch
        elif user.role == 'staff':
            if user.branch and user.branch.id == branch_id:
                return user.branch
        
        return Response({
            'error': True,
            'message': 'Access denied'
        }, status=status.HTTP_403_FORBIDDEN)


class AssignManagerView(APIView):
    """Assign a manager to a branch (SuperAdmin only)"""
    permission_classes = [IsSuperAdmin]
    
    def post(self, request, pk):
        branch = get_object_or_404(Branch, id=pk)
        serializer = ManagerAssignmentSerializer(data=request.data)
        
        if serializer.is_valid():
            try:
                branch = serializer.assign_manager(branch)
                return Response({
                    'message': 'Manager assigned successfully',
                    'branch': BranchSerializer(branch).data
                })
            except Exception as e:
                return Response({
                    'error': True,
                    'message': str(e)
                }, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RemoveManagerView(APIView):
    """Remove manager from a branch (SuperAdmin only)"""
    permission_classes = [IsSuperAdmin]
    
    def post(self, request, pk):
        branch = get_object_or_404(Branch, id=pk)
        
        if not branch.manager:
            return Response({
                'error': True,
                'message': 'No manager assigned to this branch'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        branch.remove_manager()
        
        return Response({
            'message': 'Manager removed successfully',
            'branch': BranchSerializer(branch).data
        })


class AvailableManagersView(generics.ListAPIView):
    """Get list of available managers (not assigned to any branch)"""
    serializer_class = AvailableManagerSerializer
    permission_classes = [IsSuperAdmin]
    
    def get_queryset(self):
        return User.objects.filter(
            role='manager',
            managed_branch__isnull=True,
            is_active=True
        ).select_related('profile')


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def branch_search(request):
    """Search branches by name or location"""
    query = request.query_params.get('q', '')
    
    if not query:
        return Response({
            'error': True,
            'message': 'Search query is required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    user = request.user
    
    if user.role == 'superadmin':
        branches = Branch.objects.filter(
            Q(name__icontains=query) | Q(location__icontains=query)
        )
    elif user.role == 'manager':
        if hasattr(user, 'managed_branch') and user.managed_branch:
            branches = Branch.objects.filter(
                Q(id=user.managed_branch.id) &
                (Q(name__icontains=query) | Q(location__icontains=query))
            )
        else:
            branches = Branch.objects.none()
    elif user.role == 'staff':
        if user.branch:
            branches = Branch.objects.filter(
                Q(id=user.branch.id) &
                (Q(name__icontains=query) | Q(location__icontains=query))
            )
        else:
            branches = Branch.objects.none()
    else:
        branches = Branch.objects.none()
    
    serializer = BranchSerializer(branches, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def global_stats(request):
    """Get global branch statistics (SuperAdmin only)"""
    if request.user.role != 'superadmin':
        return Response({
            'error': True,
            'message': 'Access denied'
        }, status=status.HTTP_403_FORBIDDEN)
    
    total_branches = Branch.objects.count()
    active_branches = Branch.objects.filter(is_active=True).count()
    branches_with_managers = Branch.objects.filter(manager__isnull=False).count()
    
    # Get total counts across all branches
    total_staff = User.objects.filter(role='staff').count()
    total_managers = User.objects.filter(role='manager').count()
    
    return Response({
        'total_branches': total_branches,
        'active_branches': active_branches,
        'branches_with_managers': branches_with_managers,
        'total_staff': total_staff,
        'total_managers': total_managers,
    })


@api_view(['POST'])
@permission_classes([IsSuperAdmin])
def bulk_assign_staff(request, pk):
    """Bulk assign staff to a branch (SuperAdmin only)"""
    branch = get_object_or_404(Branch, id=pk)
    staff_ids = request.data.get('staff_ids', [])
    
    if not staff_ids:
        return Response({
            'error': True,
            'message': 'Staff IDs are required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        staff_users = User.objects.filter(id__in=staff_ids, role='staff')
        
        for user in staff_users:
            user.branch = branch
            user.save()
        
        return Response({
            'message': f'{staff_users.count()} staff members assigned to branch successfully'
        })
    except Exception as e:
        return Response({
            'error': True,
            'message': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)
