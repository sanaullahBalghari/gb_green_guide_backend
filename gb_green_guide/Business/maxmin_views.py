from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from .models import Restaurant
from .serializers import RestaurantSerializer

@api_view(["GET"])
def filter_restaurants_by_price(request):
    min_price = request.GET.get("min")
    max_price = request.GET.get("max")

    queryset = Restaurant.objects.all()

    if min_price:
        queryset = queryset.filter(average_room_rent__gte=min_price)

    if max_price:
        queryset = queryset.filter(average_room_rent__lte=max_price)

    serializer = RestaurantSerializer(queryset, many=True)

    return Response(
        {
            "success": True,
            "count": len(serializer.data),
            "results": serializer.data,
        },
        status=status.HTTP_200_OK
    )
