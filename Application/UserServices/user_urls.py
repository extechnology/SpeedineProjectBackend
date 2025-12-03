from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .user_views import (
    CartViewSet, 
    CartItemViewSet, 
    ContactUsViewSet, 
    UserAddressAPIView, 
    CurrentUserAPIView,
    create_order,
    verify_payment,
    UserOrderAPIView,
    generate_invoice_pdf,
)
router = DefaultRouter()
router.register(r'cart', CartViewSet, basename='cart')
router.register(r'cart-items', CartItemViewSet, basename='cart-items')
router.register(r'contact-us', ContactUsViewSet, basename='contact-us')

urlpatterns = [
    path('', include(router.urls)),
    
    path('current-user/', CurrentUserAPIView.as_view(), name='current-user'),
    path('user-address/', UserAddressAPIView.as_view(), name='user-address'),
    path('user-address/<int:pk>/', UserAddressAPIView.as_view(), name='user-address'),

    path('create-order/', create_order, name='create-order'),
    path('verify-payment/', verify_payment, name='verify-payment'),

    path('user-order/', UserOrderAPIView.as_view(), name='user-order'),

    # path('invoice/generate/<str:order_id>/', generate_invoice_pdf, name='generate_invoice'),

]