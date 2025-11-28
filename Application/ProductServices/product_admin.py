from django.contrib import admin
from .product_models import ProductModel, ProductImageModel, ProductPrepareModel, ProductPrepareStepsModel, IngredientsModel, CustomerReviewModel
import nested_admin


# -------------------------------
# Inline for Prepare Steps
# -------------------------------
class ProductPrepareStepsInline(nested_admin.NestedStackedInline):
    model = ProductPrepareStepsModel
    extra = 1
    fk_name = 'prepare'


# -------------------------------
# Inline for Preparation Overview
# -------------------------------
class ProductPrepareInline(nested_admin.NestedStackedInline):
    model = ProductPrepareModel
    extra = 1
    fk_name = 'product'
    inlines = [ProductPrepareStepsInline]


# -------------------------------
# Inline for Ingredients
# -------------------------------
class IngredientsInline(nested_admin.NestedStackedInline):
    model = IngredientsModel
    extra = 1
    fk_name = 'product'


# -------------------------------
# Inline for Product Images
# -------------------------------
class ProductImageInline(nested_admin.NestedStackedInline):
    model = ProductImageModel
    extra = 1
    fk_name = 'product'


# -------------------------------
# MAIN PRODUCT ADMIN
# -------------------------------
@admin.register(ProductModel)
class ProductAdmin(nested_admin.NestedModelAdmin):
    list_display = ('name', 'price', 'is_available', 'rating')
    search_fields = ('name',)
    list_filter = ('category', 'is_available', 'is_offered')

    inlines = [
        IngredientsInline,
        ProductImageInline,
        ProductPrepareInline,
    ]


# -------------------------------
# Customer Review Admin
# -------------------------------
@admin.register(CustomerReviewModel)
class CustomerReviewAdmin(admin.ModelAdmin):
    list_display = ('name', 'rating', 'created_at')
    search_fields = ('name',)
    list_filter = ('rating', 'created_at')