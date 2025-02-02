"""Tests for the ingredients API"""

from decimal import Decimal
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from core.models import Recipe, Tag, Ingredient
from recipe.serializers import (RecipeSerializer,
                               RecipeDetailSerializer, IngredientSerializer)

INGREDIENTS_URL = reverse('recipe:ingredient-list')


def create_user(email='user@example.com', password='testpas123'):
    """Create and return a new user"""
    return get_user_model().objects.create_user(email=email, password=password)


def detail_url(ingredient_id):
    """Create and retrun an ingredient url"""
    return reverse('recipe:ingredient-detail', args=[ingredient_id])


def create_recipe(user, **params):
    """Create and return a sample recipe"""
    defaults = {
        'title': 'Sample recipe title',
        'time_minutes': 22,
        'price': Decimal('5.25'),

        'link': 'http://example.com/recipe.pdf',
        'description': 'sample description',
    }

    defaults.update(params)
    recipe = Recipe.objects.create(user=user, **defaults)
    return recipe


class PublicIngredientsApiTests(TestCase):
    """Test unauthorized access to ingredients API and authentication is required"""
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(INGREDIENTS_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngredientsAPITest(TestCase):
    """Test authenticated Api Requests"""
    def setUp(self):
        self.client = APIClient()
        self.user = create_user()
        self.client.force_authenticate(self.user)

    def test_retrieve_ingredients(self):
        """Test to retrieve a list of ingredients"""
        Ingredient.objects.create(user=self.user, name='test Ingredient')
        Ingredient.objects.create(user=self.user, name='test Ingredient2')
        res = self.client.get(INGREDIENTS_URL)

        ingredients = Ingredient.objects.all().order_by('-name')
        serializer = IngredientSerializer(ingredients, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_ingredients_list_limited_to_user(self):
        """Test list of ingredients is limited to one auth user"""
        new_user = create_user(email='newuser@example.com')
        Ingredient.objects.create(user=new_user, name='test Ingredient')
        Ing = Ingredient.objects.create(user=self.user, name='test Ingredient2')

        res = self.client.get(INGREDIENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], Ing.name)
        self.assertEqual(res.data[0]['id'], Ing.id)

    def test_update_Ingredient(self):
        """Test Partial update of a recipe"""
        in_1 = Ingredient.objects.create(user=self.user, name='test Ing')
        payload = {'name': 'new name'}
        url = detail_url(in_1.id)
        res = self.client.patch(url, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        in_1.refresh_from_db()
        self.assertEqual(in_1.name, payload['name'])

    def test_delete_Ingredient(self):
        """Test deleting an ingredient successful"""
        in_1 = Ingredient.objects.create(user=self.user, name='test Ing')
        url = detail_url(in_1.id)
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        ingredients = Ingredient.objects.filter(user=self.user)
        self.assertFalse(ingredients.exists())

    def test_filter_ingredients_assigned_to_recipes(self):
        """Test listing ingredients by those assigned to recipes"""
        in1 = Ingredient.objects.create(user=self.user, name='test1')
        in2 = Ingredient.objects.create(user=self.user, name='test2')
        recipe = Recipe.objects.create(
            title='test Recipe',
            time_minutes=5,
            price=Decimal('4.50'),
            user=self.user,
        )
        recipe.Ingredient.add(in1)
        res = self.client.get(INGREDIENTS_URL, {'assigned_only': 1})
        s1 = IngredientSerializer(in1)
        s2 = IngredientSerializer(in2)
        self.assertIn(s1.data, res.data)
        self.assertNotIn(s2.data, res.data)

    def test_filtered_ingredients_unique(self):
        in1 = Ingredient.objects.create(user=self.user, name='Eggs')
        Ingredient.objects.create(user=self.user, name='Lentils')
        recipe = Recipe.objects.create(
            title='test Recipe',
            time_minutes=5,
            price=Decimal('4.50'),
            user=self.user,
        )
        recipe2 = Recipe.objects.create(
            title='test Recipe2',
            time_minutes=5,
            price=Decimal('4.50'),
            user=self.user,
        )
        recipe.Ingredient.add(in1)
        recipe2.Ingredient.add(in1)
        res = self.client.get(INGREDIENTS_URL, {'assigned_only': 1})
        self.assertEqual(len(res.data), 1)




