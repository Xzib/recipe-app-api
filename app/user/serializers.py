from django.contrib.auth import get_user_model

from rest_framework import serializers


class UserSerialiser(serializers.ModelSerializer):
    """Serializer for the user object"""

    class Meta:
        model = get_user_model()
        fields = ['email', 'password', 'name']
        extra_kwargs = {'password': {'write_only':True, 'min_length':5}}

    def create(self, validated_data):
        """Create a new user with encrypted password and returns it"""
        return get_user_model.objects.create_user(**validated_data)