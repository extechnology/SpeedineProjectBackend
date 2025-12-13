from django.urls import path,include

urlpatterns = [
    path('order-info/', include('Dashboard.OrderInformations.order_urls')),
]
