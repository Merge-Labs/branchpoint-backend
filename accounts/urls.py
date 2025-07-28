from django.urls import path
from .views import RegisterUserView, MeView
from rest_framework_simplejwt.views import (
    TokenObtainPairView, TokenRefreshView, TokenVerifyView
)

urlpatterns = [
    path('register/', RegisterUserView.as_view(), name='register-user'),
    path('me/', MeView.as_view(), name='me'),
    
    # JWT endpoints
    path('token/', TokenObtainPairView.as_view(), name='token-obtain'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token-verify'),
]
