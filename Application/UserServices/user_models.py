from django.db import models


from ..models import User

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
    user_cart = models.ForeignKey(UserCartModel, on_delete=models.CASCADE, related_name='cart_items')
    product = models.ForeignKey('Application.ProductModel', on_delete=models.CASCADE, related_name='cart_items')
    quantity = models.IntegerField(default=1)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user_cart} - {self.product}"



class UserAddressModel(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,related_name='user_address')
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    address = models.TextField()
    city = models.CharField(max_length=255)
    state = models.CharField(max_length=255)
    country = models.CharField(max_length=255)
    pincode = models.CharField(max_length=20)
    landmark = models.CharField(max_length=255, null=True, blank=True)

    is_default = models.BooleanField(default=False)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user} - {self.address}"




class UserOrderModel(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    order_id = models.UUIDField(default=uuid.uuid4, editable=False)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user} - {self.order_id}"

class UserOrderItemsModel(models.Model):
    user_order = models.ForeignKey(UserOrderModel, on_delete=models.CASCADE, related_name='order_items')
    product = models.ForeignKey('Application.ProductModel', on_delete=models.CASCADE, related_name='order_items')
    quantity = models.IntegerField(default=1)
    total_price = models.FloatField(default=0.0)


    razorpay_order_id = models.CharField(max_length=255, blank=True, null=True)
    razorpay_payment_id = models.CharField(max_length=255, blank=True, null=True)
    razorpay_signature = models.CharField(max_length=255, blank=True, null=True)

    is_paid = models.BooleanField(default=False)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user_order} - {self.product}"

class OrderStatus(models.Model):
    order = models.ForeignKey(UserOrderModel, on_delete=models.CASCADE, related_name='order_status')
    status = models.CharField(max_length=255)

    is_active = models.BooleanField(default=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.order} - {self.status}"
    