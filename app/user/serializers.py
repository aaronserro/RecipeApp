"""
Seralizers for the user API View
"""
from django.contrib.auth import (
    get_user_model,
    authenticate,

    )
from django.utils.translation import gettext as _
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    class Meta:  # Tell django all of the parameters we want to pass into the Serializer
        model = get_user_model()  # model that the serializer is for
        fields = ['email', 'password', 'name']  # things that need to be set when you make a request(only allow fields that the user would change)
        extra_kwargs = {'password': {'write_only': True, 'min_length': 5}}  # provides extra information to the fields provided

    def create(self, validated_data):  # Override the behaviour of the serializer when creating new objects from the serializer
        """Create and return a user with encrypted password"""
        return get_user_model().objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        """Update and return user"""
        password = validated_data.pop('password', None)
        user = super().update(instance, validated_data)

        if password:
            user.set_password(password)
            user.save()
        return user


class AuthTokenSerializer(serializers.Serializer):
    """Serializer for the user auth token"""
    email = serializers.EmailField()
    password = serializers.CharField(
        style={'input_type': 'password'},
        trim_whitespace=False,
    )

    def validate(self, attrs):
        """Validate and authenticate the user"""
        email = attrs.get('email')
        password = attrs.get('password')
        user = authenticate(
            request=self.context.get('request'),
            username=email,
            password=password,
        )
        if not user:
            msg =_('Unable to authenticate with provided credentials')
            raise serializers.ValidationError(msg, code='authorization')
        attrs['user'] = user
        return attrs


