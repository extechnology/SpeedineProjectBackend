from django.urls import path,include

urlpatterns = [
    path('auth/', include('Application.Authentication.auth_urls')),
    
    path('categories/', include('Application.CategoryServices.category_urls')),
    
    path('products/', include('Application.ProductServices.product_urls')),
    
    path('users/', include('Application.UserServices.user_urls')),
    
    path('ui/', include('Application.UIServices.ui_urls')),
]