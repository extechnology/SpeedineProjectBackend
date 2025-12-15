from Application.UserServices.user_models import (
    UserOrderModel,
    UserOrderItemsModel,
    OrderStatus,
    UserAddressModel,
    User
)
from rest_framework import serializers



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
    class Meta:
        model = UserOrderModel
        fields = '__all__'


