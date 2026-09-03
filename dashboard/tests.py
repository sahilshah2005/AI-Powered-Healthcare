from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.core.management import call_command

class DashboardAndOLAPTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='analyst', password='AnalystPassword123!')
        call_command('run_etl', force=True)

    def test_landing_page_redirect_for_authenticated_users(self):
        """Test landing page redirects logged-in user to dashboard."""
        self.client.login(username='analyst', password='AnalystPassword123!')
        response = self.client.get('/')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/dashboard/analytics/')

    def test_dashboard_authenticated_view(self):
        """Test executive dashboard KPIs and chart data."""
        self.client.login(username='analyst', password='AnalystPassword123!')
        response = self.client.get('/dashboard/analytics/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('total_patients', response.context)
        self.assertEqual(response.context['total_patients'], 1000)

    def test_olap_roll_up_and_slice(self):
        """Test OLAP slicing and roll-up operations."""
        self.client.login(username='analyst', password='AnalystPassword123!')
        # Test slice by Gender=Male
        response = self.client.get('/dashboard/olap/?sex=Male')
        self.assertEqual(response.status_code, 200)
        self.assertIn('total_records', response.context)
        self.assertGreater(response.context['total_records'], 0)
        self.assertLessEqual(response.context['total_records'], 1000)
