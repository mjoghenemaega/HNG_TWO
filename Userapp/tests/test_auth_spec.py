from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from Userapp.models import User, Organisation

class AuthTests(APITestCase):

    def test_register_user_successfully(self):
        url = reverse('register')
        data = {
            "firstName": "John",
            "lastName": "Doe",
            "email": "john.doe@example.com",
            "password": "Password123",
            "phone": "1234567890"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('accessToken', response.data['data'])
        self.assertEqual(response.data['data']['user']['firstName'], 'John')
        self.assertTrue(Organisation.objects.filter(name="John's Organisation").exists())

    def test_login_user_successfully(self):
        user = User.objects.create_user(
            firstName="John",
            lastName="Doe",
            email="john.doe@example.com",
            password="Password123"
        )
        url = reverse('login')
        data = {
            "email": "john.doe@example.com",
            "password": "Password123"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('accessToken', response.data['data'])

    def test_register_user_missing_fields(self):
        url = reverse('register')
        data = {
            "firstName": "John",
            "lastName": "Doe",
            "email": "john.doe@example.com"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 422)
        self.assertIn('errors', response.data)

    def test_register_user_duplicate_email(self):
        User.objects.create_user(
            firstName="John",
            lastName="Doe",
            email="john.doe@example.com",
            password="Password123"
        )
        url = reverse('register')
        data = {
            "firstName": "Jane",
            "lastName": "Doe",
            "email": "john.doe@example.com",
            "password": "Password123",
            "phone": "1234567890"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('errors', response.data)


class OrganisationTests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            firstName="John",
            lastName="Doe",
            email="john.doe@example.com",
            password="Password123"
        )
        self.client.force_authenticate(user=self.user)

    def test_create_organisation_successfully(self):
        url = reverse('organisation-list-create')
        data = {
            "name": "New Organisation",
            "description": "A new organisation"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['data']['name'], 'New Organisation')

    def test_get_user_organisations(self):
        org1 = Organisation.objects.create(name="Org 1")
        org2 = Organisation.objects.create(name="Org 2")
        org1.users.add(self.user)
        org2.users.add(self.user)
        
        url = reverse('organisation-list-create')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['data']), 2)

    def test_user_cannot_see_other_organisations(self):
        other_user = User.objects.create_user(
            firstName="Jane",
            lastName="Doe",
            email="jane.doe@example.com",
            password="Password123"
        )
        org1 = Organisation.objects.create(name="Org 1")
        org1.users.add(other_user)
        
        url = reverse('organisation-list-create')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['data']), 0)