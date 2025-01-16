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
