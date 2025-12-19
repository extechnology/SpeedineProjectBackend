from Application.UserServices.user_models import (
    UserOrderModel,
    UserOrderItemsModel,
    OrderStatus,
    UserAddressModel,
    User
)
from rest_framework import serializers
from Application.ProductServices.product_models import ProductModel

class DashboardProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductModel
        fields = '__all__'

class DashboardUserAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAddressModel
        fields = '__all__'

class DashboardUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email']

class DashboardOrderStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderStatus
        fields = '__all__'


class DashboardOrderItemsSerializer(serializers.ModelSerializer):
    product = serializers.CharField(source="product.name", read_only=True)
    class Meta:
        model = UserOrderItemsModel
        fields = '__all__'


class DashboardOrderSerializer(serializers.ModelSerializer):
    order_items = DashboardOrderItemsSerializer(many=True, read_only=True)
    order_status = DashboardOrderStatusSerializer(many=True, read_only=True)
    shipping_address = DashboardUserAddressSerializer(read_only=True)
    user = DashboardUserSerializer(read_only=True)

    class Meta:
        model = UserOrderModel
        fields = '_all_'

