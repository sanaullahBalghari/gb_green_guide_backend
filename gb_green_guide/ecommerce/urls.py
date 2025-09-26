from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers

from .views import ProductViewSet, ProductCategoryViewSet,CartViewSet,OrderViewSet,ReviewViewSet

router = DefaultRouter()
router.register(r"products", ProductViewSet, basename="product")
# ✅ Nested router for reviews under products
products_router = routers.NestedDefaultRouter(router, "products", lookup="product")
products_router.register("reviews", ReviewViewSet, basename="product-reviews")

router.register(r"categories", ProductCategoryViewSet, basename="product-category")
router.register(r"cart", CartViewSet, basename="cart")
router.register(r"orders", OrderViewSet, basename="order")
urlpatterns = [
    path("", include(router.urls)),
    path("", include(products_router.urls)),
]
