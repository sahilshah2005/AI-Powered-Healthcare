from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.core.management import call_command
from prediction.models import PredictionHistory
from prediction.forms import PredictionForm
import os
from django.conf import settings

class PredictionPipelineTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='cardiodoc', password='SecretPassword123!')
        self.client.login(username='cardiodoc', password='SecretPassword123!')
        
        # Ensure models are trained
        model_path = os.path.join(settings.BASE_DIR, 'models', 'RandomForestClassifier.pkl')
        if not os.path.exists(model_path):
            call_command('train_models')

    def test_form_validation(self):
        """Test validation bounds for clinical inputs."""
        valid_data = {
            'age': 50, 'sex': 1, 'cp': 1, 'trestbps': 120, 'chol': 210,
            'fbs': 0, 'restecg': 0, 'thalach': 160, 'exang': 0, 'oldpeak': 1.0,
            'slope': 1, 'ca': 0, 'thal': 2, 'model_choice': 'LogisticRegression'
        }
        form = PredictionForm(data=valid_data)
        self.assertTrue(form.is_valid())

        invalid_data = valid_data.copy()
        invalid_data['age'] = -5  # Out of valid bounds
        form_invalid = PredictionForm(data=invalid_data)
        self.assertFalse(form_invalid.is_valid())

    def test_prediction_inference_and_persistence(self):
        """Test inference flow, probability output, and database recording."""
        payload = {
            'age': 60, 'sex': 1, 'cp': 0, 'trestbps': 140, 'chol': 260,
            'fbs': 0, 'restecg': 1, 'thalach': 140, 'exang': 1, 'oldpeak': 2.0,
            'slope': 1, 'ca': 1, 'thal': 3, 'model_choice': 'RandomForestClassifier'
        }
        response = self.client.post('/prediction/predict/', data=payload)
        self.assertEqual(response.status_code, 200)

        # Ensure history was stored
        history_entry = PredictionHistory.objects.filter(user=self.user).latest('created_at')
        self.assertIn(history_entry.prediction_label, ['Higher Likelihood', 'Lower Likelihood'])
        self.assertGreaterEqual(history_entry.probability, 0.0)
        self.assertLessEqual(history_entry.probability, 100.0)
