from django.db import models
from ..CategoryServices.category_models import Category
import uuid

class RecipeModel(models.Model):
    title = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
    video_url = models.URLField(blank=True, null=True)
    ingredients = models.TextField()
    image = models.ImageField(upload_to='recipe_images/')
    is_featured = models.BooleanField(default=False)
    is_main = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if self.is_main:
            RecipeModel.objects.exclude(id=self.id).update(is_main=False)

        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    
class RecipeStepModel(models.Model):
    recipe = models.ForeignKey(RecipeModel, on_delete=models.CASCADE, related_name='steps')
    description = models.TextField()
    step_number = models.PositiveIntegerField()
    step_title = models.CharField(max_length=255)
    instruction = models.TextField()
    
    class Meta:
        unique_together = ('recipe', 'step_number')
        ordering = ['step_number']
    
    def __str__(self):
        return f"Step {self.step_number} for {self.recipe.title}"