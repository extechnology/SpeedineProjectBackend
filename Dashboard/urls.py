from django.urls import path,include

urlpatterns = [
    path('order-info/', include('Dashboard.OrderInformations.order_urls')),
    path('user-info/', include('Dashboard.UserInformations.user_urls')),
]
