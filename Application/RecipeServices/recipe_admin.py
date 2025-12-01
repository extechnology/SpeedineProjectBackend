import nested_admin
from django.contrib import admin
from .recipe_models import RecipeModel, RecipeStepModel


# -------------------------------
# Inline for Recipe Steps
# -------------------------------
class RecipeStepInline(nested_admin.NestedStackedInline):
    model = RecipeStepModel
    extra = 1
    fk_name = 'recipe'

# -------------------------------
# MAIN RECIPE ADMIN
# -------------------------------
@admin.register(RecipeModel)
class RecipeAdmin(nested_admin.NestedModelAdmin):
    list_display = ('title', 'subtitle', 'ingredients', 'image')
    search_fields = ('title', 'description')


    inlines = [
        RecipeStepInline,
    ]