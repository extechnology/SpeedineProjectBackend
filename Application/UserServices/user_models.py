from django.db import models
from ..models import User
import uuid


class ShippingCharge(models.Model):
    charge = models.FloatField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.charge}"


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
    name = models.CharField(max_length=255,default='')
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
    
    def save(self, *args, **kwargs):
        if self.is_default:
            UserAddressModel.objects.filter(
                user=self.user
            ).exclude(pk=self.pk).update(is_default=False)

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user} - {self.address}"




class UserOrderModel(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    order_id = models.UUIDField(default=uuid.uuid4, editable=False)

    shipping_address = models.ForeignKey(UserAddressModel, on_delete=models.SET_NULL, null=True)

    total_amount = models.FloatField(default=0.0)
    discount_amount = models.FloatField(default=0.0)
    final_amount = models.FloatField(default=0.0)
    invoice = models.FileField(upload_to='invoices/', null=True, blank=True)

    razorpay_order_id = models.CharField(max_length=255, null=True, blank=True)
    razorpay_payment_id = models.CharField(max_length=255, null=True, blank=True)
    razorpay_signature = models.CharField(max_length=255, null=True, blank=True)
    is_paid = models.BooleanField(default=False)

    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('shipped', 'Shipped'),
        ('out_for_delivery', 'Out for Delivery'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    )
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user} - {self.order_id}"


class UserOrderItemsModel(models.Model):
    user_order = models.ForeignKey(UserOrderModel, on_delete=models.CASCADE, related_name='order_items')
    product = models.ForeignKey('Application.ProductModel', on_delete=models.PROTECT, related_name='order_items')
    quantity = models.PositiveIntegerField(default=1)
    price = models.FloatField(default=0.0)  # snapshot of product price

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user_order} - {self.product}"



class OrderStatus(models.Model):
    class StatusChoices(models.TextChoices):
        PENDING = "pending"
        PROCESSING = "processing"
        SHIPPED = "shipped"
        OUT_FOR_DELIVERY = "out_for_delivery"
        DELIVERED = "delivered"
        CANCELLED = "cancelled"

    order = models.ForeignKey(UserOrderModel, on_delete=models.CASCADE, related_name='order_status')
    status = models.CharField(max_length=50, choices=StatusChoices.choices)

    is_active = models.BooleanField(default=True)
    
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if self.is_active:
            OrderStatus.objects.filter(order=self.order).exclude(pk=self.pk).update(is_active=False)
        super().save(*args, **kwargs)
