from django.db import models
from django.conf import settings
from django.utils.text import slugify
from core.models import City   # tumhare existing City model ka import


# ✅ Product Category Model
class ProductCategory(models.Model):
    name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=200, unique=True, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)

    class Meta:
        verbose_name_plural = "Product Categories"
        ordering = ["name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug and self.name:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


# ✅ Product Model
class Product(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="products",
        blank=True,
        null=True
    )
    city = models.ForeignKey(
        City,
        on_delete=models.CASCADE,
        related_name="products",
        blank=True,
        null=True
    )
    category = models.ForeignKey(
        ProductCategory,
        on_delete=models.SET_NULL,
        related_name="products",
        blank=True,
        null=True
    )

    name = models.CharField(max_length=255, blank=True, null=True)
    slug = models.SlugField(max_length=255, blank=True, null=True)  # ❌ unique hata diya
    description = models.TextField(blank=True, null=True)

    price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    stock = models.PositiveIntegerField(default=0, blank=True, null=True)

    is_available = models.BooleanField(default=True)
    image = models.ImageField(upload_to="uploads/products/", blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)

    class Meta:
        ordering = ["-created_at"]
        unique_together = ("owner", "slug")   

    def __str__(self):
        return self.name if self.name else f"Product #{self.id}"

    def save(self, *args, **kwargs):
        if not self.slug and self.name:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1
            # ✅ ensure unique slug only per owner
            while Product.objects.filter(owner=self.owner, slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)


# --- Cart Model ---
class Cart(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name="cart", 
       
    )
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    def __str__(self):
        return f"Cart of {self.user.username if self.user else 'Guest'}"

    @property
    def subtotal(self):
        return sum(item.total_price for item in self.items.all())

    @property
    def grand_total(self):
        # Future: add shipping, tax, discount
        return self.subtotal


# --- CartItem Model ---
class CartItem(models.Model):
    cart = models.ForeignKey(
        Cart, 
        on_delete=models.CASCADE, 
        related_name="items", 
        null=True, blank=True
    )
    product = models.ForeignKey(
        Product, 
        on_delete=models.CASCADE, 
        null=True, blank=True
    )
    quantity = models.PositiveIntegerField(default=1, null=True, blank=True)

    def __str__(self):
        return f"{self.product.name if self.product else 'Deleted Product'} x {self.quantity}"
    

    @property
    def total_price(self):
        if not self.product:
            return 0
        return (self.product.discount_price or self.product.price) * self.quantity


# ===============================
# ✅ Order Model
# ===============================
class Order(models.Model):
    STATUS_CHOICES = [
        ("Pending", "Pending"),
        ("Confirmed", "Confirmed"),
        ("Shipped", "Shipped"),
        ("Delivered", "Delivered"),
        ("Cancelled", "Cancelled"),
    ]

    PAYMENT_CHOICES = [
        ("COD", "Cash on Delivery"),
    ]

    # Buyer (Tourist/User)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="orders",
        null=True,
        blank=True,
    )

    # Owner (Business Owner - jiska product order hua)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="owner_orders",
        null=True,
        blank=True,
    )

    # Shipping Details (detailed address)
    full_name = models.CharField(max_length=255, null=True, blank=True)
    phone = models.CharField(max_length=20, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    address_line1 = models.CharField(max_length=255, null=True, blank=True)
    address_line2 = models.CharField(max_length=255, null=True, blank=True)
    country = models.CharField(max_length=100, null=True, blank=True)

    payment_method = models.CharField(
        max_length=20, choices=PAYMENT_CHOICES, default="COD", null=True, blank=True
    )
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="Pending", null=True, blank=True
    )
    total_price = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    def __str__(self):
        return f"Order #{self.id} by {self.user.username if self.user else 'Guest'}"


# ===============================
# ✅ OrderItem Model
# ===============================
class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items",
        null=True,
        blank=True,
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    quantity = models.PositiveIntegerField(default=1, null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return f"{self.quantity} x {self.product.name if self.product else 'Deleted Product'}"
    





class Review(models.Model):
    product = models.ForeignKey("Product",
        related_name="reviews",
        on_delete=models.CASCADE
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="reviews",
        on_delete=models.CASCADE
    )
    rating = models.PositiveSmallIntegerField()  # 1–5 stars
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("product", "user")  # ek user ek product ka sirf ek review likh sake
        ordering = ["-created_at"]  # latest review sabse pehle

    def __str__(self):
        return f"{self.user} → {self.product} ({self.rating}⭐)"
