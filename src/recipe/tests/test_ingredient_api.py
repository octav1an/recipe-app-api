"""
Test for the ingredients API
"""
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient


from core.models import Ingredient

from recipe.serializers import IngredientSerializer

INGREDIENTS_URL = reverse('recipe:ingredient-list')


def detail_url(ingredient_id):
    return reverse('recipe:ingredient-detail', args=[ingredient_id])


def create_user(email='user@example.com', password='testpass123'):
    """Create and return a user"""
    return get_user_model().objects.create_user(email, password)


def create_ingredient(user, **params):
    defaults = {
        'name': 'Test ingredient'
    }

    defaults.update(params)

    ingredient = Ingredient.objects.create(user=user, **defaults)
    return ingredient


class PublicIngredientsApiTests(TestCase):
    """Test unauthenticated API requests"""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test auth is required for retrieving ingredients"""
        res = self.client.get(INGREDIENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngredientsApiTests(TestCase):
    """Test authenticated API requests"""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user()
        self.client.force_authenticate(self.user)

    def test_retrieve_ingredients(self):
        """Test retrieving a list of ingredients"""
        create_ingredient(self.user)
        create_ingredient(self.user)

        res = self.client.get(INGREDIENTS_URL)
        ingredients = Ingredient.objects.all().order_by('-name')
        serializer = IngredientSerializer(ingredients, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_ingredient_limited_to_user(self):
        """Test list of ingredients limited to auth user"""
        other_user = create_user(email='user2@example.com')
        create_ingredient(user=other_user)
        create_ingredient(user=self.user)

        res = self.client.get(INGREDIENTS_URL)
        ingredients = Ingredient.objects.filter(user=self.user)
        serializer = IngredientSerializer(ingredients, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_update_ingredient(self):
        """Test updating an ingredient"""
        ingredient = create_ingredient(self.user, name="Milk")

        payload = {
            'name': 'Honey'
        }
        res = self.client.patch(detail_url(ingredient.id), payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        ingredient.refresh_from_db()
        self.assertEqual(ingredient.name, payload['name'])

    def test_delete_ingredient(self):
        """Test deleting an ingredient successfully"""
        ingredient = create_ingredient(self.user)

        res = self.client.delete(detail_url(ingredient.id))

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        qs = Ingredient.objects.filter(user=self.user)
        self.assertFalse(qs.exists())
