from django.urls import path
from . import views

urlpatterns = [
    path('products/', views.product_list_create),
    path('customers/', views.customer_list_create),
    path('sales/', views.list_sales),
    path('sales/create/', views.create_sale),
    path('payments/record/', views.record_payment),
    path('customers/<int:customer_id>/statement/', views.customer_statement),
]
