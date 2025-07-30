from django.urls import path
from . import views

urlpatterns = [
    # Sales Accounts
    path('accounts/', views.SalesAccountListView.as_view(), name='sales-accounts-list'),
    path('accounts/<int:account_id>/', views.SalesAccountDetailView.as_view(), name='sales-account-detail'),
    path('accounts/<int:account_id>/status/', views.update_account_status, name='update-account-status'),
    path('accounts/<int:account_id>/assign/', views.assign_account, name='assign-account'),
    
    # Deals
    path('accounts/<int:account_id>/deals/', views.DealListView.as_view(), name='account-deals'),
    
    # Contact Activities
    path('accounts/<int:account_id>/activities/', views.ContactActivityListView.as_view(), name='account-activities'),
    
    # Statistics
    path('stats/', views.SalesAccountStatsView.as_view(), name='sales-accounts-stats'),
] 