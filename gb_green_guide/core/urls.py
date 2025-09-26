from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CityViewSet, RegionViewSet, EventViewSet, TouristPlaceViewSet

router = DefaultRouter()
router.register(r'cities', CityViewSet, basename='cities')
router.register(r'regions', RegionViewSet, basename='regions')
router.register(r'events', EventViewSet, basename='events')
router.register(r'tourist-places', TouristPlaceViewSet, basename='touristplace')

urlpatterns = [
    path('', include(router.urls)),
]








