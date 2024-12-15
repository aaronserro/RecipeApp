"""Views for the user API"""
from rest_framework import generics
from user.serializers import UserSerializer


class CreateUserView(generics.CreateAPIView):  # Creating objects in Databas
    """Create a new user in system """
    serializer_class = UserSerializer  # set the serializer
# Create your views here.
