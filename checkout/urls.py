"""
URL mappings for the checkout app.
"""
from django.urls import path
from .views import LinkAPIView, OrderAPIView, ConfirmOrderAPIView

app_name = 'checkout'

urlpatterns = [
    path('links/<str:code>/', LinkAPIView.as_view(), name='links'),
    path('orders/', OrderAPIView.as_view(), name='orders'),
    path('orders/confirm/', ConfirmOrderAPIView.as_view(), name='confirm-order'),
]
