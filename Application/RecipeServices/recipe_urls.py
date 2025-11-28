from .recipe_views import RecipeListAPIView, RecipeDetailAPIView
from django.urls import path

urlpatterns = [
    path('recipe-list/', RecipeListAPIView.as_view(), name='recipe-list'),
    path('recipes/<int:id>/', RecipeDetailAPIView.as_view(), name='recipe-detail'),
]

