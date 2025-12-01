from .category_models import *
from .category_serializers import *
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

class CategoryView(APIView):

    def get(self, request):
        categories = Category.objects.all()
        serializer = CategorySerializer(categories, many=True,context = {'request': request} )
        return Response(serializer.data, status=status.HTTP_200_OK  )