from django.urls import path
from .order_views import *

urlpatterns = [
    path("orders", OrderListView.as_view(), name="order-list"),
    path("order/<str:order_id>", OrderDetailView.as_view(), name="order-detail"),
    path("order/<str:order_id>/update", OrderUpdateView.as_view(), name="order-update"),
    path("order/<str:order_id>/delete", OrderDeleteView.as_view(), name="order-delete"),
]