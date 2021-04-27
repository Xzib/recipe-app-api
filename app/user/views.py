from rest_framework import generics
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings

from user.serializers import UserSerialiser, AuthTokkenSerializer


class CreateUserView(generics.CreateAPIView):
    """Creates a new user in the system"""
    serializer_class = UserSerialiser


class CreateTokenView(ObtainAuthToken):
    """"Create a new auth token for the user"""
    serializer_class = AuthTokkenSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES
