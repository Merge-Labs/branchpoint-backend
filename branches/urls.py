from django.urls import path
from .views import (
    BranchListView, BranchDetailView, MyBranchView, BranchStatsView,
    BranchStaffView, AssignManagerView, RemoveManagerView, AvailableManagersView,
    branch_search, global_stats, bulk_assign_staff
)

app_name = 'branches'

urlpatterns = [
    # Branch CRUD operations (SuperAdmin only)
    path('', BranchListView.as_view(), name='branch-list'),
    path('<int:pk>/', BranchDetailView.as_view(), name='branch-detail'),
    
    # Current user's branch (Manager/Staff)
    path('my-branch/', MyBranchView.as_view(), name='my-branch'),
    
    # Branch statistics
    path('<int:pk>/stats/', BranchStatsView.as_view(), name='branch-stats'),
    path('my-branch/stats/', BranchStatsView.as_view(), name='my-branch-stats'),
    
    # Branch staff management
    path('<int:pk>/staff/', BranchStaffView.as_view(), name='branch-staff'),
    path('my-branch/staff/', BranchStaffView.as_view(), name='my-branch-staff'),
    
    # Manager assignment (SuperAdmin only)
    path('<int:pk>/assign-manager/', AssignManagerView.as_view(), name='assign-manager'),
    path('<int:pk>/remove-manager/', RemoveManagerView.as_view(), name='remove-manager'),
    path('available-managers/', AvailableManagersView.as_view(), name='available-managers'),
    
    # Bulk operations (SuperAdmin only)
    path('<int:pk>/bulk-assign-staff/', bulk_assign_staff, name='bulk-assign-staff'),
    
    # Search and utilities
    path('search/', branch_search, name='branch-search'),
    path('global-stats/', global_stats, name='global-stats'),
]