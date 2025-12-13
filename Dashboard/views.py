from django.shortcuts import render

# Create your views here.

from Application.UserServices.user_models import (
    UserOrderModel,
    UserOrderItemsModel,
    OrderStatus,
)

from Application.models import (
    User
)

from Application.ProductServices.product_models import (
    ProductModel,
    CustomerReviewModel,
    ProductImageModel
)


