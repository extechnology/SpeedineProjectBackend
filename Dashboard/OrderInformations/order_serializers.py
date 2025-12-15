from Application.UserServices.user_models import (
    UserOrderModel,
    UserOrderItemsModel,
    OrderStatus,
    UserAddressModel,
    User
)
from rest_framework import serializers

class DashboardUserAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAddressModel
        fields = '__all__'

class DashboardUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

class DashboardOrderStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderStatus
        fields = '__all__'


class DashboardOrderItemsSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserOrderItemsModel
        fields = '__all__'


class DashboardOrderSerializer(serializers.ModelSerializer):
    order_items = DashboardOrderItemsSerializer(many=True, read_only=True)
    order_status = DashboardOrderStatusSerializer(many=True, read_only=True)
    user_address = DashboardUserAddressSerializer(many=True, read_only=True)
    user = DashboardUserSerializer(many=True, read_only=True)
    class Meta:
        model = UserOrderModel
        fields = '__all__'


