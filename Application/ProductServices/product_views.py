from .product_models import *
from .product_serializers import *
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404



class ProductListAPIView(APIView):

    def get(self, request):
        products = ProductModel.objects.all().order_by('-created_at')
        serializer = ProductSerializer(products, many=True,context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)



class ProductDetailAPIView(APIView):

    def get(self, request, pk):
        product = get_object_or_404(ProductModel, pk=pk)
        serializer = ProductSerializer(product,context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)
