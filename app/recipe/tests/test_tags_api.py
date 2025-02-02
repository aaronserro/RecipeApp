"""
Tests for the tags API
"""
from decimal import Decimal
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from core.models import Tag
from core.models import Recipe
from recipe.serializers import TagSerializer

TAGS_URL = reverse('recipe:tag-list')


def detail_url(tag_id):
    """Create and return a tag detail url"""
    return reverse('recipe:tag-detail', args=[tag_id])


def create_user(email='user@example.com', password='testpass123'):
    return get_user_model().objects.create_user(email=email, password=password)


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


class PublicTagsApiTests(TestCase):
    """Test unauthenticaed API requests"""
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(TAGS_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class privateTagsApiTests(TestCase):
    """Tests Authorized API requests"""
    def setUp(self):
        self.client = APIClient()
        self.user = create_user()
        self.client.force_authenticate(self.user)

    def test_retrieve_tags(self):
        """Test retrieveing a list of tags"""
        Tag.objects.create(user=self.user, name='vegan')
        Tag.objects.create(user=self.user, name='Dessert')

        res = self.client.get(TAGS_URL)
        tags = Tag.objects.all().order_by('-name')
        serializer = TagSerializer(tags, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def tags_limited_to_user(self):
        """Test list of tags limited to authenticated user"""
        other_user = create_user(email='user2@example.com')
        Tag.objects.create(user=other_user, name='vegan')
        tag = Tag.objects.create(user=self.user, name='Dessert')
        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], tag.name)
        self.assertEqual(res.data[0]['id'], tag.id)

    def test_update_tag(self):
        """Test updating a Tag"""
        tag = Tag.objects.create(user=self.user, name='After Dinner')
        payload = {
            'name': 'new name'
        }

        url = detail_url(tag.id)

        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        tag.refresh_from_db()
        self.assertEqual(tag.name, payload['name'])

    def test_delete_tag(self):
        """Test whether deleting a tag is successful"""
        tag = Tag.objects.create(user=self.user, name='After Dinner')
        url = detail_url(tag.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        tags = Tag.objects.filter(user=self.user)
        self.assertFalse(tags.exists())

    def test_filter_tags_assigned_to_recipes(self):
        """Test listing ingredients by those assigned to recipes"""
        in1 = Tag.objects.create(user=self.user, name='test1')
        in2 = Tag.objects.create(user=self.user, name='test2')
        recipe = Recipe.objects.create(
            title='test Recipe',
            time_minutes=5,
            price=Decimal('4.50'),
            user=self.user,
        )
        recipe.tags.add(in1)
        res = self.client.get(TAGS_URL, {'assigned_only': 1})
        s1 = TagSerializer(in1)
        s2 = TagSerializer(in2)
        self.assertIn(s1.data, res.data)
        self.assertNotIn(s2.data, res.data)

    def test_filtered_tags_unique(self):
        in1 = Tag.objects.create(user=self.user, name='Eggs')
        Tag.objects.create(user=self.user, name='Lentils')
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
        recipe.tags.add(in1)
        recipe2.tags.add(in1)
        res = self.client.get(TAGS_URL, {'assigned_only': 1})
        self.assertEqual(len(res.data), 1)




