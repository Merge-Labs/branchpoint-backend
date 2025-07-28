from django.urls import path
from payments.views import stk_push

urlpatterns = [
    path('stkpush/', stk_push, name='stk push'),
    

]