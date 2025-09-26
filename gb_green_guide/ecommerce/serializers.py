from rest_framework import serializers
from .models import Product, ProductCategory, Cart, CartItem, Order, OrderItem,Review
from core.models import City
from core.serializers import CitySerializer 

# ✅ Category Serializer
class ProductCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductCategory
        fields = ["id", "name", "slug"]

# ✅ Product Serializer
class ProductSerializer(serializers.ModelSerializer):
    owner = serializers.StringRelatedField(read_only=True)
    category = ProductCategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=ProductCategory.objects.all(),
        source="category",
        write_only=True
    )

    city = CitySerializer(read_only=True)
    city_id = serializers.PrimaryKeyRelatedField(
        queryset=City.objects.all(),
        source="city",
        write_only=True
    )

    discount_percentage = serializers.SerializerMethodField()
    effective_price = serializers.SerializerMethodField()
    reviews_count = serializers.IntegerField(source="reviews.count", read_only=True)

    class Meta:
        model = Product
        fields = [
            "id", "owner", "city", "city_id", "category", "category_id",
            "name", "slug", "description",
            "price", "discount_price", "effective_price", "discount_percentage",
            "stock", "is_available", "image",
            "created_at", "reviews_count","updated_at"
        ]
        read_only_fields = ["slug", "created_at", "updated_at"]

    def get_discount_percentage(self, obj):
        if obj.price and obj.discount_price:
            try:
                return round(((obj.price - obj.discount_price) / obj.price) * 100)
            except ZeroDivisionError:
                return 0
        return 0

    def get_effective_price(self, obj):
        return obj.discount_price if obj.discount_price else obj.price

# ✅ CartItem Serializer
class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(),
        source="product",
        write_only=True
    )
    total_price = serializers.ReadOnlyField()

    class Meta:
        model = CartItem
        fields = ["id", "product", "product_id", "quantity", "total_price"]

# ✅ Cart Serializer
class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    subtotal = serializers.ReadOnlyField()
    grand_total = serializers.ReadOnlyField()

    class Meta:
        model = Cart
        fields = ["id", "user", "items", "subtotal", "grand_total", "created_at", "updated_at"]
        read_only_fields = ["user", "subtotal", "grand_total", "created_at", "updated_at"]


# ✅ OrderItem Serializer
class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_image = serializers.ImageField(source='product.image', read_only=True, allow_null=True)

    class Meta:
        model = OrderItem
        fields = ["id", "product", "product_name","product_image", "quantity", "price", "subtotal"]
        read_only_fields = ["product_name","product_image", "subtotal"]

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    buyer = serializers.StringRelatedField(source='user', read_only=True)
    seller = serializers.StringRelatedField(source='owner', read_only=True)
    shipping_address = serializers.SerializerMethodField()
    total_amount = serializers.DecimalField(source='total_price', max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = Order
        fields = [
            "id",
            "buyer",
            "seller",
            "full_name",          # ✅ include customer name
            "email",              # ✅ include email
            "phone",
            "address_line1",
            "address_line2",
            "city",
            "country",
            "shipping_address",
            "status",
            "payment_method",
            "total_amount",
            "created_at",
            "updated_at",
            "items",
        ]
        read_only_fields = [
            "buyer",
            "seller",
            "status",
            "payment_method",
            "total_amount",
            "created_at",
            "updated_at"
        ]

    def get_shipping_address(self, obj):
        address_parts = [
            obj.full_name,
            obj.address_line1,
            obj.address_line2,
            obj.city,
            obj.country
        ]
        return ", ".join([part for part in address_parts if part])



class ReviewSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    

    class Meta:
        model = Review
        fields = ["id", "product", "user", "rating", "comment", "created_at"]
        read_only_fields = ["id", "user", "product", "created_at"]