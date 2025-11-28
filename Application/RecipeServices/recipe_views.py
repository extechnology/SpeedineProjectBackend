from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from django.shortcuts import get_object_or_404
from .recipe_models import RecipeModel  
from .recipe_serializers import RecipeSerializer

class RecipeListAPIView(APIView):

    def get(self, request):
        recipes = RecipeModel.objects.all().order_by('-id')
        serializer = RecipeSerializer(recipes, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self, request):
        serializer = RecipeSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class RecipeDetailAPIView(APIView):

    def get(self, request, id):
        recipe = get_object_or_404(RecipeModel, id=id)
        serializer = RecipeSerializer(recipe, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)