from django.urls import path
from .maxmin_views import filter_restaurants_by_price

urlpatterns = [
    path("filter/", filter_restaurants_by_price),
]
