# from rest_framework import serializers
# from djoser.serializers import UserSerializer as BaseUserCreateSerializer
# from accounts.models import User
#
#
# class UserSerializer(BaseUserCreateSerializer):
#     class Meta:
#         model = User
#
#         fields = ('id', 'username', 'email', 'password')
#         extra_kwargs = {'password': {'write_only': True}}
#
#     def create(self, validated_data):
#         # Ensure username exists
#         username = validated_data.get('username')
#         if not username:
#             raise serializers.ValidationError({"username": "This field is required."})
#
#         email = validated_data.get('email')
#         password = validated_data.get('password')
#
#         user = User.objects.create_user(
#             username=username,
#             email=email,
#             password=password
#         )
#         return user
#
#     def validate_username(self, value):
#         if ' ' in value or '!' in value:
#             raise serializers.ValidationError("Username cannot contain spaces or special characters.")
#         return value
#
#
# class ProfileSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = User
#         fields = ('username', 'email')
from django.contrib.auth import authenticate
from django.core.validators import RegexValidator, EmailValidator
from rest_framework import serializers
from accounts.models import User


def validate_password(value):
    if len(value) < 8:
        raise serializers.ValidationError('Password must be at least 8 characters long.')
    return value


def validate_username(value):
    if not value.isalnum() and not any(char in './-_' for char in value):
        raise serializers.ValidationError(
            'Username can only contain letters, numbers, and ./-/_ characters.'
        )
    return value


class RegisterSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(
        required=True,
        validators=[RegexValidator(
            regex=r'^[a-zA-Z]+$',
            message='First name can only contain letters.'
        )]
    )

    last_name = serializers.CharField(
        required=True,
        validators=[RegexValidator(
            regex=r'^[a-zA-Z]+$',
            message='Last name can only contain letters.'
        )]
    )

    username = serializers.CharField(
        required=True,
        validators=[validate_username]
    )

    email = serializers.EmailField(
        required=True,
        validators=[EmailValidator()]
    )

    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password]
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'first_name', 'last_name']

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name']
        )
        return user


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        user = authenticate(username=data['username'], password=data['password'])
        if not user:
            raise serializers.ValidationError('Invalid credentials', code='invalid')
        return data


class ProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'profile_picture')
