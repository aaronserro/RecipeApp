"""Views for the user API"""
from rest_framework import generics, authentication, permissions
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings
from django.views.generic import TemplateView


from user.serializers import (UserSerializer, AuthTokenSerializer,)


class SignupPageView(TemplateView):
    template_name = "user/signup.html"



class CreateUserView(generics.CreateAPIView):  # Creating objects in Databas
    """Create a new user in system """
    serializer_class = UserSerializer  # set the serializer

# Create your views here.


class CreateTokenView(ObtainAuthToken):
    """Create a new auth token for user"""
    serializer_class = AuthTokenSerializer  # customize the serializer
    renderer_class = api_settings.DEFAULT_RENDERER_CLASSES  # render the browzeable API


class ManageUserView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        """Retrieve and return the authenticated user"""
        return self.request.user

