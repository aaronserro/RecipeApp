"""
Seralizers for the user API View
"""
from django.contrib.auth import get_user_model

from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    class Meta:  # Tell django all of the parameters we want to pass into the Serializer
        model = get_user_model()  # model that the serializer is for
        fields = ['email', 'password', 'name']  # things that need to be set when you make a request(only allow fields that the user would change)
        extra_kwargs = {'password': {'write_only': True, 'min_length': 5}}  # provides extra information to the fields provided

    def create(self, validated_data):  # Override the behaviour of the serializer when creating new objects from the serializer
        """Create and return a user with encrypted password"""
        return get_user_model().objects.create_user(**validated_data)
