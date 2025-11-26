from django.core.files import images
from django.db import models



class CarouselImage(models.Model):
    image = models.ImageField()
    priority = models.IntegerField()

    created = models.DateTimeField(auto_now_add=True,blank=True,null=True)
    updated = models.DateTimeField(auto_now=True,blank=True,null=True)

    def __str__(self):
        return str(self.image)



class ThumbNail ( models.Model):
    title= models.CharField(max_length =100)
    image = models.ImageField()
    description = models.CharField(max_length = 200)
    
    created = models.DateTimeField(auto_now_add=True,blank=True,null=True)
    updated = models.DateTimeField(auto_now=True,blank=True,null=True)
    
    def __str__(self):
        return self.title
    
class StepTellsStory(models.Model) :
    image1=models.ImageField()
    image2=models.ImageField()
    
    created = models.DateTimeField(auto_now_add=True,blank=True,null=True)
    updated = models.DateTimeField(auto_now=True,blank=True,null=True)
        
    def __str__(self):
        return self.image1
    
class ContactBanner(models.Model):
    image=models.ImageField()
    
    created = models.DateTimeField(auto_now_add=True,blank=True,null=True)
    updated = models.DateTimeField(auto_now=True,blank=True,null=True)
    
    def __str__(self):
        return self.image
    
class AboutUsSectionImages(models.Model):
    banner=models.ImageField()
    image=models.ImageField()
    
    created = models.DateTimeField(auto_now_add=True,blank=True,null=True)
    updated = models.DateTimeField(auto_now=True,blank=True,null=True)
    
    def __str__(self):
        return self.image


class AboutUsCustomerReview(models.Model):
    name = models.CharField(max_length=255)
    rating = models.PositiveIntegerField()
    description = models.TextField()
    image = models.ImageField(upload_to='customer_reviews/', blank=True, null=True)
    
    created = models.DateTimeField(auto_now_add=True,blank=True,null=True)
    updated = models.DateTimeField(auto_now=True,blank=True,null=True)
    
    def __str__(self):
        return self.name