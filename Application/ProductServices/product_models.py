from django.db import models
from Application.CategoryServices.category_models import Category
import uuid


 
class ProductModel(models.Model):
    unique_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True) 
    price = models.DecimalField(max_digits=10, decimal_places=2)
    old_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    weight = models.CharField(max_length=100, blank=True, null=True)

    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    
    is_offered = models.BooleanField(default=False)
    offer_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    
    is_available = models.BooleanField(default=True)
    special_tags = models.CharField(max_length=255, blank=True, null=True)
    special_offer = models.CharField(max_length=255, blank=True, null=True)
    
    prepare_time = models.PositiveIntegerField(help_text="Preparation time in minutes", default=0)
    DIFFICULTY_CHOICES = [
        ('Easy', 'Easy'),
        ('Medium', 'Medium'),
        ('Hard', 'Hard'),
    ]
    difficulty_level = models.CharField(max_length=100, choices=DIFFICULTY_CHOICES, default='Easy')
    
    serving_count = models.CharField(max_length=100, blank=True, null=True)
    
    rating = models.FloatField(default=0.0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class ProductWeightModel(models.Model):
    product = models.ForeignKey(ProductModel, on_delete=models.CASCADE, related_name='weights')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    old_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    weight = models.CharField(max_length=100, blank=True, null=True)

    is_offered = models.BooleanField(default=False)
    offer_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    is_available = models.BooleanField(default=True)
    special_tags = models.CharField(max_length=255, blank=True, null=True)
    special_offer = models.CharField(max_length=255, blank=True, null=True)

    serving_count = models.CharField(max_length=100, blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.weight} ({self.product.name})"


class IngredientsModel(models.Model):
    product = models.ForeignKey(ProductModel, on_delete=models.CASCADE, related_name='ingredients')
    name = models.CharField(max_length=255)
    quantity = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.name} ({self.product.name})"


class ProductImageModel(models.Model):
    product = models.ForeignKey(ProductModel, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='product_images/')

    def __str__(self):
        return f"Image for {self.product.name}"


class ProductPrepareModel(models.Model):
    product = models.ForeignKey(ProductModel, on_delete=models.CASCADE, related_name='preparations')
    overview = models.TextField()
    
    def __str__(self):
        return f"Preparation for {self.product.name}"

class ProductPrepareStepsModel(models.Model):
    prepare = models.ForeignKey(ProductPrepareModel, on_delete=models.CASCADE, related_name='steps')
    step_number = models.PositiveIntegerField()
    heading = models.CharField(max_length=255)
    details = models.TextField()
    
    def __str__(self):
        return f"Step {self.prepare.product.name}"



class CustomerReviewModel(models.Model):
    name = models.CharField(max_length=255)
    rating = models.PositiveIntegerField()
    description = models.TextField()
    image = models.ImageField(upload_to='customer_reviews/', blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Review by {self.name} - Rating: {self.rating}"

