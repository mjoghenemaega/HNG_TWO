from rest_framework.test import APITestCase, APIClient
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
        self.client = APIClient()
        self.user = User.objects.create_user(email='test@example.com', password='password', firstName='John', lastName='Doe')
        self.client.force_authenticate(user=self.user)

    def test_create_organisation_successfully(self):
        url = reverse('organisation-list')
        data = {
            'name': 'Test Organisation',
            'description': 'This is a test organisation'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['status'], 'success')
        self.assertEqual(response.data['data']['name'], 'Test Organisation')

    def test_get_user_organisations(self):
        url = reverse('organisation-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['status'], 'success')
        self.assertIsInstance(response.data['data'], list)

    def test_user_cannot_see_other_organisations(self):
        url = reverse('organisation-list')
        other_user = User.objects.create_user(email='other@example.com', password='password', firstName='Jane', lastName='Doe')
        other_org = Organisation.objects.create(name='Other Organisation')
        other_org.users.add(other_user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['status'], 'success')
        self.assertNotIn(other_org.name, [org['name'] for org in response.data['data']])