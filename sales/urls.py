from django.urls import path
from . import views
from .views import TodaySalesSummaryView, DailyTargetView, TodayProductsSoldCountView # Import the new views

urlpatterns = [
    path('products/', views.product_list_create),
    path('customers/', views.customer_list_create),
    path('sales/', views.list_sales),
    path('sales/create/', views.create_sale),
    path('payments/record/', views.record_payment),
    path('customers/<int:customer_id>/statement/', views.customer_statement),

    # NEW ENDPOINTS FOR DASHBOARD
    path('today_sales_summary/', TodaySalesSummaryView.as_view(), name='today-sales-summary'),
    path('daily_target/', DailyTargetView.as_view(), name='daily-target'),
    path('products/today_sold_count/', TodayProductsSoldCountView.as_view(), name='today-products-sold-count'),
]