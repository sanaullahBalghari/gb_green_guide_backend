# accounts/urls.py
from django.urls import path
from .views import RegisterView, LoginView, LogoutView, ForgotPasswordView, ResetPasswordView, UserProfileView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='auth-register'),
    path('login/', LoginView.as_view(), name='auth-login'),
    path('logout/', LogoutView.as_view(), name='auth-logout'),
    path('forgot-password/', ForgotPasswordView.as_view(), name='auth-forgot-password'),
    path('reset-password/<uidb64>/<token>/', ResetPasswordView.as_view(), name='auth-reset-password'),
        # 🔹 New profile endpoint
    path('profile/', UserProfileView.as_view(), name='user-profile'),
   

]
