from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework import viewsets, filters,permissions
from django_filters.rest_framework import DjangoFilterBackend
from .models import City, Region, Event,TouristPlace,TouristPlaceImage
from .serializers import CitySerializer, RegionSerializer, EventSerializer, TouristPlaceSerializer,TouristPlaceImageSerializer
from django.utils import timezone
from rest_framework.response import Response
from django.db.models import Count

class CityViewSet(viewsets.ModelViewSet):
    print('yes city is called')
    queryset = City.objects.annotate(tourist_places_count=Count('tourist_places')).order_by('-created_at')
    serializer_class = CitySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['region__name']
    search_fields = ['name']

    def list(self, request, *args, **kwargs):
        """
        Override list method to handle 'fetch all cities' requests
        """
        # ✅ Check if frontend wants ALL cities (no pagination)
        all_cities = request.query_params.get('all')
        no_pagination = request.query_params.get('no_pagination')
        limit = request.query_params.get('limit')
        
        if all_cities == 'true' or no_pagination == 'true' or limit == 'all':
            # ✅ Return ALL cities without pagination
            queryset = self.filter_queryset(self.get_queryset())
            serializer = self.get_serializer(queryset, many=True)
            
            print(f"🏙️ Returning ALL cities: {queryset.count()}")
            
            return Response(serializer.data)
        
        # ✅ Default paginated response for other cases
        return super().list(request, *args, **kwargs)

class RegionViewSet(viewsets.ModelViewSet):
    print('yes called here')
    queryset = Region.objects.all()
    serializer_class = RegionSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    def list(self, request, *args, **kwargs):
        """
        Override list method to handle 'fetch all regions' requests
        """
        # ✅ Check if frontend wants ALL regions (no pagination)
        all_regions = request.query_params.get('all')
        no_pagination = request.query_params.get('no_pagination')
        limit = request.query_params.get('limit')
        
        if all_regions == 'true' or no_pagination == 'true' or limit == 'all':
            # ✅ Return ALL regions without pagination
            queryset = self.filter_queryset(self.get_queryset())
            serializer = self.get_serializer(queryset, many=True)
            
            print(f"🗺️ Returning ALL regions: {queryset.count()}")
            
            return Response(serializer.data)
        
        # ✅ Default paginated response for other cases
        return super().list(request, *args, **kwargs)


# evnts viewset 

class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        # Allow read-only access for any user
        if request.method in permissions.SAFE_METHODS:
            return True
        # Only allow admin users to create/update/delete
        return request.user and request.user.is_staff


class EventViewSet(viewsets.ModelViewSet):
    serializer_class = EventSerializer
    permission_classes = [IsAdminOrReadOnly]
    # permission_classes = [IsAdminOrReadOnly,IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['type', 'city']
    search_fields = ['title', 'description', 'location']

    def get_queryset(self):
        queryset = Event.objects.all().order_by('-date')

        upcoming = self.request.query_params.get('upcoming')
        limit = self.request.query_params.get('limit')

        if upcoming == 'true':
            queryset = queryset.filter(date__gt=timezone.now()).order_by('date')

        if limit and limit.isdigit():
            queryset = queryset[:int(limit)]

        return queryset



# Update your views.py

class TouristPlaceViewSet(viewsets.ModelViewSet):
    serializer_class = TouristPlaceSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'location_inside_city', 'short_description']

    def get_queryset(self):
        """Optimize queries by prefetching related images"""
        return TouristPlace.objects.select_related('city').prefetch_related('extra_images')

    def get_serializer_context(self):
        """Pass request context to serializer for building full URLs"""
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def list(self, request, *args, **kwargs):
        city_id = request.query_params.get('city_id')
        queryset = self.get_queryset()

        if city_id:
            queryset = queryset.filter(city_id=city_id)

        queryset = self.filter_queryset(queryset)

        if not queryset.exists():
            return Response({
                "count": 0,
                "message": "No tourist places found in this city",
                "results": []
            })

        # Pass request context to serializer
        serializer = self.get_serializer(queryset, many=True, context={'request': request})
        return Response({
            "count": queryset.count(),
            "message": "Tourist places retrieved successfully",
            "results": serializer.data
        })




# # ✅ Tourist Places
# class TouristPlaceViewSet(viewsets.ModelViewSet):
#     queryset = TouristPlace.objects.all()
#     serializer_class = TouristPlaceSerializer
#     permission_classes = [IsAuthenticatedOrReadOnly]
#     filter_backends = [filters.SearchFilter]
#     search_fields = ['name', 'location_inside_city', 'short_description']

#     def list(self, request, *args, **kwargs):
#         city_id = request.query_params.get('city_id')
#         queryset = self.queryset

#         if city_id:
#             queryset = queryset.filter(city_id=city_id)

#         queryset = self.filter_queryset(queryset)

#         if not queryset.exists():
#             return Response({
#                 "count": 0,
#                 "message": "No tourist places found in this city",
#                 "results": []
#             })

#         serializer = self.get_serializer(queryset, many=True)
#         return Response({
#             "count": queryset.count(),
#             "message": "Tourist places retrieved successfully",
#             "results": serializer.data
#         })


# # ✅ TouristPlace Images
# class TouristPlaceImageViewSet(viewsets.ModelViewSet):
#     queryset = TouristPlaceImage.objects.all()
#     serializer_class = TouristPlaceImageSerializer
#     permission_classes = [IsAuthenticatedOrReadOnly]

#     filter_backends = [DjangoFilterBackend]
#     filterset_fields = ['tourist_place']  # filter by tourist place id







# class TouristPlaceViewSet(viewsets.ModelViewSet):
#     queryset = TouristPlace.objects.all()
#     serializer_class = TouristPlaceSerializer
#     http_method_names = ['get']  # Only GET allowed
#     filter_backends = [filters.SearchFilter]
#     search_fields = ['name', 'location_inside_city', 'short_description']  # Search support

#     def list(self, request, *args, **kwargs):
#         city_id = request.query_params.get('city_id', None)
#         queryset = self.queryset

#         if city_id:
#             queryset = queryset.filter(city_id=city_id)

#         # Search filter from DRF
#         queryset = self.filter_queryset(queryset)

#         if not queryset.exists():
#             return Response({
#                 "count": 0,
#                 "message": "No tourist places found in this city",
#                 "results": []
#             })

#         serializer = self.get_serializer(queryset, many=True)
#         return Response({
#             "count": queryset.count(),
#             "message": "Tourist places retrieved successfully",
#             "results": serializer.data
#         })

