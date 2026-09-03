from django.test import TestCase, Client
from django.contrib.auth.models import User

class AccountsAuthenticationTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='drsmith', password='SecurePass456!')

    def test_login_flow(self):
        """Test valid and invalid login flows."""
        # Invalid credentials
        response = self.client.post('/accounts/login/', {'username': 'drsmith', 'password': 'wrongpassword'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid username or password')

        # Valid credentials
        response = self.client.post('/accounts/login/', {'username': 'drsmith', 'password': 'SecurePass456!'}, follow=False)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/dashboard/analytics/')

    def test_registration_flow(self):
        """Test user registration and subsequent login."""
        response = self.client.post('/accounts/register/', {
            'username': 'newclinician',
            'password1': 'ValidPassword789!',
            'password2': 'ValidPassword789!'
        }, follow=False)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username='newclinician').exists())

    def test_authenticated_user_redirect_from_auth_pages(self):
        """Test authenticated user is redirected from login and register."""
        self.client.login(username='drsmith', password='SecurePass456!')
        resp_login = self.client.get('/accounts/login/')
        self.assertEqual(resp_login.status_code, 302)

        resp_register = self.client.get('/accounts/register/')
        self.assertEqual(resp_register.status_code, 302)
