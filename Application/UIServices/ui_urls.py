from django.urls import path
from .ui_views import *

urlpatterns = [
    path('carousel-image/', CarouselImageListCreateView.as_view()),
    path('thumb-nail/', ThumbNailListCreateView.as_view()),
    path('step-tells-story/', StepTellsStoryListCreateView.as_view()),
    path('contact-banner/', ContactBannerListCreateView.as_view()),
    path('about-us-section-images/', AboutUsSectionImagesListCreateView.as_view()),
    path('about-us-customer-review/', AboutUsCustomerReviewListCreateView.as_view()),
]