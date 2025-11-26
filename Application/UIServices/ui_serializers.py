from .ui_models import CarouselImage, ThumbNail, StepTellsStory, ContactBanner, AboutUsSectionImages
from rest_framework import serializers


class CarouselImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = CarouselImage
        fields = '__all__'
        
class ThumbNailSerializer(serializers.ModelSerializer):
    class Meta:
        model = ThumbNail
        fields = '__all__'  
        
class StepTellsStorySerializer(serializers.ModelSerializer):
    class Meta:
        model = StepTellsStory
        fields = '__all__'
        
class ContactBannerSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactBanner
        fields = '__all__'
        
class AboutUsSectionImagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = AboutUsSectionImages
        fields = '__all__'