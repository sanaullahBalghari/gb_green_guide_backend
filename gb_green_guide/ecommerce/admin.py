from django.contrib import admin
from .models import ProductCategory, Product, Cart, CartItem,Order, OrderItem,Review




# ===============================
# ✅ ProductCategory Admin
# ===============================
@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "slug", "created_at", "updated_at")
    search_fields = ("name", "slug")
    ordering = ("name",)
    prepopulated_fields = {"slug": ("name",)}


# ===============================
# ✅ Product Admin
# ===============================
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "owner",
        "category",
        "city",
        "price",
        "discount_price",
        "stock",
        "is_available",
        "created_at",
    )
    list_filter = ("is_available", "category", "city", "owner")
    search_fields = ("name", "slug", "description", "owner__username")
    prepopulated_fields = {"slug": ("name",)}
    ordering = ("-created_at",)
    readonly_fields = ("created_at", "updated_at")

    fieldsets = (
        ("Basic Info", {
            "fields": ("owner", "city", "category", "name", "slug", "description")
        }),
        ("Pricing & Stock", {
            "fields": ("price", "discount_price", "stock", "is_available")
        }),
        ("Media", {
            "fields": ("image",)
        }),
        ("Timestamps", {
            "fields": ("created_at", "updated_at")
        }),
    )


# ===============================
# ✅ CartItem Inline for Cart
# ===============================
class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 1
    readonly_fields = ("total_price",)


# ===============================
# ✅ Cart Admin
# ===============================
@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "grand_total", "created_at", "updated_at")
    search_fields = ("user__username",)
    ordering = ("-created_at",)
    readonly_fields = ("created_at", "updated_at", "grand_total")

    # Inline show cart items inside cart
    inlines = [CartItemInline]


# ===============================
# ✅ CartItem Admin (standalone)
# ===============================
@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ("id", "cart", "product", "quantity", "total_price")
    search_fields = ("product__name", "cart__user__username")
    ordering = ("-id",)
    readonly_fields = ("total_price",)





# ✅ Inline Order Items (Order ke andar dikhaye)
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("product", "quantity", "price", "subtotal")


# ✅ Order Admin
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "owner",
        "status",
        "payment_method",
        "total_price",
        "created_at",
    )
    list_filter = ("status", "payment_method", "created_at")
    search_fields = ("user__username", "owner__username", "id")
    inlines = [OrderItemInline]
    readonly_fields = ("created_at", "updated_at")


# ✅ OrderItem Admin (standalone view bhi rahe)
@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ("id", "order", "product", "quantity", "price", "subtotal")
    search_fields = ("order__id", "product__name")





# ===============================
# ✅ Review Admin
# ===============================
@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("id", "product", "user", "rating", "created_at")
    list_filter = ("rating", "created_at")
    search_fields = ("product__name", "user__username", "comment")
    ordering = ("-created_at",)
    readonly_fields = ("created_at",)

    fieldsets = (
        ("Review Info", {
            "fields": ("product", "user", "rating", "comment")
        }),
        ("Timestamps", {
            "fields": ("created_at", "updated_at")
        }),
    )
