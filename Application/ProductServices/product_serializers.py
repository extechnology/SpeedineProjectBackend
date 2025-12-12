from rest_framework import serializers
from .product_models import *


class IngredientsSerializer(serializers.ModelSerializer):
    class Meta:
        model = IngredientsModel
        fields = '__all__'

class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImageModel
        fields = '__all__'

class ProductPrepareStepsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductPrepareStepsModel
        fields = '__all__'

class ProductPrepareSerializer(serializers.ModelSerializer):
    steps = ProductPrepareStepsSerializer(many=True, read_only=True)

    class Meta:
        model = ProductPrepareModel
        fields = '__all__'

class CustomerReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerReviewModel
        fields = '__all__'

class ProductWeightSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductWeightModel
        fields = '__all__'

class ProductSerializer(serializers.ModelSerializer):
    ingredients = IngredientsSerializer(many=True, read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)
    preparations = ProductPrepareSerializer(many=True, read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    category_id = serializers.CharField(source='category.unique_id', read_only=True)
    weights = ProductWeightSerializer(many=True, read_only=True)
    class Meta:
        model = ProductModel
        fields = [
            'unique_id', 'name', 'description',
            'category', 'category_name', 
            'is_available', 'prepare_time',
            'difficulty_level', 'rating', 'created_at',
            'updated_at', 'ingredients', 'images', 'preparations','category_id','weights'
        ]
