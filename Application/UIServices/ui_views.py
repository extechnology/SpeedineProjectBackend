from .ui_models import *
from .ui_serializers import *
from rest_framework import generics


class CarouselImageListCreateView(generics.ListCreateAPIView):
    queryset = CarouselImage.objects.all().order_by('priority')
    serializer_class = CarouselImageSerializer
    
class ThumbNailListCreateView(generics.ListCreateAPIView):
    queryset = ThumbNail.objects.all()
    serializer_class = ThumbNailSerializer
    
class StepTellsStoryListCreateView(generics.ListCreateAPIView):
    queryset = StepTellsStory.objects.all()
    serializer_class = StepTellsStorySerializer
    
class ContactBannerListCreateView(generics.ListCreateAPIView):
    queryset = ContactBanner.objects.all()
    serializer_class = ContactBannerSerializer
    
class AboutUsSectionImagesListCreateView(generics.ListCreateAPIView):   
    queryset = AboutUsSectionImages.objects.all()
    serializer_class = AboutUsSectionImagesSerializer

class AboutUsCustomerReviewListCreateView(generics.ListCreateAPIView):   
    queryset = AboutUsCustomerReview.objects.all()
    serializer_class = AboutUsCustomerReviewSerializer