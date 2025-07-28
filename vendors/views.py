from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.db.models import Q
from .models import Vendor
from .serializers import (
    VendorSerializer, VendorCreateSerializer, VendorUpdateSerializer,
    VendorStatsSerializer, VendorProductSerializer, VendorPurchaseSerializer,
    VendorSearchSerializer
)
from branches.permissions import IsManagerOrSuperAdmin, IsBranchManager


class VendorListView(generics.ListCreateAPIView):
    """List and create vendors (BranchManagers only for creation)"""
    serializer_class = VendorSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        
        if user.role == 'superadmin':
            return Vendor.objects.all()
        elif user.role == 'manager' and hasattr(user, 'managed_branch') and user.managed_branch:
            return Vendor.objects.filter(branch=user.managed_branch)
        elif user.role == 'staff' and user.branch:
            return Vendor.objects.filter(branch=user.branch)
        else:
            return Vendor.objects.none()
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return VendorCreateSerializer
        return VendorSerializer


class VendorDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Get, update, or delete a specific vendor"""
    serializer_class = VendorSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        
        if user.role == 'superadmin':
            return Vendor.objects.all()
        elif user.role == 'manager' and hasattr(user, 'managed_branch') and user.managed_branch:
            return Vendor.objects.filter(branch=user.managed_branch)
        elif user.role == 'staff' and user.branch:
            return Vendor.objects.filter(branch=user.branch)
        else:
            return Vendor.objects.none()
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return VendorUpdateSerializer
        return VendorSerializer
    
    def destroy(self, request, *args, **kwargs):
        vendor = self.get_object()
        
        # Check if vendor has associated products or purchases
        if vendor.total_products > 0 or vendor.total_purchases > 0:
            return Response({
                'error': True,
                'message': 'Cannot delete vendor with associated products or purchases'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        return super().destroy(request, *args, **kwargs)


class VendorStatsView(generics.RetrieveAPIView):
    """Get vendor statistics"""
    serializer_class = VendorStatsSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        
        if user.role == 'superadmin':
            return Vendor.objects.all()
        elif user.role == 'manager' and hasattr(user, 'managed_branch') and user.managed_branch:
            return Vendor.objects.filter(branch=user.managed_branch)
        elif user.role == 'staff' and user.branch:
            return Vendor.objects.filter(branch=user.branch)
        else:
            return Vendor.objects.none()


class VendorProductsView(generics.RetrieveAPIView):
    """Get products supplied by a vendor"""
    serializer_class = VendorProductSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        
        if user.role == 'superadmin':
            return Vendor.objects.all()
        elif user.role == 'manager' and hasattr(user, 'managed_branch') and user.managed_branch:
            return Vendor.objects.filter(branch=user.managed_branch)
        elif user.role == 'staff' and user.branch:
            return Vendor.objects.filter(branch=user.branch)
        else:
            return Vendor.objects.none()


class VendorPurchasesView(generics.RetrieveAPIView):
    """Get purchases from a vendor"""
    serializer_class = VendorPurchaseSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        
        if user.role == 'superadmin':
            return Vendor.objects.all()
        elif user.role == 'manager' and hasattr(user, 'managed_branch') and user.managed_branch:
            return Vendor.objects.filter(branch=user.managed_branch)
        elif user.role == 'staff' and user.branch:
            return Vendor.objects.filter(branch=user.branch)
        else:
            return Vendor.objects.none()


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def vendor_search(request):
    """Search vendors by name, contact person, or email"""
    query = request.query_params.get('q', '')
    
    if not query:
        return Response({
            'error': True,
            'message': 'Search query is required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    user = request.user
    
    if user.role == 'superadmin':
        vendors = Vendor.objects.filter(
            Q(name__icontains=query) | 
            Q(contact_person__icontains=query) | 
            Q(email__icontains=query)
        )
    elif user.role == 'manager' and hasattr(user, 'managed_branch') and user.managed_branch:
        vendors = Vendor.objects.filter(
            Q(branch=user.managed_branch) &
            (Q(name__icontains=query) | 
             Q(contact_person__icontains=query) | 
             Q(email__icontains=query))
        )
    elif user.role == 'staff' and user.branch:
        vendors = Vendor.objects.filter(
            Q(branch=user.branch) &
            (Q(name__icontains=query) | 
             Q(contact_person__icontains=query) | 
             Q(email__icontains=query))
        )
    else:
        vendors = Vendor.objects.none()
    
    serializer = VendorSearchSerializer(vendors, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def vendor_stats_summary(request):
    """Get summary statistics for vendors"""
    user = request.user
    
    if user.role == 'superadmin':
        total_vendors = Vendor.objects.count()
        active_vendors = Vendor.objects.filter(is_active=True).count()
        vendors_by_type = {}
        
        for vendor_type, _ in Vendor._meta.get_field('vendor_type').choices:
            vendors_by_type[vendor_type] = Vendor.objects.filter(vendor_type=vendor_type).count()
        
        # Get top vendors by total spent
        top_vendors = Vendor.objects.all()[:5]
        
    elif user.role == 'manager' and hasattr(user, 'managed_branch') and user.managed_branch:
        branch = user.managed_branch
        total_vendors = Vendor.objects.filter(branch=branch).count()
        active_vendors = Vendor.objects.filter(branch=branch, is_active=True).count()
        vendors_by_type = {}
        
        for vendor_type, _ in Vendor._meta.get_field('vendor_type').choices:
            vendors_by_type[vendor_type] = Vendor.objects.filter(branch=branch, vendor_type=vendor_type).count()
        
        # Get top vendors by total spent
        top_vendors = Vendor.objects.filter(branch=branch)[:5]
        
    elif user.role == 'staff' and user.branch:
        branch = user.branch
        total_vendors = Vendor.objects.filter(branch=branch).count()
        active_vendors = Vendor.objects.filter(branch=branch, is_active=True).count()
        vendors_by_type = {}
        
        for vendor_type, _ in Vendor._meta.get_field('vendor_type').choices:
            vendors_by_type[vendor_type] = Vendor.objects.filter(branch=branch, vendor_type=vendor_type).count()
        
        # Get top vendors by total spent
        top_vendors = Vendor.objects.filter(branch=branch)[:5]
        
    else:
        return Response({
            'error': True,
            'message': 'No branch assigned'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    return Response({
        'total_vendors': total_vendors,
        'active_vendors': active_vendors,
        'vendors_by_type': vendors_by_type,
        'top_vendors': VendorSerializer(top_vendors, many=True).data
    })


@api_view(['POST'])
@permission_classes([IsBranchManager])
def bulk_update_vendor_status(request):
    """Bulk update vendor status (BranchManagers only)"""
    vendor_ids = request.data.get('vendor_ids', [])
    is_active = request.data.get('is_active', True)
    
    if not vendor_ids:
        return Response({
            'error': True,
            'message': 'Vendor IDs are required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    user = request.user
    branch = user.managed_branch
    
    try:
        vendors = Vendor.objects.filter(id__in=vendor_ids, branch=branch)
        updated_count = vendors.update(is_active=is_active)
        
        return Response({
            'message': f'{updated_count} vendors updated successfully',
            'updated_count': updated_count
        })
    except Exception as e:
        return Response({
            'error': True,
            'message': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def vendor_by_type(request, vendor_type):
    """Get vendors by type"""
    user = request.user
    
    if user.role == 'superadmin':
        vendors = Vendor.objects.filter(vendor_type=vendor_type)
    elif user.role == 'manager' and hasattr(user, 'managed_branch') and user.managed_branch:
        vendors = Vendor.objects.filter(branch=user.managed_branch, vendor_type=vendor_type)
    elif user.role == 'staff' and user.branch:
        vendors = Vendor.objects.filter(branch=user.branch, vendor_type=vendor_type)
    else:
        vendors = Vendor.objects.none()
    
    serializer = VendorSerializer(vendors, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def active_vendors(request):
    """Get only active vendors"""
    user = request.user
    
    if user.role == 'superadmin':
        vendors = Vendor.objects.filter(is_active=True)
    elif user.role == 'manager' and hasattr(user, 'managed_branch') and user.managed_branch:
        vendors = Vendor.objects.filter(branch=user.managed_branch, is_active=True)
    elif user.role == 'staff' and user.branch:
        vendors = Vendor.objects.filter(branch=user.branch, is_active=True)
    else:
        vendors = Vendor.objects.none()
    
    serializer = VendorSerializer(vendors, many=True)
    return Response(serializer.data)
