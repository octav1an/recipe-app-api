"""
Tests for the tags API
"""
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Tag

from recipe.serializers import TagSerializer

TAGS_URL = reverse('recipe:tag-list')


def detail_url(tag_id):
    """Create and return a tag detail URL"""
    return reverse('recipe:tag-detail', args=[tag_id])


def create_user(email='user@example.com', password='testpass123'):
    """Create and return a user"""
    return get_user_model().objects.create_user(email, password)


def create_tag(user, **params):
    defaults = {
        'name': 'Test tag',
    }

    defaults.update(params)

    tag = Tag.objects.create(user=user, **defaults)
    return tag


class PublicTagsApiTests(TestCase):
    """Test unauthenticated API requests"""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test auth is required for retrieving tags"""
        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagsApiTest(TestCase):
    """Test authenticated API requests"""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user()
        self.client.force_authenticate(self.user)

    def test_retrieve_tags(self):
        """Test retrieving a list of tags"""
        create_tag(user=self.user, name='Vegan')
        create_tag(user=self.user, name='Dessert')

        res = self.client.get(TAGS_URL)

        tags = Tag.objects.all().order_by('-name')
        serializer = TagSerializer(tags, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_tag_list_limited_to_user(self):
        """Test list of tags is limited to authenticated user"""
        user2 = create_user(email='user2@example.com')

        create_tag(user=user2)
        create_tag(user=self.user)

        res = self.client.get(TAGS_URL)

        tags = Tag.objects.filter(user=self.user)
        serializer = TagSerializer(tags, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    # def test_get_tag_detail(self):
    #     """Test retrieving a tag"""
    #     tag = create_tag(user=self.user)

    #     res = self.client.get(detail_url(tag.id))
    #     serializer = TagSerializer(res.data)

    #     self.assertEqual(res.status_code, status.HTTP_200_OK)
    #     self.assertEqual(res.data, serializer.data)

    def test_update_tag(self):
        """Test updating a tag"""
        tag = create_tag(self.user, name='After Dinner')

        payload = {'name': 'Dessert'}
        res = self.client.patch(detail_url(tag.id), payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        tag.refresh_from_db()
        self.assertEqual(tag.name, payload['name'])

    def test_delete_tag(self):
        """Test deleting a tag"""
        tag = create_tag(self.user)

        res = self.client.delete(detail_url(tag.id))

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Tag.objects.filter(user=self.user).exists())
