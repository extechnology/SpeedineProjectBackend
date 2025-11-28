from rest_framework.serializers import ModelSerializer
from .recipe_models import RecipeModel, RecipeStepModel



class RecipeStepSerializer(ModelSerializer):
    class Meta:
        model = RecipeStepModel
        fields = ['id', 'step_number', 'step_title', 'instruction']  
        
class RecipeSerializer(ModelSerializer):
    steps = RecipeStepSerializer(many=True, read_only=True)
    
    class Meta:
        model = RecipeModel
        fields = ['id', 'title',"description","subtitle", 'video_url', 'ingredients', 'image', 'steps',"is_main","is_featured"]