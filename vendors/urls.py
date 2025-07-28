from django.urls import path
from .views import (
    VendorListView, VendorDetailView, VendorStatsView, VendorProductsView,
    VendorPurchasesView, vendor_search, vendor_stats_summary, bulk_update_vendor_status,
    vendor_by_type, active_vendors
)

app_name = 'vendors'

urlpatterns = [
    # Vendor CRUD operations
    path('', VendorListView.as_view(), name='vendor-list'),
    path('<int:pk>/', VendorDetailView.as_view(), name='vendor-detail'),
    
    # Vendor statistics and details
    path('<int:pk>/stats/', VendorStatsView.as_view(), name='vendor-stats'),
    path('<int:pk>/products/', VendorProductsView.as_view(), name='vendor-products'),
    path('<int:pk>/purchases/', VendorPurchasesView.as_view(), name='vendor-purchases'),
    
    # Search and filtering
    path('search/', vendor_search, name='vendor-search'),
    path('type/<str:vendor_type>/', vendor_by_type, name='vendor-by-type'),
    path('active/', active_vendors, name='active-vendors'),
    
    # Statistics and bulk operations
    path('stats/summary/', vendor_stats_summary, name='vendor-stats-summary'),
    path('bulk-update-status/', bulk_update_vendor_status, name='bulk-update-vendor-status'),
]