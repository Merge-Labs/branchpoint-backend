from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status, permissions

from .models import Product, Customer, Sale, SaleItem, Payment
from .serializers import (
    ProductSerializer,
    CustomerSerializer,
    SaleSerializer,
    CreateSaleSerializer,
    PaymentSerializer,
)

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
            if product.stock < quantity:
                return Response(
                    {"detail": f"Not enough stock for {product.name}"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            SaleItem.objects.create(
                sale=sale,
                product=product,
                quantity=quantity,
                price_at_sale=product.price
            )

            product.stock -= quantity
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
        customer.balance -= payment.amount
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

    sales = Sale.objects.filter(customer=customer)
    payments = Payment.objects.filter(customer=customer)

    return Response({
        "customer": CustomerSerializer(customer).data,
        "sales": SaleSerializer(sales, many=True).data,
        "payments": PaymentSerializer(payments, many=True).data,
    })
