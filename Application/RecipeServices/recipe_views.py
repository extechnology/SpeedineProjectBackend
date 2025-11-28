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
    
class RecipeDetailAPIView(APIView):

    def get(self, request, id):
        recipe = get_object_or_404(RecipeModel, id=id)
        serializer = RecipeSerializer(recipe, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)