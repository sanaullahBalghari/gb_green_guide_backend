# views.py (corrected version)
from rest_framework import viewsets, filters, status,permissions
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend
from django_filters import rest_framework as django_filters
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Product, ProductCategory, Cart, CartItem, Order, OrderItem,Review
from .serializers import ProductSerializer, ProductCategorySerializer, CartSerializer, CartItemSerializer, OrderSerializer,ReviewSerializer
from Business.permissions import IsOwnerOrReadOnly, IsBusinessOwner
from django.db.models import F, ExpressionWrapper, DecimalField

# 📩 Email
from django.core.mail import send_mail
from django.conf import settings


# 🔹 Product Filters
class ProductFilter(django_filters.FilterSet):
    min_price = django_filters.NumberFilter(field_name="price", lookup_expr="gte")
    max_price = django_filters.NumberFilter(field_name="price", lookup_expr="lte")
    min_discount = django_filters.NumberFilter(method="filter_min_discount")

    class Meta:
        model = Product
        fields = ["city", "category", "is_available"]

    def filter_min_discount(self, queryset, name, value):
        queryset = queryset.annotate(
            discount_percent=ExpressionWrapper(
                (F("price") - F("discount_price")) * 100.0 / F("price"),
                output_field=DecimalField()
            )
        )
        return queryset.filter(discount_percent__gte=value)


# 🔹 Category CRUD
class ProductCategoryViewSet(viewsets.ModelViewSet):
    queryset = ProductCategory.objects.all().order_by("name")
    serializer_class = ProductCategorySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

# 🔹 Product CRUD
class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all().order_by("-created_at")
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [
        filters.SearchFilter,
        DjangoFilterBackend,
        filters.OrderingFilter
    ]
    search_fields = ["name", "description", "category__name", "city__name"]
    filterset_class = ProductFilter
    ordering_fields = ["created_at", "price", "discount_price"]
    ordering = ["-created_at"]
    
    def get_permissions(self):
        if self.action == "create":
            return [IsBusinessOwner()]
        if self.action in ["update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsOwnerOrReadOnly()]
        if self.action == "my_products":
            return [IsAuthenticated()]
        return super().get_permissions()
    
    # ✅ NEW: Override list to handle n8n agents (return all products when no page param)
    def list(self, request, *args, **kwargs):
        """
        Override list method to support n8n agents and custom pagination.
        Returns all products when no 'page' parameter is provided (for n8n).
        Uses pagination when 'page' is explicitly provided (for frontend).
        """
        page_param = request.query_params.get('page')
        all_products = request.query_params.get('all')
        no_pagination = request.query_params.get('no_pagination')
        
        # ✅ If no page parameter OR explicit all/no_pagination flag, return all products
        if all_products == 'true' or no_pagination == 'true' or page_param is None:
            queryset = self.filter_queryset(self.get_queryset())
            serializer = self.get_serializer(queryset, many=True)
            
            print(f"🛒 Returning ALL products: {queryset.count()}")
            
            return Response(serializer.data)
        
        # ✅ Otherwise use default pagination (for frontend with page param)
        return super().list(request, *args, **kwargs)
      
    # ✅ Override pagination based on query params
    def paginate_queryset(self, queryset):
        """
        Allow custom page_size from query params if provided.
        This lets the frontend request more items for sliders/carousels.
        """
        if 'page_size' in self.request.query_params:
            try:
                page_size = int(self.request.query_params['page_size'])
                print("✅ Page size received sana:", page_size)
                # Set a reasonable maximum to prevent abuse
                if 1 <= page_size <= 1000:
                    self.paginator.page_size = page_size
            except (ValueError, TypeError):
                pass  # Invalid page_size, use default
        
        return super().paginate_queryset(queryset)
    
    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
    
    @action(detail=False, methods=["get"], url_path="my_products")
    def my_products(self, request):
        """
        Get all products owned by the current user.
        Supports pagination bypass with ?all=true or ?no_pagination=true
        """
        qs = self.get_queryset().filter(owner=request.user)
        
        # ✅ Check if user wants all products without pagination
        all_products = request.query_params.get('all')
        no_pagination = request.query_params.get('no_pagination')
        page_param = request.query_params.get('page')
        
        # ✅ Return all products if requested or no page parameter
        if all_products == 'true' or no_pagination == 'true' or page_param is None:
            serializer = self.get_serializer(qs, many=True)
            print(f"🛒 Returning ALL my products: {qs.count()}")
            return Response(serializer.data)
        
        # ✅ Otherwise use pagination
        page = self.paginate_queryset(qs)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)
    
    

