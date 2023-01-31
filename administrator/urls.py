"""
URL mappings for administrator app.
"""
from django.urls import path, include

from .views import (AmbassadorAPIView, ProductGenericAPIView,
                    OrderAPIView, LinkAPIView)

urlpatterns = [
    path('', include('common.urls')),
    path('ambassadors/', AmbassadorAPIView.as_view(), name='ambassadors'),
    path('products/', ProductGenericAPIView.as_view(), name='products'),
    path('products/<str:pk>/', ProductGenericAPIView.as_view(), name='product'),
    path('users/<str:pk>/links/', LinkAPIView.as_view(), name='links'),
    path('orders/', OrderAPIView.as_view(), name='orders'),
]

