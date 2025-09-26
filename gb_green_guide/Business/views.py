from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend
from .models import Restaurant
from .serializers import RestaurantSerializer
from rest_framework.decorators import action
from rest_framework.response import Response
from .permissions import IsOwnerOrReadOnly, IsBusinessOwner

class RestaurantViewSet(viewsets.ModelViewSet):
    queryset = Restaurant.objects.all().order_by("-created_at")
    serializer_class = RestaurantSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ["name", "restaurant_type"]  # hotel/restaurant name search
    filterset_fields = ["city"]  # city id filter
    
    def get_permissions(self):
        """
        - List/Detail: Read only → IsAuthenticatedOrReadOnly + IsOwnerOrReadOnly already enough
        - Create: Only business_owner
        - Update/Delete: Auth + must be owner (object-level check)
        - my_restaurants: Auth required
        """
        if self.action == "create":
            return [IsBusinessOwner()]
        if self.action in ["update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsOwnerOrReadOnly()]
        if self.action == "my_restaurants":
            return [IsAuthenticated()]
        return super().get_permissions()

    def perform_create(self, serializer):
        # Owner = logged-in user
        serializer.save(owner=self.request.user)

    @action(detail=False, methods=["get"], url_path="my_restaurants")
    def my_restaurants(self, request):
        """
        Sirf current user ke restaurants (profile page ke liye).
        Paginated response if pagination enabled.
        """
        qs = self.get_queryset().filter(owner=request.user)
        page = self.paginate_queryset(qs)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)