# # 🔹 Product CRUD
# class ProductViewSet(viewsets.ModelViewSet):
#     queryset = Product.objects.all().order_by("-created_at")
#     serializer_class = ProductSerializer
#     permission_classes = [IsAuthenticatedOrReadOnly]

#     filter_backends = [
#         filters.SearchFilter,
#         DjangoFilterBackend,
#         filters.OrderingFilter
#     ]
#     search_fields = ["name", "description", "category__name", "city__name"]
#     filterset_class = ProductFilter
#     ordering_fields = ["created_at", "price", "discount_price"]
#     ordering = ["-created_at"]

#     def get_permissions(self):
#         if self.action == "create":
#             return [IsBusinessOwner()]
#         if self.action in ["update", "partial_update", "destroy"]:
#             return [IsAuthenticated(), IsOwnerOrReadOnly()]
#         if self.action == "my_products":
#             return [IsAuthenticated()]
#         return super().get_permissions()

#     def perform_create(self, serializer):
#         serializer.save(owner=self.request.user)

#     @action(detail=False, methods=["get"], url_path="my_products")
#     def my_products(self, request):
#         qs = self.get_queryset().filter(owner=request.user)
#         page = self.paginate_queryset(qs)
#         if page is not None:
#             serializer = self.get_serializer(page, many=True)
#             return self.get_paginated_response(serializer.data)
#         serializer = self.get_serializer(qs, many=True)
#         return Response(serializer.data)


# 🔹 Cart CRUD
class CartViewSet(viewsets.ModelViewSet):

    serializer_class = CartSerializer

    # ✅ Custom queryset
    def get_queryset(self):
        if not self.request.user.is_authenticated:
            # Agar login nahi hai to empty queryset return karo
            return Cart.objects.none()
        return Cart.objects.filter(user=self.request.user)

    # ✅ Custom create (Add to Cart)
    def create(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return Response(
                {"detail": "Login required to add items to your cart"},
                status=status.HTTP_401_UNAUTHORIZED
            )
        return super().create(request, *args, **kwargs)

    # ✅ Agar login hai to user assign karna
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    # serializer_class = CartSerializer
    # permission_classes = [IsAuthenticated]

    # def get_queryset(self):
    #     return Cart.objects.filter(user=self.request.user)

    # def perform_create(self, serializer):
    #     serializer.save(user=self.request.user)

    @action(detail=False, methods=["post"], url_path="add")
    def add_to_cart(self, request):
        product_id = request.data.get("product_id")
        quantity = int(request.data.get("quantity", 1))

        cart, _ = Cart.objects.get_or_create(user=request.user)
        item, created = CartItem.objects.get_or_create(cart=cart, product_id=product_id)
        if not created:
            item.quantity += quantity
        else:
            item.quantity = quantity
        item.save()

        return Response(CartSerializer(cart).data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["post"], url_path="remove")
    def remove_from_cart(self, request):
        product_id = request.data.get("product_id")
        cart = Cart.objects.filter(user=request.user).first()
        if not cart:
            return Response({"detail": "Cart not found"}, status=status.HTTP_404_NOT_FOUND)

        CartItem.objects.filter(cart=cart, product_id=product_id).delete()
        return Response(CartSerializer(cart).data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["post"], url_path="clear")
    def clear_cart(self, request):
        cart = Cart.objects.filter(user=request.user).first()
        if cart:
            cart.items.all().delete()
        return Response({"detail": "Cart cleared"}, status=status.HTTP_200_OK)



class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        # Use Q objects instead of union to avoid get_object issues
        from django.db.models import Q
        return Order.objects.filter(
            Q(user=user) | Q(owner=user)
        ).order_by("-created_at")
    
    def create(self, request, *args, **kwargs):
        """Override create method to handle order creation with proper response"""
        try:
            # Check if cart exists and has items
            cart = Cart.objects.filter(user=request.user).first()
            if not cart or cart.items.count() == 0:
                return Response(
                    {
                        "error": True,
                        "message": "Cart is empty",
                        "detail": "Your cart is empty. Please add items before checkout."
                    }, 
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Get seller from first item
            first_item = cart.items.first()
            if not first_item or not first_item.product or not first_item.product.owner:
                return Response(
                    {
                        "error": True,
                        "message": "Invalid cart items",
                        "detail": "Cart contains items with invalid seller information."
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            seller = first_item.product.owner
            
            # Calculate total
            total_amount = cart.grand_total

            # Extract customer details from request
            full_name = request.data.get("full_name")
            email = request.data.get("email")
            phone = request.data.get("phone")
            address_line1 = request.data.get("address_line1")
            address_line2 = request.data.get("address_line2", "")
            city = request.data.get("city")
            country = request.data.get("country", "Pakistan")

            # Validate required fields
            required_fields = {
                'full_name': full_name,
                'email': email,
                'phone': phone,
                'address_line1': address_line1,
                'city': city
            }
            
            missing_fields = [field for field, value in required_fields.items() if not value or not value.strip()]
            if missing_fields:
                return Response(
                    {
                        "error": True,
                        "message": "Missing required fields",
                        "detail": f"Please provide: {', '.join(missing_fields)}"
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Create order
            order = Order.objects.create(
                user=request.user,  # Buyer
                owner=seller,       # Seller/Product Owner
                full_name=full_name.strip(),
                email=email.strip().lower(),
                phone=phone.strip(),
                address_line1=address_line1.strip(),
                address_line2=address_line2.strip() if address_line2 else "",
                city=city.strip(),
                country=country.strip(),
                payment_method="COD",
                status="Pending",
                total_price=total_amount
            )

            # Create order items
            order_items_created = 0
            for item in cart.items.all():
                if item.product:  # Ensure product exists
                    effective_price = item.product.discount_price or item.product.price
                    OrderItem.objects.create(
                        order=order,
                        product=item.product,
                        quantity=item.quantity,
                        price=effective_price,
                        subtotal=effective_price * item.quantity
                    )
                    order_items_created += 1

            # Clear cart after successful order creation
            cart.items.all().delete()

            # Send email to seller (product owner)
            email_sent = False
            try:
                if seller.email:
                    subject = f"New Order Received - GB Green Guide #{order.id}"
                    message = f"""
Dear {seller.first_name or seller.username},

You have received a new order!

Order Details:
- Order ID: #{order.id}
- Customer: {request.user.first_name or request.user.username}
- Customer Name: {order.full_name}
- Total Amount: Rs. {order.total_price}
- Customer Phone: {order.phone}
- Customer Email: {order.email}

Shipping Address:
{order.full_name}
{order.address_line1}
{order.address_line2 + ', ' if order.address_line2 else ''}{order.city}, {order.country}

Items Ordered:
"""
                    # Add order items to email
                    for item in order.items.all():
                        message += f"- {item.product.name} x {item.quantity} = Rs. {item.subtotal}\n"
                    
                    message += f"""
Please contact the customer to confirm and arrange delivery.

Best regards,
GB Green Guide Team
                    """
                    send_mail(
                        subject, 
                        message, 
                        settings.DEFAULT_FROM_EMAIL, 
                        [seller.email],
                        fail_silently=True
                    )
                    email_sent = True
                    print(f"Order notification email sent to {seller.email}")
            except Exception as e:
                print(f"Failed to send order notification email: {e}")

            # Return success response with order data
            order_data = OrderSerializer(order).data
            
            return Response({
                "error": False,
                "message": "Order placed successfully!",
                "data": order_data,
                "email_sent": email_sent,
                "items_count": order_items_created
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            print(f"Order creation error: {str(e)}")
            import traceback
            traceback.print_exc()
            return Response({
                "error": True,
                "message": "Failed to create order",
                "detail": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def destroy(self, request, *args, **kwargs):
        """Override destroy method to handle order deletion"""
        try:
            order = self.get_object()
            
            # Check if current user has permission to delete this order
            if order.user != request.user and order.owner != request.user:
                return Response(
                    {
                        "error": True,
                        "message": "Not authorized to delete this order",
                        "detail": "You can only delete your own orders."
                    }, 
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Allow deletion for all statuses (removed restriction)
            # Users can now delete delivered orders to clean their records
            
            order_id = order.id
            order.delete()
            
            return Response({
                "error": False,
                "message": f"Order #{order_id} deleted successfully"
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            print(f"Order deletion error: {str(e)}")
            return Response({
                "error": True,
                "message": "Failed to delete order",
                "detail": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def perform_create(self, serializer):
        # This method is no longer used since we override create()
        pass

    @action(detail=True, methods=["post"], url_path="confirm")
    def confirm_order(self, request, pk=None):
        try:
            # Get the order
            order = self.get_object()
            
            # Check if current user is the seller (owner)
            if order.owner != request.user:
                return Response(
                    {
                        "error": True,
                        "message": "Not authorized to update this order",
                        "detail": "You can only update orders for your own products."
                    }, 
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Get the new status from request data
            new_status = request.data.get('status', 'Confirmed')
            old_status = order.status
            
            # Validate the status
            valid_statuses = ['Pending', 'Confirmed', 'Shipped', 'Delivered', 'Cancelled']
            if new_status not in valid_statuses:
                return Response(
                    {
                        "error": True,
                        "message": "Invalid status",
                        "detail": f"Status must be one of: {', '.join(valid_statuses)}"
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Update order status
            order.status = new_status
            order.save()
            
            print(f"Order {order.id} status updated from {old_status} to {new_status}")
            
            # Send confirmation email to buyer ONLY when status changes to "Confirmed"
            if new_status == "Confirmed" and old_status != "Confirmed":
                try:
                    if order.email:
                        subject = f"Order Confirmed - GB Green Guide #{order.id}"
                        message = f"""
Dear {order.full_name},

Great news! Your order #{order.id} has been confirmed by the seller!

Order Details:
- Order ID: #{order.id}
- Seller: {order.owner.first_name or order.owner.username}
- Total Amount: Rs. {order.total_price}
- Payment Method: {order.payment_method}
- Status: {order.status}

Items Ordered:
"""
                        # Add order items to email
                        for item in order.items.all():
                            message += f"- {item.product.name} x {item.quantity} = Rs. {item.subtotal}\n"
                        
                        message += f"""
The seller will contact you soon at {order.phone} to arrange delivery.

Thank you for shopping with GB Green Guide!

Best regards,
GB Green Guide Team
                        """
                        send_mail(
                            subject,
                            message,
                            settings.DEFAULT_FROM_EMAIL,
                            [order.email],
                            fail_silently=True
                        )
                        print(f"Confirmation email sent to buyer: {order.email}")
                except Exception as e:
                    print(f"Failed to send confirmation email to buyer: {e}")
            
            # Send cancellation email when order is cancelled
            if new_status == "Cancelled":
                try:
                    # Email to buyer
                    if order.email:
                        subject = f"Order Cancelled - GB Green Guide #{order.id}"
                        message = f"""
Dear {order.full_name},

Your order #{order.id} has been cancelled.

Order Details:
- Order ID: #{order.id}
- Total Amount: Rs. {order.total_price}
- Cancellation Date: {order.updated_at.strftime('%B %d, %Y')}

If you have any questions, please contact us.

Best regards,
GB Green Guide Team
                        """
                        send_mail(
                            subject,
                            message,
                            settings.DEFAULT_FROM_EMAIL,
                            [order.email],
                            fail_silently=True
                        )
                        print(f"Cancellation email sent to buyer: {order.email}")
                except Exception as e:
                    print(f"Failed to send cancellation email: {e}")
            
            # Return success response
            return Response({
                "error": False,
                "message": f"Order status updated from {old_status} to {new_status}",
                "data": OrderSerializer(order).data
            }, status=status.HTTP_200_OK)
            
        except Order.DoesNotExist:
            return Response({
                "error": True,
                "message": "Order not found",
                "detail": "The requested order does not exist."
            }, status=status.HTTP_404_NOT_FOUND)
            
        except Exception as e:
            print(f"Order confirmation error: {str(e)}")
            import traceback
            traceback.print_exc()
            
            return Response({
                "error": True,
                "message": "Failed to update order status",
                "detail": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=["post"], url_path="cancel")
    def cancel_order(self, request, pk=None):
        """Cancel an order - accessible by both buyer and seller"""
        try:
            order = self.get_object()
            
            # Check if current user has permission to cancel this order
            if order.user != request.user and order.owner != request.user:
                return Response(
                    {
                        "error": True,
                        "message": "Not authorized to cancel this order",
                        "detail": "You can only cancel your own orders."
                    }, 
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Check if order can be cancelled
            if order.status in ['Delivered', 'Cancelled']:
                return Response(
                    {
                        "error": True,
                        "message": "Cannot cancel order",
                        "detail": f"Orders with status '{order.status}' cannot be cancelled."
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            old_status = order.status
            order.status = "Cancelled"
            order.save()
            
            # Send cancellation emails to both parties
            try:
                # Email to buyer
                if order.email:
                    subject = f"Order Cancelled - GB Green Guide #{order.id}"
                    cancelled_by = "seller" if request.user == order.owner else "you"
                    message = f"""
Dear {order.full_name},

Your order #{order.id} has been cancelled by {cancelled_by}.

Order Details:
- Order ID: #{order.id}
- Total Amount: Rs. {order.total_price}
- Previous Status: {old_status}
- Cancellation Date: {order.updated_at.strftime('%B %d, %Y')}

If you have any questions, please contact us.

Best regards,
GB Green Guide Team
                    """
                    send_mail(
                        subject,
                        message,
                        settings.DEFAULT_FROM_EMAIL,
                        [order.email],
                        fail_silently=True
                    )
                
                # Email to seller if buyer cancelled
                if request.user == order.user and order.owner.email:
                    subject = f"Order Cancelled by Customer - GB Green Guide #{order.id}"
                    message = f"""
Dear {order.owner.first_name or order.owner.username},

Order #{order.id} has been cancelled by the customer.

Order Details:
- Order ID: #{order.id}
- Customer: {order.full_name}
- Total Amount: Rs. {order.total_price}
- Previous Status: {old_status}
- Cancellation Date: {order.updated_at.strftime('%B %d, %Y')}

Best regards,
GB Green Guide Team
                    """
                    send_mail(
                        subject,
                        message,
                        settings.DEFAULT_FROM_EMAIL,
                        [order.owner.email],
                        fail_silently=True
                    )
                    
            except Exception as e:
                print(f"Failed to send cancellation emails: {e}")
            
            return Response({
                "error": False,
                "message": f"Order #{order.id} cancelled successfully",
                "data": OrderSerializer(order).data
            }, status=status.HTTP_200_OK)
            
        except Order.DoesNotExist:
            return Response({
                "error": True,
                "message": "Order not found",
                "detail": "The requested order does not exist."
            }, status=status.HTTP_404_NOT_FOUND)
            
        except Exception as e:
            print(f"Order cancellation error: {str(e)}")
            return Response({
                "error": True,
                "message": "Failed to cancel order",
                "detail": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=["get"], url_path="my_orders")
    def my_orders(self, request):
        """Get orders where current user is the buyer"""
        orders = Order.objects.filter(user=request.user).order_by("-created_at")
        page = self.paginate_queryset(orders)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(orders, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"], url_path="seller_orders")
    def seller_orders(self, request):
        """Get orders for current user's products (excluding cancelled orders)"""
        orders = Order.objects.filter(owner=request.user).exclude(status="Cancelled").order_by("-created_at")
        page = self.paginate_queryset(orders)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(orders, many=True)
        return Response(serializer.data)



class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
   
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        return Review.objects.filter(product_id=self.kwargs["product_pk"])

    def perform_create(self, serializer):
        serializer.save(
            user=self.request.user,
            product_id=self.kwargs["product_pk"]
        )




# ya wala fisrt wala ha 

# 🔹 Order CRUD (CORRECTED VERSION)
# class OrderViewSet(viewsets.ModelViewSet):
#     serializer_class = OrderSerializer
#     permission_classes = [IsAuthenticated]

#     def get_queryset(self):
#         user = self.request.user
#         # ✅ Fixed: Use 'user' and 'owner' fields correctly
#         buyer_orders = Order.objects.filter(user=user)  # Orders made by user
#         seller_orders = Order.objects.filter(owner=user)  # Orders for user's products
#         return buyer_orders.union(seller_orders).order_by("-created_at")
    
#     def create(self, request, *args, **kwargs):
#         """Override create method to handle order creation with proper response"""
#         try:
#             # Check if cart exists and has items
#             cart = Cart.objects.filter(user=request.user).first()
#             if not cart or cart.items.count() == 0:
#                 return Response(
#                     {
#                         "error": True,
#                         "message": "Cart is empty",
#                         "detail": "Your cart is empty. Please add items before checkout."
#                     }, 
#                     status=status.HTTP_400_BAD_REQUEST
#                 )

#             # ✅ Get seller from first item
#             first_item = cart.items.first()
#             if not first_item or not first_item.product or not first_item.product.owner:
#                 return Response(
#                     {
#                         "error": True,
#                         "message": "Invalid cart items",
#                         "detail": "Cart contains items with invalid seller information."
#                     },
#                     status=status.HTTP_400_BAD_REQUEST
#                 )
            
#             seller = first_item.product.owner
            
#             # ✅ Calculate total
#             total_amount = cart.grand_total

#             # ✅ Extract customer details from request
#             full_name = request.data.get("full_name")
#             email = request.data.get("email")
#             phone = request.data.get("phone")
#             address_line1 = request.data.get("address_line1")
#             address_line2 = request.data.get("address_line2", "")
#             city = request.data.get("city")
#             country = request.data.get("country", "Pakistan")

#             # Validate required fields
#             required_fields = {
#                 'full_name': full_name,
#                 'email': email,
#                 'phone': phone,
#                 'address_line1': address_line1,
#                 'city': city
#             }
            
#             missing_fields = [field for field, value in required_fields.items() if not value or not value.strip()]
#             if missing_fields:
#                 return Response(
#                     {
#                         "error": True,
#                         "message": "Missing required fields",
#                         "detail": f"Please provide: {', '.join(missing_fields)}"
#                     },
#                     status=status.HTTP_400_BAD_REQUEST
#                 )

#             # ✅ Create order
#             order = Order.objects.create(
#                 user=request.user,
#                 owner=seller,
#                 full_name=full_name.strip(),
#                 email=email.strip().lower(),
#                 phone=phone.strip(),
#                 address_line1=address_line1.strip(),
#                 address_line2=address_line2.strip() if address_line2 else "",
#                 city=city.strip(),
#                 country=country.strip(),
#                 payment_method="COD",
#                 status="Pending",
#                 total_price=total_amount
#             )

#             # ✅ Create order items
#             order_items_created = 0
#             for item in cart.items.all():
#                 if item.product:  # Ensure product exists
#                     effective_price = item.product.discount_price or item.product.price
#                     OrderItem.objects.create(
#                         order=order,
#                         product=item.product,
#                         quantity=item.quantity,
#                         price=effective_price,
#                         subtotal=effective_price * item.quantity
#                     )
#                     order_items_created += 1

#             # ✅ Clear cart after successful order creation
#             cart.items.all().delete()

#             # 📩 Send email to seller (don't fail order if email fails)
#             email_sent = False
#             try:
#                 if seller.email:
#                     subject = f"New Order Received - GB Green Guide #{order.id}"
#                     message = f"""
# Dear {seller.first_name or seller.username},

# You have received a new order!

# Order Details:
# - Order ID: #{order.id}
# - Customer: {request.user.first_name or request.user.username}
# - Total Amount: Rs. {order.total_price}
# - Customer Phone: {order.phone}
# - Customer Email: {order.email}

# Shipping Address:
# {order.full_name}
# {order.address_line1}
# {order.address_line2 + ', ' if order.address_line2 else ''}{order.city}, {order.country}

# Please contact the customer to confirm and arrange delivery.

# Best regards,
# GB Green Guide Team
#                     """
#                     send_mail(
#                         subject, 
#                         message, 
#                         settings.DEFAULT_FROM_EMAIL, 
#                         [seller.email],
#                         fail_silently=True
#                     )
#                     email_sent = True
#                     print(f"Order notification email sent to {seller.email}")
#             except Exception as e:
#                 print(f"Failed to send order notification email: {e}")

#             # ✅ Return success response with order data
#             order_data = OrderSerializer(order).data
            
#             return Response({
#                 "error": False,
#                 "message": "Order placed successfully!",
#                 "data": order_data,
#                 "email_sent": email_sent,
#                 "items_count": order_items_created
#             }, status=status.HTTP_201_CREATED)

#         except Exception as e:
#             print(f"Order creation error: {str(e)}")
#             return Response({
#                 "error": True,
#                 "message": "Failed to create order",
#                 "detail": str(e)
#             }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#     def perform_create(self, serializer):
#         # This method is no longer used since we override create()
#         # Keep it empty for compatibility
#         pass

#     @action(detail=True, methods=["post"], url_path="confirm")
#     def confirm_order(self, request, pk=None):
#         order = self.get_object()
#         # ✅ Check if current user is the seller (owner)
#         if order.owner != request.user:
#             return Response(
#                 {"detail": "Not authorized to confirm this order"}, 
#                 status=status.HTTP_403_FORBIDDEN
#             )
        
#         order.status = "Confirmed"
#         order.save()
        
#         # Optional: Send confirmation email to buyer
#         try:
#             if order.email:
#                 subject = f"Order Confirmed - GB Green Guide #{order.id}"
#                 message = f"""
# Dear {order.full_name},

# Your order #{order.id} has been confirmed by the seller!

# The seller will contact you soon to arrange delivery.

# Order Total: Rs. {order.total_price}

# Thank you for shopping with GB Green Guide!

# Best regards,
# GB Green Guide Team
#                 """
#                 send_mail(
#                     subject,
#                     message,
#                     settings.DEFAULT_FROM_EMAIL,
#                     [order.email],
#                     fail_silently=True
#                 )
#         except Exception as e:
#             print(f"Failed to send confirmation email: {e}")
        
#         return Response(OrderSerializer(order).data)

#     @action(detail=False, methods=["get"], url_path="my_orders")
#     def my_orders(self, request):
#         """Get orders where current user is the buyer"""
#         orders = Order.objects.filter(user=request.user).order_by("-created_at")
#         page = self.paginate_queryset(orders)
#         if page is not None:
#             serializer = self.get_serializer(page, many=True)
#             return self.get_paginated_response(serializer.data)
#         serializer = self.get_serializer(orders, many=True)
#         return Response(serializer.data)

#     @action(detail=False, methods=["get"], url_path="seller_orders")
#     def seller_orders(self, request):
#         """Get orders for current user's products"""
#         orders = Order.objects.filter(owner=request.user).order_by("-created_at")
#         page = self.paginate_queryset(orders)
#         if page is not None:
#             serializer = self.get_serializer(page, many=True)
#             return self.get_paginated_response(serializer.data)
#         serializer = self.get_serializer(orders, many=True)
#         return Response(serializer.data)
# ya wala fisrt wala ha 







