from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Ingredients, Recipe

from recipe.serializers import IngredientSerializer

INGREDIENT_URL = reverse("recipe:ingredients-list")


class PublicIngredientsApiTests(TestCase):
    """Test the publically available ingredients API"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Test that login is required to access the endpoint"""
        res = self.client.get(INGREDIENT_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngredientApiTests(TestCase):
    """Test ingredients can be accessed by authorized user"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'test@123.com',
            'test1234'
        )

        self.client.force_authenticate(self.user)

    def test_retreive_ingredients_list(self):
        """Test retrieving a list of ingredients"""
        Ingredients.objects.create(user=self.user, name='Kale')
        Ingredients.objects.create(user=self.user, name='Carrot')

        res = self.client.get(INGREDIENT_URL)

        ingredients = Ingredients.objects.all().order_by('-name')
        serializer = IngredientSerializer(ingredients, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_ingredients_limited_to_user(self):
        """test that only ingredients for the authenticated
            user are returned"""

        user2 = get_user_model().objects.create_user(
             'zohaib@123.com',
             'zohaib123'
         )
        Ingredients.objects.create(user=user2, name='Vinegar')

        ingredient = Ingredients.objects.create(
                    user=self.user, name="Turmeric"
                    )
        res = self.client.get(INGREDIENT_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], ingredient.name)

    def test_create_ingredient_successful(self):
        """Test that a ingredient has been created successfully"""
        payload = {
            'name': 'turmeric'
        }

        self.client.post(INGREDIENT_URL, payload)

        exists = Ingredients.objects.filter(
            user=self.user,
            name=payload['name']
        ).exists()

        self.assertTrue(exists)

    def test_create_ingredient_invalid(self):
        """test that a invalid ingredient fails"""
        payload = {
            'name': ''
        }
        res = self.client.post(INGREDIENT_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_ingredients_assigned_to_recipes(self):
        """test filtering ingredients assigned to recipes"""
        ingredient1 = Ingredients.objects.create(
            user=self.user,
            name='Breakfast'
            )
        ingredient2 = Ingredients.objects.create(user=self.user, name='Dinner')
        recipe = Recipe.objects.create(
            title='biryani',
            time_minutes=30,
            price=250,
            user=self.user
        )
        recipe.ingredients.add(ingredient1)

        res = self.client.get(INGREDIENT_URL, {'assigned_only': 1})

        serializer1 = IngredientSerializer(ingredient1)
        serializer2 = IngredientSerializer(ingredient2)

        self.assertIn(serializer1.data, res.data)
        self.assertNotIn(serializer2.data, res.data)

    def test_retrive_ingredients_assigned_to_unique(self):
        """Return unique ingredients assigned to recipes"""
        ingredient = Ingredients.objects.create(user=self.user, name='supper')
        Ingredients.objects.create(user=self.user, name='meetha')

        recipe1 = Recipe.objects.create(
            title='aloo matar',
            time_minutes=15,
            price=50,
            user=self.user
        )
        recipe1.ingredients.add(ingredient)

        recipe2 = Recipe.objects.create(
            title='burger',
            time_minutes='10',
            price=500,
            user=self.user
        )
        recipe2.ingredients.add(ingredient)

        res = self.client.get(INGREDIENT_URL, {'assigned_only': 1})

        self.assertEqual(len(res.data), 1)
