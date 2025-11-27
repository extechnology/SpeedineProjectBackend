from django.db import models
from ..models import User
from ..ProductServices.product_models import ProductModel 
import uuid

class ContactModel(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Contact from {self.name} <{self.email}>"


class UserCartModel(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    cart_id = models.UUIDField(default=uuid.uuid4, editable=False)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user} - {self.cart_id}"


class UserCartItemsModel(models.Model):
    user_cart = models.ForeignKey(UserCartModel, on_delete=models.CASCADE)
    product = models.ForeignKey(ProductModel, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user_cart} - {self.product}"
