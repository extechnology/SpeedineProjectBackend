from django.contrib import admin
from .user_models import (
    ContactModel,
    UserCartModel,
    UserCartItemsModel,
    UserOrderModel,
    UserOrderItemsModel,
    OrderStatus,
    UserAddressModel,
    ShippingCharge
)

# ================= CONTACT ==================
@admin.register(ContactModel)
class ContactAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "created")
    search_fields = ("name", "email")
    ordering = ("-created",)


# ================= CART ITEMS INLINE ==================
class CartItemsInline(admin.TabularInline):
    model = UserCartItemsModel
    extra = 0


# ================= USER CART ==================
@admin.register(UserCartModel)
class UserCartAdmin(admin.ModelAdmin):
    list_display = ("user", "cart_id", "created", "updated")
    search_fields = ("user__username", "cart_id")
    ordering = ("-created",)
    inlines = [CartItemsInline]


# ================= ORDER ITEMS INLINE ==================
class OrderItemsInline(admin.TabularInline):
    model = UserOrderItemsModel
    extra = 0
    # readonly_fields = ("razorpay_order_id", "razorpay_payment_id", "razorpay_signature")


# ================= USER ORDER ==================
@admin.register(UserOrderModel)
class UserOrderAdmin(admin.ModelAdmin):
    list_display = ("user", "order_id", "created", "updated")
    search_fields = ("user__username", "order_id")
    ordering = ("-created",)
    inlines = [OrderItemsInline]


# ================= USER ORDER ITEMS ==================
@admin.register(UserOrderItemsModel)
class UserOrderItemsAdmin(admin.ModelAdmin):
    list_display = (
        "user_order",
        "product",
        "quantity",
        "price",
        "created",
    )
    list_filter = ("created",)
    search_fields = ("user_order__order_id", "product__name")
    ordering = ("-created",)


# ================= ORDER STATUS ==================
@admin.register(OrderStatus)
class OrderStatusAdmin(admin.ModelAdmin):
    list_display = ("order", "status", "is_active", "created")
    list_filter = ("is_active",)
    search_fields = ("order__order_id", "status")
    ordering = ("-created",)


@admin.register(UserAddressModel)
class UserAddressAdmin(admin.ModelAdmin):
    list_display = ("user", "address", "created", "updated")
    search_fields = ("user__username", "address")
    ordering = ("-created",)

admin.site.register(ShippingCharge)