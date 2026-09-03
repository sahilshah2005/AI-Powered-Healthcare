from django.test import TestCase
from django.core.management import call_command
from data_mining.utils import run_kmeans, run_apriori
from etl.models import PatientFact

class DataMiningTestCase(TestCase):
    def setUp(self):
        call_command('run_etl', force=True)

    def test_kmeans_clustering_execution(self):
        """Test K-Means execution, feature scaling, elbow data, and cluster profiles."""
        results = run_kmeans(n_clusters=3)
        self.assertIn('samples', results)
        self.assertIn('summary', results)
        self.assertIn('elbow_data', results)
        self.assertIn('profiles', results)

        # Verify cluster distribution
        summary = results['summary']
        total_clustered = sum(summary.values())
        self.assertEqual(total_clustered, PatientFact.objects.count())

    def test_apriori_association_mining(self):
        """Test Apriori frequent itemsets, support, confidence, and lift calculation."""
        rules = run_apriori(min_support=0.05, min_confidence=0.5, min_lift=1.0)
        self.assertIsInstance(rules, list)
        if len(rules) > 0:
            rule = rules[0]
            self.assertIn('antecedents', rule)
            self.assertIn('consequents', rule)
            self.assertIn('support', rule)
            self.assertIn('confidence', rule)
            self.assertIn('lift', rule)
            self.assertGreaterEqual(rule['lift'], 1.0)
