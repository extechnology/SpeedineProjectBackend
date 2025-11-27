from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .user_views import CartViewSet, CartItemViewSet

router = DefaultRouter()
router.register(r'cart', CartViewSet, basename='cart')
router.register(r'cart-items', CartItemViewSet, basename='cart-items')

urlpatterns = [
    path('', include(router.urls)),
]