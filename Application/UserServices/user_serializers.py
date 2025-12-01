from rest_framework import serializers
from .user_models import UserCartModel, UserCartItemsModel,ContactModel,UserAddressModel
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
    items = UserCartItemsSerializer(source='usercartitemsmodel_set', many=True, read_only=True)
    total_price = serializers.SerializerMethodField()
    total_items = serializers.SerializerMethodField()

    class Meta:
        model = UserCartModel
        fields = ['cart_id', 'items', 'total_price', 'total_items']

    def get_total_price(self, obj):
        total = 0
        for item in obj.usercartitemsmodel_set.all():
            total += item.product.price * item.quantity
        return total

    def get_total_items(self, obj):
        return sum(item.quantity for item in obj.usercartitemsmodel_set.all())



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