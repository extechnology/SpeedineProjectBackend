from django.db import models
import uuid



class Category(models.Model):
    unique_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
    priority = models.PositiveIntegerField(default=0)
    image = models.ImageField(upload_to='category_images/', blank=True, null=True)
    display_name1= models.CharField(max_length=255, blank=True, null=True)
    display_name2= models.CharField(max_length=255, blank=True, null=True)
    
    is_available = models.BooleanField(default=True)
    special_tags = models.CharField(max_length=255, blank=True, null=True)
    special_offer = models.CharField(max_length=255, blank=True, null=True)
    
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.name
 