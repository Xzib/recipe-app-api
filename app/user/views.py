from rest_framework import generics

from user.serializers import UserSerialiser

class CreateUserView(generics.CreateAPIView):
    """Creates a new user in the system"""
    serializer_class = UserSerialiser
