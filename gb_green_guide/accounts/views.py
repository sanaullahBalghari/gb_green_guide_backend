# accounts/views.py
import base64
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import logout as django_logout
from django.http import JsonResponse
from rest_framework import generics
from .serializers import UserProfileSerializer


from .serializers import (
    RegisterSerializer, LoginSerializer,
    ForgotPasswordSerializer, ResetPasswordSerializer
)

User = get_user_model()

# Read JWT cookie settings from settings.py
JWT_COOKIE_NAME = getattr(settings, "JWT_AUTH_COOKIE", "access_token")
JWT_COOKIE_SAMESITE = getattr(settings, "JWT_AUTH_COOKIE_SAMESITE", "Lax")
JWT_COOKIE_SECURE = getattr(settings, "JWT_AUTH_COOKIE_SECURE", False)
JWT_COOKIE_MAX_AGE = getattr(settings, "JWT_AUTH_COOKIE_MAX_AGE", 3600)


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            user_data = {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "phone": user.phone,
                "role": user.role,
                "shop_name":user.shop_name,
                "address":user.address
            }
            # print("user regsiter data :", user)
            return Response({"message": "User registered successfully.",
                              "user": user_data
                             
                             }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data['username']
        password = serializer.validated_data['password']

        user = authenticate(request, username=username, password=password)
        print("logged in user :",user)
        if not user:
            return Response({"detail": "Invalid credentials."}, status=status.HTTP_401_UNAUTHORIZED)
        if not user.is_active:
            return Response({"detail": "User is inactive."}, status=status.HTTP_403_FORBIDDEN)

        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)

        response = Response({
            "message": "Login successful.",
            # OPTIONAL: return some basic user info (no sensitive data)
            "access": access_token,
        
            "user": {
                "id": user.pk,
                "username": user.username,
                "role": getattr(user, "role", None)
            }
        }, status=status.HTTP_200_OK)

        # Set HttpOnly cookie with access token (short lived)
        response.set_cookie(
            key=JWT_COOKIE_NAME,
            value=access_token,
            max_age=JWT_COOKIE_MAX_AGE,
            httponly=False,
            secure=JWT_COOKIE_SECURE,
            samesite=JWT_COOKIE_SAMESITE
        )
        # Optionally set a refresh cookie if you want (not required here)
        return response


class LogoutView(APIView):
    permission_classes = [AllowAny]  # logout should be callable anytime

    def post(self, request):
        # Clear Django session if used
        try:
            django_logout(request)
        except Exception:
            pass

        # Prepare response and delete access token cookie
        
        # response = JsonResponse({"message": "Logged out."})

        response = Response({"message": "Logged out."}, status=status.HTTP_200_OK)
        response.delete_cookie(
            JWT_COOKIE_NAME,
            path="/",
            domain=getattr(settings, "SESSION_COOKIE_DOMAIN", None),
            samesite=JWT_COOKIE_SAMESITE,
            # secure=JWT_COOKIE_SECURE,
        )
        return response



class ForgotPasswordView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']

        # Find users with this email (if you allow non-unique email, take first)
        users_qs = User.objects.filter(email__iexact=email)
        if not users_qs.exists():
            # Don't reveal whether email exists — respond with success message
            return Response({"message": "If an account with that email exists, a reset link will be sent."}, status=status.HTTP_200_OK)

        # For each user send a password reset email (usually one)
        for user in users_qs:
            uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            # Build reset link - FRONTEND_URL should be provided in settings (e.g. https://yourfrontend.com)
            frontend_base = getattr(settings, "FRONTEND_URL", None)
            if not frontend_base:
                # If FRONTEND_URL not set, you can fallback to a route on backend to handle token validation
                reset_link = f"{request.scheme}://{request.get_host()}/accounts/reset-password/?uid={uidb64}&token={token}"
            else:
                # Example frontend route: /reset-password?uid=...&token=...
                # reset_link = f"{frontend_base.rstrip('/')}/reset-password?uid={uidb64}&token={token}"
                reset_link = f"{frontend_base.rstrip('/')}/reset-password/{uidb64}/{token}/"

            subject = "Password reset for your account"
            message = f"Hi {user.username},\n\nUse the link below to reset your password:\n\n{reset_link}\n\nIf you did not request this, ignore this email."
            from_email = getattr(settings, "DEFAULT_FROM_EMAIL", None)
            # send_mail will use your EMAIL_BACKEND settings
            send_mail(subject, message, from_email, [user.email], fail_silently=False)

        return Response({"message": "If an account with that email exists, a reset link will be sent."}, status=status.HTTP_200_OK)

class ResetPasswordView(APIView):
    permission_classes = [AllowAny]

    def put(self, request, uidb64, token):  # <- Add these parameters here
        # Get password data from serializer (but not uid/token)
        serializer = ResetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        new_password = serializer.validated_data['new_password']
        
        # uid and token come from URL parameters now, not from serializer
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except Exception:
            return Response({"detail": "Invalid uid."}, status=status.HTTP_400_BAD_REQUEST)

        if not default_token_generator.check_token(user, token):
            return Response({"detail": "Invalid or expired token."}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
        user.save()
        return Response({"message": "Password reset successful."}, status=status.HTTP_200_OK)

# accounts/views.py


class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        # 👤 Current logged-in user ko console me print karega
        print("👤 Current user:", self.request.user)
        return self.request.user

    def update(self, request, *args, **kwargs):
        # 📝 Update request ka data console me print karega
        print("📝 Profile update request data:", request.data)
        return super().update(request, *args, **kwargs)

