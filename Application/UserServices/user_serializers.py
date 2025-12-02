from rest_framework import serializers
from .user_models import UserCartModel, UserCartItemsModel,ContactModel,UserAddressModel,UserOrderItemsModel,UserOrderModel,OrderStatus
from ..ProductServices.product_serializers import ProductSerializer
from ..ProductServices.product_models import ProductModel
from ..models import User


class UserCartItemsSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_id = serializers.SlugRelatedField(
        slug_field='unique_id',              
        queryset=ProductModel.objects.all(),
        source='product',
        write_only=True
    )

    sub_total = serializers.SerializerMethodField()

    class Meta:
        model = UserCartItemsModel
        fields = ['id', 'product', 'product_id', 'quantity', 'sub_total']

    def get_sub_total(self, obj):
        return obj.product.price * obj.quantity



class UserCartSerializer(serializers.ModelSerializer):
    items = UserCartItemsSerializer(
    source='cart_items',
    many=True,
    read_only=True
)

    total_price = serializers.SerializerMethodField()
    total_items = serializers.SerializerMethodField()

    class Meta:
        model = UserCartModel
        fields = ['cart_id', 'items', 'total_price', 'total_items']

    def get_total_price(self, obj):
        total = 0
        for item in obj.cart_items.all():

            total += item.product.price * item.quantity
        return total

    def get_total_items(self, obj):
        return sum(item.quantity for item in obj.cart_items.all())




class ContactUsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactModel 
        fields = '__all__'
        
        

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"


class UserAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAddressModel
        fields = '__all__'
        
        
        


class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.name", read_only=True)
    product_image = serializers.SerializerMethodField()

    class Meta:
        model = UserOrderItemsModel
        fields = ["id", "product", "product_name", "product_image", "quantity", "price"]

    def get_product_image(self, obj):
        return obj.product.images.first().image_url if hasattr(obj.product, "images") else None



class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(source="order_items", many=True, read_only=True)
    shipping_address = UserAddressSerializer(read_only=True)

    class Meta:
        model = UserOrderModel
        fields = [
            "id",
            "order_id",
            "shipping_address",
            "total_amount",
            "discount_amount",
            "final_amount",
            "razorpay_order_id",
            "is_paid",
            "created",
            "items"
        ]



class OrderStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderStatus
        fields = ["id", "status", "is_active", "created"]