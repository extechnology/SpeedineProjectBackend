from django.urls import path
from .product_views import *

urlpatterns = [
    path('list/', ProductListAPIView.as_view(), name='product-list'),
    path('details/<int:id>/', ProductDetailAPIView.as_view(), name='product-detail'),

    path('category/', CategoryView.as_view(), name='category'), 
    
]