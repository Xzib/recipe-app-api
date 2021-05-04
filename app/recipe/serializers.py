from rest_framework import serializers
from core.models import Tag, Ingredients


class TagSerializer(serializers.ModelSerializer):
    """Serializer for tag objects"""

    class Meta:
        model = Tag
        fields = ('id', 'name')
        read_only_fields = ('id',)


class IngredientSerializer(serializers.ModelSerializer):
    """Serializer for ingredients"""

    class Meta:
        model = Ingredients
        fields = ('id', 'name')
        read_only_fields = ('id',)
