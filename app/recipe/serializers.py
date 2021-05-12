from rest_framework import serializers
from core.models import Tag, Ingredients, Recipe


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


class RecipeSerailizer(serializers.ModelSerializer):
    """Serializer for Recipes"""

    ingredients = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Ingredients.objects.all()
    )

    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all()
    )

    class Meta:
        model = Recipe
        fields = ('id', 'title', 'ingredients', 'tags', 'time_minutes',
                  'price', 'link')
        read_only_fields = ('id',)


class RecipeDetailSerializer(RecipeSerailizer):
    """Serializer for Recipe Detail"""

    ingredients = IngredientSerializer(many=True, read_only=True)
    tags = TagSerializer(many=True, read_only=True)


class RecipeImageSerializer(serializers.ModelSerializer):
    """serializer for uploading images to recipe model"""

    class Meta:
        model = Recipe
        fields = ('id', 'image')
        read_only_fields = ('id',)