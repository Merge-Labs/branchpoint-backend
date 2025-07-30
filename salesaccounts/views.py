from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.views import APIView
from django.db.models import Q, Sum, Count
from django.shortcuts import get_object_or_404

from .models import SalesAccount, Deal, ContactActivity
from .serializers import (
    SalesAccountSerializer,
    CreateSalesAccountSerializer,
    UpdateSalesAccountSerializer,
    DealSerializer,
    CreateDealSerializer,
    ContactActivitySerializer,
    CreateContactActivitySerializer,
    SalesAccountStatsSerializer
)


class SalesAccountListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """Get all sales accounts with filtering and search"""
        # Get query parameters
        search = request.query_params.get('search', '')
        status_filter = request.query_params.get('status', 'all')
        
        # Start with all accounts
        accounts = SalesAccount.objects.all()
        
        # Apply search filter
        if search:
            accounts = accounts.filter(
                Q(name__icontains=search) |
                Q(contact_person__icontains=search) |
                Q(email__icontains=search)
            )
        
        # Apply status filter
        if status_filter != 'all':
            accounts = accounts.filter(status=status_filter)
        
        # Serialize and return
        serializer = SalesAccountSerializer(accounts, many=True)
        return Response(serializer.data)

    def post(self, request):
        """Create a new sales account"""
        serializer = CreateSalesAccountSerializer(
            data=request.data, 
            context={'request': request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SalesAccountDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, account_id):
        """Get a specific sales account with all details"""
        account = get_object_or_404(SalesAccount, id=account_id)
        serializer = SalesAccountSerializer(account)
        return Response(serializer.data)

    def put(self, request, account_id):
        """Update a sales account"""
        account = get_object_or_404(SalesAccount, id=account_id)
        serializer = UpdateSalesAccountSerializer(account, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, account_id):
        """Delete a sales account"""
        account = get_object_or_404(SalesAccount, id=account_id)
        account.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class SalesAccountStatsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """Get sales accounts statistics"""
        total_accounts = SalesAccount.objects.count()
        active_deals = SalesAccount.objects.filter(status='active').count()
        total_value = SalesAccount.objects.aggregate(
            total=Sum('account_value')
        )['total'] or 0
        
        # Calculate conversion rate (active accounts / total accounts)
        conversion_rate = 0
        if total_accounts > 0:
            conversion_rate = (active_deals / total_accounts) * 100
        
        stats = {
            'total_accounts': total_accounts,
            'active_deals': active_deals,
            'total_value': total_value,
            'conversion_rate': round(conversion_rate, 2)
        }
        
        serializer = SalesAccountStatsSerializer(stats)
        return Response(serializer.data)


class DealListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, account_id):
        """Get all deals for a specific account"""
        account = get_object_or_404(SalesAccount, id=account_id)
        deals = account.deals.all()
        serializer = DealSerializer(deals, many=True)
        return Response(serializer.data)

    def post(self, request, account_id):
        """Create a new deal for an account"""
        account = get_object_or_404(SalesAccount, id=account_id)
        serializer = CreateDealSerializer(
            data=request.data,
            context={'request': request, 'account': account}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ContactActivityListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, account_id):
        """Get all contact activities for a specific account"""
        account = get_object_or_404(SalesAccount, id=account_id)
        activities = account.activities.all()
        serializer = ContactActivitySerializer(activities, many=True)
        return Response(serializer.data)

    def post(self, request, account_id):
        """Create a new contact activity for an account"""
        account = get_object_or_404(SalesAccount, id=account_id)
        serializer = CreateContactActivitySerializer(
            data=request.data,
            context={'request': request, 'account': account}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def update_account_status(request, account_id):
    """Update account status"""
    account = get_object_or_404(SalesAccount, id=account_id)
    new_status = request.data.get('status')
    
    if new_status not in dict(SalesAccount.STATUS_CHOICES):
        return Response(
            {'error': 'Invalid status'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    account.status = new_status
    account.save()
    
    serializer = SalesAccountSerializer(account)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def assign_account(request, account_id):
    """Assign account to a user"""
    account = get_object_or_404(SalesAccount, id=account_id)
    user_id = request.data.get('user_id')
    
    if user_id:
        try:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            user = User.objects.get(id=user_id)
            account.assigned_to = user
            account.save()
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
    else:
        account.assigned_to = None
        account.save()
    
    serializer = SalesAccountSerializer(account)
    return Response(serializer.data)
