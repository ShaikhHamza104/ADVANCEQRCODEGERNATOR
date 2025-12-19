from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse

class AuthTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='password123')

    def test_login(self):
        response = self.client.login(username='testuser', password='password123')
        self.assertTrue(response)

    def test_logout(self):
        self.client.login(username='testuser', password='password123')
        
        # Verify we are logged in
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200) # Should be 200 if logged in
        
        # Perform logout (Using POST to match template form)
        response = self.client.post(reverse('logout'))
        
        # Verify redirect
        self.assertRedirects(response, reverse('home'))
        
        # Verify we are logged out by checking access to dashboard (should redirect to login)
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith(reverse('login')))