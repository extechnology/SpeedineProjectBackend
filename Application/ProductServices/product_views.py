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
    
    def post(self, request):
        serializer = ProductSerializer(data=request.data,context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class ProductDetailAPIView(APIView):

    def get(self, request, id):
        product = get_object_or_404(ProductModel, id=id)
        serializer = ProductSerializer(product,context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class CategoryView(APIView):

    def get(self, request):
        categories = CategoryModel.objects.all()
        serializer = CategorySerializer(categories, many=True,contaxt = {'request': request} )
        return Response(serializer.data, status=status.HTTP_200_OK  )