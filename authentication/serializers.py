from rest_framework import serializers
from authentication.models import User
from notifications.models import Notification


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        max_length=16, min_length=6, write_only=True)

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'phone', 'password')

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class LoginSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        max_length=16, min_length=6, write_only=True)

    class Meta:
        model = User
        fields = ('email', 'password', 'token')
        read_only_fields = ['token']


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'email', 'phone', 'password')
