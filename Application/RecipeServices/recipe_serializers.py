from rest_framework.serializers import ModelSerializer
from .recipe_models import RecipeModel, RecipeStepModel



class RecipeStepSerializer(ModelSerializer):
    class Meta:
        model = RecipeStepModel
        fields = ['id', 'step_number', 'step_title', 'instruction', 'description']  
        
class RecipeSerializer(ModelSerializer):
    steps = RecipeStepSerializer(many=True, read_only=True)
    
    class Meta:
        model = RecipeModel
        fields = ['id', 'title', 'description', 'video_url', 'ingredients', 'image', 'steps']