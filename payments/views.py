# payments/views.py

import base64
import requests
from datetime import datetime
from django.conf import settings
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes # Import permission_classes
from rest_framework.permissions import AllowAny # Import AllowAny
from rest_framework.response import Response
from .models import MpesaRequest, MpesaResponse, MpesaCallback
from .serializers import MpesaRequestSerializer, MpesaResponseSerializer


@api_view(['POST'])
@permission_classes([AllowAny]) # Add this decorator for AllowAny
def stk_push(request):
    serializer = MpesaRequestSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    try:
        mpesa_request = serializer.save()
        print("MPESA Request created:", mpesa_request)

        try:
            response_data = initiate_stk_push(mpesa_request)
            print("STK Push Response Data:", response_data)
        except Exception as e:
            print("Failed to initiate STK Push:", str(e))
            return Response({"error": "Failed to initiate STK Push", "details": str(e)}, status=status.HTTP_502_BAD_GATEWAY)

        mpesa_response = MpesaResponse.objects.create(
            request=mpesa_request,
            merchant_request_id=response_data.get('MerchantRequestID', ''),
            checkout_request_id=response_data.get('CheckoutRequestID', ''),
            response_code=response_data.get('ResponseCode', ''),
            response_description=response_data.get('ResponseDescription', ''),
            customer_message=response_data.get('CustomerMessage', '')
        )

        response_serializer = MpesaResponseSerializer(mpesa_response)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    except Exception as e:
        print("Unexpected error during STK push:", str(e))
        return Response({"error": "Unexpected error", "details": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def initiate_stk_push(mpesa_request):
    try:
        access_token = get_access_token()
    except Exception as e:
        raise Exception(f"Access token error: {str(e)}")

    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    callback_url = f"{settings.MPESA_CALLBACK_URL}/mpesa/api/mpesa/callback/"
    print("Callback URL being sent to Safaricom:", callback_url)

    payload = {
        "BusinessShortCode": settings.MPESA_SHORTCODE,
        "Password": generate_password(timestamp),
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": float(mpesa_request.amount),
        "PartyA": mpesa_request.phone_number,
        "PartyB": settings.MPESA_SHORTCODE,
        "PhoneNumber": mpesa_request.phone_number,
        "CallBackURL": callback_url,
        "AccountReference": mpesa_request.account_reference,
        "TransactionDesc": mpesa_request.transaction_desc
    }

    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    try:
        response = requests.post("https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest", json=payload, headers=headers)
        response.raise_for_status()
        return response.json()
        
    except requests.exceptions.RequestException as e:
        print("STK push request failed:", str(e))
        raise Exception(f"STK push request failed: {getattr(e.response, 'text', str(e))}")


def get_access_token():
    consumer_key = settings.MPESA_CONSUMER_KEY
    consumer_secret = settings.MPESA_CONSUMER_SECRET
    api_url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"

    try:
        response = requests.get(api_url, auth=(consumer_key, consumer_secret))
        response.raise_for_status()
        access_token = response.json().get('access_token')
        if not access_token:
            raise Exception("Access token not found in response")
        return access_token
    except requests.exceptions.RequestException as e:
        print("Token request failed:", str(e))
        raise Exception(f"Token request failed: {getattr(e.response, 'text', str(e))}")


def generate_password(timestamp):
    try:
        shortcode = settings.MPESA_SHORTCODE
        passkey = settings.MPESA_PASSKEY
        data_to_encode = shortcode + passkey + timestamp
        encoded_string = base64.b64encode(data_to_encode.encode())
        return encoded_string.decode('utf-8')
    except Exception as e:
        raise Exception(f"Password generation failed: {str(e)}")


@api_view(['POST'])
@permission_classes([AllowAny]) # Also add AllowAny here if the callback should be public
def mpesa_callback(request):
    print("Received callback:", request.data)
    try:
        callback_data = request.data.get('Body', {}).get('stkCallback')
        if not callback_data:
            return Response({"error": "Callback data missing"}, status=status.HTTP_400_BAD_REQUEST)

        merchant_request_id = callback_data.get('MerchantRequestID')
        result_code = callback_data.get('ResultCode')
        result_description = callback_data.get('ResultDesc')
        metadata = callback_data.get('CallbackMetadata', {}).get('Item', [])

        mpesa_receipt_number = None
        transaction_date = None
        phone_number = None
        amount = None

        for item in metadata:
            name = item.get('Name')
            value = item.get('Value')
            if name == "MpesaReceiptNumber":
                mpesa_receipt_number = value
            elif name == "TransactionDate":
                transaction_date = datetime.strptime(str(value), '%Y%m%d%H%M%S') if value else None
            elif name == "PhoneNumber":
                phone_number = str(value)
            elif name == "Amount":
                amount = float(value) if value else None

        # Try to get MpesaRequest based on MerchantRequestID
        # The MpesaResponse model already stores MerchantRequestID.
        # It's more logical to find the MpesaResponse first, then link to its request.
        # Or, ideally, Safaricom sends back the CheckoutRequestID, which is unique
        # for a given initiated transaction. Let's adjust this part.
        
        # --- Adjusted Callback Logic ---
        checkout_request_id_from_callback = callback_data.get('CheckoutRequestID')
        if not checkout_request_id_from_callback:
            print("Error: CheckoutRequestID missing in callback.")
            return Response({"error": "CheckoutRequestID missing in callback data"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Find the MpesaResponse associated with this callback
            # We assume CheckoutRequestID is unique enough to link the callback
            mpesa_response_instance = MpesaResponse.objects.get(checkout_request_id=checkout_request_id_from_callback)
            mpesa_request_instance = mpesa_response_instance.request # Get the original request

        except MpesaResponse.DoesNotExist:
            print(f"Error: MpesaResponse with CheckoutRequestID {checkout_request_id_from_callback} not found.")
            return Response({"error": "Related MpesaResponse not found for this callback"}, status=status.HTTP_404_NOT_FOUND)
        except MpesaResponse.MultipleObjectsReturned:
            print(f"Error: Multiple MpesaResponse objects found for CheckoutRequestID {checkout_request_id_from_callback}.")
            # Handle this case, e.g., by logging and perhaps picking the latest or raising an error
            return Response({"error": "Multiple matching MpesaResponse found. Ambiguous callback."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


        # Update the status of the associated MpesaRequest
        mpesa_request_instance.status = 'SUCCESS' if result_code == 0 else 'FAILED'
        mpesa_request_instance.save()
        print(f"MpesaRequest {mpesa_request_instance.id} status updated to {mpesa_request_instance.status}")


        # Check if a callback already exists for this response to prevent duplicates
        if hasattr(mpesa_response_instance, 'callback') and mpesa_response_instance.callback:
            print(f"Warning: Callback already exists for MpesaResponse {mpesa_response_instance.id}. Skipping duplicate creation.")
            return Response({"message": "Callback already processed"}, status=status.HTTP_200_OK)


        MpesaCallback.objects.create(
            response=mpesa_response_instance, # Link to MpesaResponse, not MpesaRequest
            result_code=result_code,
            result_description=result_description,
            mpesa_receipt_number=mpesa_receipt_number,
            transaction_date=transaction_date,
            phone_number=phone_number,
            amount=amount,
            callback_metadata=callback_data.get('CallbackMetadata')
        )
        print("MpesaCallback created successfully.")

        return Response({"message": "Callback processed successfully"}, status=status.HTTP_200_OK)

    except Exception as e:
        print("Callback processing failed:", str(e))
        # Log the full traceback in production for better debugging
        import traceback
        traceback.print_exc()
        return Response({"error": f"Callback processing failed: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)