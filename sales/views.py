from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.views import APIView # Import APIView

from .models import Product, Customer, Sale, SaleItem, Payment
from .serializers import (
    ProductSerializer,
    CustomerSerializer,
    SaleSerializer,
    CreateSaleSerializer,
    PaymentSerializer,
)

from datetime import date, timedelta # Import date and timedelta
from django.db.models import Sum, F # Import Sum and F

# 🧾 PRODUCT VIEWS
@api_view(['GET', 'POST'])
@permission_classes([permissions.IsAuthenticated])
def product_list_create(request):
    if request.method == 'GET':
        products = Product.objects.all()
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = ProductSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# 👤 CUSTOMER VIEWS
@api_view(['GET', 'POST'])
@permission_classes([permissions.IsAuthenticated])
def customer_list_create(request):
    if request.method == 'GET':
        customers = Customer.objects.all()
        serializer = CustomerSerializer(customers, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = CustomerSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# 💸 SALE VIEWS
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def create_sale(request):
    data = request.data
    items = data.pop('items', [])
    sale_serializer = CreateSaleSerializer(data=data)

    if sale_serializer.is_valid():
        sale = sale_serializer.save(salesperson=request.user)

        for item in items:
            product = Product.objects.get(id=item['product'])
            quantity = item['quantity']
            # FIX: Use product.stock_quantity instead of product.stock
            if product.stock_quantity < quantity:
                # Optionally, clean up the sale created so far if this is a transaction
                sale.delete()
                return Response(
                    {"detail": f"Not enough stock for {product.name}. Available: {product.stock_quantity}, Requested: {quantity}"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            SaleItem.objects.create(
                sale=sale,
                product=product,
                quantity=quantity,
                price_at_sale=product.price # Or item['price_at_sale'] if you want to allow custom price
            )

            product.stock_quantity -= quantity # FIX: Use product.stock_quantity
            product.save()

        return Response(SaleSerializer(sale).data, status=status.HTTP_201_CREATED)

    return Response(sale_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# 📋 LIST SALES
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def list_sales(request):
    sales = Sale.objects.all().order_by('-created_at')
    serializer = SaleSerializer(sales, many=True)
    return Response(serializer.data)


# 💵 RECORD PAYMENT
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def record_payment(request):
    serializer = PaymentSerializer(data=request.data)
    if serializer.is_valid():
        payment = serializer.save(received_by=request.user)

        # Update customer balance
        customer = payment.customer
        # Ensure customer balance is updated correctly for payments
        # If recording a payment means reducing what they owe, then it should be customer.balance -= payment.amount
        customer.balance -= payment.amount # Assuming balance is what they *owe*
        customer.save()

        return Response(PaymentSerializer(payment).data, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# 📑 CUSTOMER STATEMENT
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def customer_statement(request, customer_id):
    try:
        customer = Customer.objects.get(id=customer_id)
    except Customer.DoesNotExist:
        return Response({"error": "Customer not found"}, status=404)

    sales = Sale.objects.filter(customer=customer).order_by('created_at')
    payments = Payment.objects.filter(customer=customer).order_by('received_at')

    # You might want to combine these into a single chronological statement
    # For now, returning separately as per current structure
    return Response({
        "customer": CustomerSerializer(customer).data,
        "sales": SaleSerializer(sales, many=True).data,
        "payments": PaymentSerializer(payments, many=True).data,
    })


# --- NEW VIEWS FOR SALESPERSON DASHBOARD ---

class TodaySalesSummaryView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        today = date.today()
        today_sales = Sale.objects.filter(created_at__date=today)

        total_sales_amount = today_sales.aggregate(total=Sum('total_amount'))['total'] or 0
        total_transactions = today_sales.count()
        total_customers_served = today_sales.values('customer').distinct().count() # Count unique customers

        return Response({
            'total_sales': float(total_sales_amount), # Convert Decimal to float for JSON
            'total_transactions': total_transactions,
            'total_customers_served': total_customers_served,
        }, status=status.HTTP_200_OK)


class DailyTargetView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        # This is a placeholder for actual target logic.
        # You'd likely fetch the daily target from a database or configuration.
        # For now, let's use a mock target or a simple calculation.
        
        # Example: A fixed daily target
        DAILY_SALES_TARGET = 50000.00 # KSh
        
        today = date.today()
        today_sales_amount = Sale.objects.filter(created_at__date=today).aggregate(total=Sum('total_amount'))['total'] or 0

        percentage_achieved = 0
        if DAILY_SALES_TARGET > 0:
            percentage_achieved = (float(today_sales_amount) / DAILY_SALES_TARGET) * 100
            if percentage_achieved > 100:
                percentage_achieved = 100.0 # Cap at 100% for display if desired

        return Response({
            'daily_target': DAILY_SALES_TARGET,
            'current_sales': float(today_sales_amount),
            'percentage_achieved': round(percentage_achieved, 2), # Round to 2 decimal places
        }, status=status.HTTP_200_OK)


class TodayProductsSoldCountView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        today = date.today()
        
        # Calculate the sum of quantities for all SaleItems created today
        # This correctly reflects the total number of individual product units sold
        total_products_sold = SaleItem.objects.filter(
            sale__created_at__date=today
        ).aggregate(total_quantity=Sum('quantity'))['total_quantity']

        if total_products_sold is None:
            total_products_sold = 0

        return Response({'total_products_sold': total_products_sold}, status=status.HTTP_200_OK)