"""
Test for the ingredients API
"""

from decimal import Decimal

from core.models import Ingredient, Recipe
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from recipe.serializers import IngredientSerializer

INGREDIENTS_URL = reverse("recipe:ingredient-list")


def detail_url(ingredient_id):
    return reverse("recipe:ingredient-detail", args=[ingredient_id])


def create_user(email="user@example.com", password="testpass123"):
    """Create and return a user"""
    return get_user_model().objects.create_user(email, password)


def create_ingredient(user, **params):
    defaults = {"name": "Test ingredient"}

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
        ingredients = Ingredient.objects.all().order_by("-name")
        serializer = IngredientSerializer(ingredients, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_ingredient_limited_to_user(self):
        """Test list of ingredients limited to auth user"""
        other_user = create_user(email="user2@example.com")
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

        payload = {"name": "Honey"}
        res = self.client.patch(detail_url(ingredient.id), payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        ingredient.refresh_from_db()
        self.assertEqual(ingredient.name, payload["name"])

    def test_delete_ingredient(self):
        """Test deleting an ingredient successfully"""
        ingredient = create_ingredient(self.user)

        res = self.client.delete(detail_url(ingredient.id))

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        qs = Ingredient.objects.filter(user=self.user)
        self.assertFalse(qs.exists())

    def test_filter_ingredients_assigned_to_recipes(self):
        """Test listing ingredients by those assigned to recipes"""
        ing1 = Ingredient.objects.create(user=self.user, name="Apples")
        ing2 = Ingredient.objects.create(user=self.user, name="Turkey")
        recipe = Recipe.objects.create(
            user=self.user, title="Apple Crumble", time_minutes=5, price=Decimal("4.50")
        )
        recipe.ingredients.add(ing1)

        res = self.client.get(INGREDIENTS_URL, {"assigned_only": 1})

        s1 = IngredientSerializer(ing1)
        s2 = IngredientSerializer(ing2)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(s1.data, res.data)
        self.assertNotIn(s2.data, res.data)

    def test_filtered_ingredients_unique(self):
        """Test filtered ingredients returns a unique list"""
        ing = create_ingredient(user=self.user, name="Apples")
        create_ingredient(user=self.user, name="Eggs")
        recipe1 = Recipe.objects.create(
            user=self.user, title="Apple Crumble", time_minutes=5, price=Decimal("4.50")
        )
        recipe1.ingredients.add(ing)
        recipe2 = Recipe.objects.create(
            user=self.user, title="Baked Apples", time_minutes=20, price=Decimal("3.00")
        )
        recipe2.ingredients.add(ing)

        res = self.client.get(INGREDIENTS_URL, {"assigned_only": 1})
        ser = IngredientSerializer(ing)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertIn(ser.data, res.data)
