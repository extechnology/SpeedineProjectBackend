from django.core.files import images
from django.db import models



class CarouselImage(models.Model):
    image = models.ImageField()
    priority = models.IntegerField()

    def __str__(self):
        return str(self.image)



class ThumbNail ( models.Model):
    title= models.CharField(max_length =100)
    image = models.ImageField()
    description = models.CharField(max_length = 200)
    
    def __str__(self):
        return self.title
    
class StepTellsStory(models.Model) :
    image1=models.ImageField()
    image2=models.ImageField()
    
    def __str__(self):
        return self.image1
    
class ContactBanner(models.Model):
    image=models.ImageField()
    
    def __str__(self):
        return self.image
    
class AboutUsSectionImages(models.Model):
    banner=models.ImageField()
    image=models.ImageField()
    
    def __str__(self):
        return self.image