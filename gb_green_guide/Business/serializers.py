from rest_framework import serializers
from .models import Restaurant


class RestaurantSerializer(serializers.ModelSerializer):
    whatsapp_link = serializers.SerializerMethodField()

    class Meta:
        model = Restaurant
        fields = [
            "id",
            "owner",  # sirf owner id show hoga
            "city",
            "name",
            "location_inside_city",
            "restaurant_type",
            "is_active",
            "description",
            "room_available",
            "average_room_rent", 
            "contacts_and_hours",
            "amenities",
            "get_direction",
            "whatsapp_number",
            "whatsapp_link",
            "image",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["owner", "created_at", "updated_at"]

    def get_whatsapp_link(self, obj):
        return obj.whatsapp_link()
