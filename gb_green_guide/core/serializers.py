from rest_framework import serializers
from .models import City, Region, Event,TouristPlace,TouristPlaceImage

class RegionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Region
        fields = ['id', 'name']


class CitySerializer(serializers.ModelSerializer):
    tourist_places_count = serializers.IntegerField(read_only=True)
  

    region = RegionSerializer(read_only=True)
    region_id = serializers.PrimaryKeyRelatedField(
        queryset=Region.objects.all(), source='region', write_only=True
    )
    highlights_list = serializers.SerializerMethodField()

    class Meta:
        model = City
        fields = [
            'id', 'name', 'region', 'region_id',
            'description', 'image', 'highlights',
            'highlights_list', 'altitude', 'best_time_to_visit',
            'created_at', 'updated_at','tourist_places_count',
        ]

    def get_highlights_list(self, obj):
        return obj.get_highlights_list()
    
 



class EventSerializer(serializers.ModelSerializer):
    city = serializers.SerializerMethodField()
    city_id = serializers.PrimaryKeyRelatedField(
        queryset=City.objects.all(), source='city', write_only=True
    )

    class Meta:
        model = Event
        fields = [
            'id', 'title', 'description', 'image', 'date', 'location',
            'type', 'event_calendar', 'city', 'city_id',
            'created_at', 'updated_at'
        ]

    def get_city(self, obj):
        return {
            "id": obj.city.id,
            "name": obj.city.name,
        }
    


# Update your serializers.py

class TouristPlaceImageSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    
    class Meta:
        model = TouristPlaceImage
        fields = ['id', 'image']
    
    def get_image(self, obj):
        """Return full URL for image"""
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
            else:
                # Fallback if no request context
                return f"http://localhost:8000{obj.image.url}"
        return None


class TouristPlaceSerializer(serializers.ModelSerializer):
    city_name = serializers.CharField(source='city.name', read_only=True)
    city_id = serializers.PrimaryKeyRelatedField(
        queryset=City.objects.all(), source='city', write_only=True
    )

    # Fixed: Use correct related_name from your model
    extra_images = TouristPlaceImageSerializer(many=True, read_only=True)
    
    # Add a computed field for all images combined with full URLs
    all_images = serializers.SerializerMethodField()
    
    # Fix main image URL too
    image = serializers.SerializerMethodField()

    class Meta:
        model = TouristPlace
        fields = [
            'id',
            'name',
            'city_name',
            'city_id',
            'image',  # main image with full URL
            'extra_images',  # related images with full URLs
            'all_images',  # computed field with all images
            'short_description',
            'location_inside_city',
            'distance_from_main_city',
            'map_url'
        ]
    
    def get_image(self, obj):
        """Return full URL for main image"""
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
            else:
                # Fallback if no request context
                return f"http://localhost:8000{obj.image.url}"
        return None
    
    def get_all_images(self, obj):
        """Combine main image + extra images into single list with full URLs"""
        all_imgs = []
        request = self.context.get('request')
        
        # Add main image first
        if obj.image:
            if request:
                all_imgs.append(request.build_absolute_uri(obj.image.url))
            else:
                all_imgs.append(f"http://localhost:8000{obj.image.url}")
        
        # Add extra images
        for extra_img in obj.extra_images.all():
            if extra_img.image:
                if request:
                    all_imgs.append(request.build_absolute_uri(extra_img.image.url))
                else:
                    all_imgs.append(f"http://localhost:8000{extra_img.image.url}")
        
        return all_imgs




# class TouristPlaceImageSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = TouristPlaceImage
#         fields = ['id', 'image']


# class TouristPlaceSerializer(serializers.ModelSerializer):
#     city_name = serializers.CharField(source='city.name', read_only=True)
#     city_id = serializers.PrimaryKeyRelatedField(
#         queryset=City.objects.all(), source='city', write_only=True
#     )

#     # ✅ Nested images
#     images = TouristPlaceImageSerializer(many=True, read_only=True)

#     class Meta:
#         model = TouristPlace
#         fields = [
#             'id',
#             'name',
#             'city_name',
#             'city_id',
#             'image',  # ✅ main single image (already in model)
#             'images',  # ✅ related multiple images
#             'short_description',
#             'location_inside_city',
#             'distance_from_main_city',
#             'map_url'
#         ]
