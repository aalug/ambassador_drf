"""
URL mappings for ambassador app.
"""
from django.urls import path, include

from .views import ProductBackendAPIView, ProductFrontendAPIView

app_name = 'ambassador'

urlpatterns = [
    path('', include('common.urls')),
    path('products/frontend/', ProductFrontendAPIView.as_view(), name='products-frontend'),
    path('products/backend/', ProductBackendAPIView.as_view(), name='products-backend')
]

