from django.test import TestCase
from django.core.management import call_command
from etl.models import (
    DimGender, DimAgeGroup, DimChestPainType, DimRestECG,
    DimCholesterolCategory, DimBPCategory, DimHeartRateCategory,
    PatientFact, ETLLog
)

class ETLPipelineTestCase(TestCase):
    def test_etl_execution_and_schema_integrity(self):
        """Test ETL extracts from CSV, applies transformations, and populates dimensional Star Schema."""
        call_command('run_etl', force=True)

        # Verify fact count matches CSV rows
        fact_count = PatientFact.objects.count()
        self.assertEqual(fact_count, 1000)

        # Verify dimensions populated
        self.assertEqual(DimGender.objects.count(), 2)
        self.assertGreaterEqual(DimAgeGroup.objects.count(), 5)
        self.assertEqual(DimChestPainType.objects.count(), 4)
        self.assertEqual(DimRestECG.objects.count(), 3)
        self.assertEqual(DimCholesterolCategory.objects.count(), 3)
        self.assertEqual(DimBPCategory.objects.count(), 3)
        self.assertEqual(DimHeartRateCategory.objects.count(), 3)

        # Verify ETL logging
        latest_log = ETLLog.objects.latest('started_at')
        self.assertEqual(latest_log.status, 'SUCCESS')
        self.assertEqual(latest_log.records_loaded, 1000)
        self.assertEqual(latest_log.records_extracted, 1000)

        # Verify referential integrity
        fact = PatientFact.objects.first()
        self.assertIsNotNone(fact.gender)
        self.assertIsNotNone(fact.age_group)
        self.assertIsNotNone(fact.cp_type)
        self.assertIsNotNone(fact.rest_ecg)
        self.assertIn(fact.gender.gender_name, ['Male', 'Female'])
