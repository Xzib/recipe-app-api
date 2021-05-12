from django.db import transaction, IntegrityError

import tempfile
import os

from PIL import Image

from django.contrib.auth import get_user_model
from django.test import TestCase, TransactionTestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Recipe, Tag, Ingredients
from recipe.serializers import RecipeSerailizer, RecipeDetailSerializer

RECIPES_URL = reverse("recipe:recipe-list")


def image_upload_url(recipe_id):
    """return URL for recipe image"""
    return reverse('recipe:recipe-upload-image', args=[recipe_id])

def detail_url(recipe_id):
    """return recipe detail url"""
    return reverse('recipe:recipe-detail', args=[recipe_id])


def sample_tag(user, name='Main Course'):
    """Create and return a tag"""
    return Tag.objects.create(user=user, name=name)


def sample_ingredient(user, name='Cinamon'):
    """Create an Ingredient"""
    return Ingredients.objects.create(user=user, name=name)


def sample_recipe(user, **params):
    """Create and return a simple recipe"""
    defaults = {
        'title': 'Sample recipe',
        'time_minutes': '5',
        'price': '10'
    }
    defaults.update(params)

    return Recipe.objects.create(user=user, **defaults)


class PublicRecipeApiTests(TestCase):
    """Test unauthorized recipe access"""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test that authentication is required"""
        res = self.client.get(RECIPES_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeApiTest(TestCase):
    """Test Unauthenticated recipe API Access"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'test@123.com',
            'test1234',
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_recipe(self):
        sample_recipe(user=self.user)
        sample_recipe(user=self.user)

        res = self.client.get(RECIPES_URL)

        recipes = Recipe.objects.all().order_by('-id')
        serializer = RecipeSerailizer(recipes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_recipe_limited_to_user(self):
        """Test Retrieving recipees for user"""
        user2 = get_user_model().objects.create_user(
            'test1@123.com',
            'test12345',
        )
        sample_recipe(user=user2)
        sample_recipe(user=self.user)

        res = self.client.get(RECIPES_URL)

        recipe = Recipe.objects.filter(user=self.user)
        serializer = RecipeSerailizer(recipe, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data, serializer.data)

    def test_view_recipe_detail(self):
        """test viewing the recipe detail"""
        recipe = sample_recipe(user=self.user)
        recipe.tags.add(sample_tag(user=self.user))
        recipe.ingredients.add(sample_ingredient(user=self.user))

        url = detail_url(recipe.id)
        res = self.client.get(url)

        serializer = RecipeDetailSerializer(recipe)

        self.assertEqual(res.data, serializer.data)

    def test_create_basic_recipe(self):
        """test creating recipe"""
        payload = {
            'title': 'chicken karhai',
            'time_minutes': 2,
            'price': 25,

        }

        res = self.client.post(RECIPES_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        recipe = Recipe.objects.get(id=res.data['id'])

        for key in payload.keys():
            self.assertEqual(payload[key], getattr(recipe, key))

    def test_create_tag_recipe(self):
        """Create recipe with tags"""
        tag1 = sample_tag(user=self.user, name="sweet")
        tag2 = sample_tag(user=self.user, name="sour")

        payload = {
            'title': 'Tinday Aloo',
            'tags': [tag1.id, tag2.id],
            'time_minutes': 20,
            'price': 25,
        }

        res = self.client.post(RECIPES_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        recipe = Recipe.objects.get(id=res.data['id'])
        tags = recipe.tags.all()

        self.assertEqual(tags.count(), 2)
        self.assertIn(tag1, tags)
        self.assertIn(tag2, tags)

    def test_create_ingredients_recipe(self):
        """Create recipe with ingredients"""
        ingredient1 = sample_ingredient(user=self.user, name="red chilli")
        ingredient2 = sample_ingredient(user=self.user, name="mint")

        payload = {
            'title': "chicken aloo",
            'ingredients': [ingredient1.id, ingredient2.id],
            'time_minutes': 20,
            'price': 50.2
        }

        res = self.client.post(RECIPES_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        recipe = Recipe.objects.get(id=res.data['id'])
        ingredients = recipe.ingredients.all()

        self.assertEqual(ingredients.count(), 2)
        self.assertIn(ingredient1, ingredients)
        self.assertIn(ingredient2, ingredients)

    def test_partial_update_recipe(self):
        """test updating a recipe with patch"""
        recipe = sample_recipe(user=self.user)
        recipe.tags.add(sample_tag(user=self.user))
        new_tag = sample_tag(user=self.user, name="continental")

        payload = {'title': 'Chicken tikka', 'tags': [new_tag.id]}
        url = detail_url(recipe.id)
        self.client.patch(url, payload)

        recipe.refresh_from_db()
        self.assertEqual(recipe.title, payload['title'])
        tag = recipe.tags.all()
        self.assertEqual(len(tag), 1)
        self.assertIn(new_tag, tag)

    def test_full_update_recipe(self):
        recipe = sample_recipe(user=self.user)
        recipe.tags.add(sample_tag(user=self.user))
        payload = {
            'title': 'speghetti',
            'time_minutes': 10,
            'price': 100,
        }
        url = detail_url(recipe.id)
        self.client.put(url, payload)

        recipe.refresh_from_db()
        self.assertEqual(recipe.title, payload['title'])
        self.assertEqual(recipe.time_minutes, payload['time_minutes'])
        self.assertEqual(recipe.price, payload['price'])

        tags = recipe.tags.all()
        self.assertEqual(len(tags), 0)


class RecipeImageUploadTest(TransactionTestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'zohaib@123.com',
            'testpass'
        )
        self.client.force_authenticate(self.user)
        self.recipe = sample_recipe(user=self.user)
    
    def tearDown(self):
        self.recipe.image.delete()
    
    def test_upload_image(self):
        """Test uploading an image to recipe"""
        url = image_upload_url(self.recipe.id)
        # temp_file = tempfile.NamedTemporaryFile(suffix='.jpg')    
        # try:
        #     img = Image.new('RGB', (10, 10))
        #     img.save(temp_file, format='JPEG')
        #     temp_file.seek(0)
        #     res = self.client.post(url, {'image':temp_file}, format='multipart')
        # except IntegrityError:
        #     pass
        # finally:
        #     temp_file.close()
        
        with tempfile.NamedTemporaryFile(suffix='.jpg') as ntf:
            img = Image.new('RGB', (10, 10))
            img.save(ntf, format='JPEG')
            ntf.seek(0)
            res = self.client.post(url, {'image':ntf}, format='multipart')
        
        self.recipe.refresh_from_db()
        print(res)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('image', res.data)
        self.assertTrue(os.path.exists(self.recipe.image.path))

    def test_upload_image_bad_request(self):
        """test uploading an invalid image"""
        url = image_upload_url(self.recipe.id)
        res = self.client.post(url, {'image':'not an image'}, format='multipart')

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)