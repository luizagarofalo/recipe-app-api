from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status


CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')


def create_user(**params):
    return get_user_model().objects.create_user(**params)


class PublicUserApiTests(TestCase):

    def setUp(self):
        self.client = APIClient()

    def test_create_valid_user_successful(self):
        payload = {
            'email': 'hi@adalovelace.com',
            'password': 'testpass',
            'name': 'Ada Lovelace',
        }

        response = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(**response.data)
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', response.data)

    def test_create_user_already_exists(self):
        payload = {
            'email': 'hi@adalovelace.com',
            'password': 'testpass',
            'name': 'Ada Lovelace'
        }

        create_user(**payload)
        response = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_user_password_too_short(self):
        payload = {
            'email': 'hi@adalovelace.com',
            'password': 'pw',
            'name': 'Ada Lovelace'
        }

        response = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(
            email=payload['email']
        ).exists()
        self.assertFalse(user_exists)

    def test_create_token_for_user(self):
        payload = {
            'email': 'hi@adalovelace.com',
            'password': 'testpass',
            'name': 'Ada Lovelace'
        }
        create_user(**payload)
        response = self.client.post(TOKEN_URL, payload)
        self.assertIn('token', response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_token_invalid_credentials(self):
        user = {
            'email': 'hi@adalovelace.com',
            'password': 'testpass',
            'name': 'Ada Lovelace'
        }
        create_user(**user)

        payload = {
            'email': 'hi@adalovelace.com',
            'password': 'wrongpass',
            'name': 'Ada Lovelace'
        }

        response = self.client.post(TOKEN_URL, payload)
        self.assertNotIn('token', response.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_for_non_existing_user(self):
        payload = {
            'email': 'hi@adalovelace.com',
            'password': 'testpass',
            'name': 'Ada Lovelace'
        }

        response = self.client.post(TOKEN_URL, payload)
        self.assertNotIn('token', response.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_missing_field(self):
        response = self.client.post(TOKEN_URL, {'email': 'a', 'password': ''})
        self.assertNotIn('token', response.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)