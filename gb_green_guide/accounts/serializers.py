# accounts/serializers.py
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from ecommerce.models import Product  # 👈 import product model
from django.db.models import Count
User = get_user_model()



class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['first_name','last_name','username', 'password', 'confirm_password', 'phone','email', 'role', 'shop_name', 'address']

    def validate(self, data):
        if data.get('password') != data.get('confirm_password'):
            raise serializers.ValidationError({"confirm_password": "Password fields didn't match."})
        # Optionally use Django password validators:
        validate_password(data.get('password'))
        return data

    def create(self, validated_data):
        validated_data.pop('confirm_password', None)
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)


class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()


class ResetPasswordSerializer(serializers.Serializer):
    # Remove uid and token fields since they come from URL now
    new_password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, data):
        if data.get('new_password') != data.get('confirm_password'):
            raise serializers.ValidationError({"confirm_password": "Password fields didn't match."})
        validate_password(data.get('new_password'))
        return data

# accounts/serializers.py
class UserProfileSerializer(serializers.ModelSerializer):
    total_reviews = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ["id","first_name","last_name", "username", "email", "phone", "role", "shop_name", "address","total_reviews"]
        read_only_fields = ["id"] 
    

    def get_total_reviews(self, obj):
        return Product.objects.filter(owner=obj).aggregate(
            total_reviews=Count("reviews")
        )["total_reviews"] or 0
        # read_only_fields = ["id", "username", "email"]  # username & email ko edit nahi karne dena
