import pandas as pd
import numpy as np
import time
import uuid
from django.core.management.base import BaseCommand
from django.conf import settings
from django.db import transaction
from django.utils import timezone
from etl.models import (
    DimGender, DimAgeGroup, DimChestPainType, DimRestECG,
    DimCholesterolCategory, DimBPCategory, DimHeartRateCategory, DimTime,
    PatientFact, ETLLog
)


class Command(BaseCommand):
    help = 'Run the ETL pipeline to load data from CSV into the Star Schema Data Warehouse'

    def add_arguments(self, parser):
        parser.add_argument('--force', action='store_true', help='Force re-import even if data exists')

    def handle(self, *args, **kwargs):
        force = kwargs.get('force', False)
        batch_id = f"ETL-{uuid.uuid4().hex[:8].upper()}"
        start_time = time.time()

        # Create ETL log entry
        etl_log = ETLLog.objects.create(
            batch_id=batch_id,
            started_at=timezone.now(),
            status='RUNNING'
        )

        self.stdout.write(self.style.SUCCESS(f'\n{"="*60}'))
        self.stdout.write(self.style.SUCCESS(f'  ETL Pipeline Started - Batch: {batch_id}'))
        self.stdout.write(self.style.SUCCESS(f'{"="*60}\n'))

        try:
            # Check if data already loaded
            existing_count = PatientFact.objects.count()
            if existing_count > 0 and not force:
                self.stdout.write(self.style.WARNING(
                    f'Data warehouse already contains {existing_count} records. '
                    f'Use --force to re-import.'
                ))
                etl_log.status = 'SUCCESS'
                etl_log.records_loaded = existing_count
                etl_log.completed_at = timezone.now()
                etl_log.duration_seconds = round(time.time() - start_time, 2)
                etl_log.save()
                return

            # ============================================================
            # PHASE 1: EXTRACTION
            # ============================================================
            self.stdout.write(self.style.MIGRATE_HEADING('Phase 1: Extraction'))

            csv_path = settings.DATASET_DIR / 'heart_disease.csv'
            if not csv_path.exists():
                raise FileNotFoundError(f'Dataset not found at {csv_path}')

            df = pd.read_csv(csv_path)
            etl_log.records_extracted = len(df)
            self.stdout.write(f'  [OK] Extracted {len(df)} records from {csv_path.name}')

            # ============================================================
            # PHASE 2: VALIDATION
            # ============================================================
            self.stdout.write(self.style.MIGRATE_HEADING('\nPhase 2: Validation'))

            # Schema validation
            required_columns = ['age', 'sex', 'cp', 'trestbps', 'chol', 'fbs',
                                'restecg', 'thalach', 'exang', 'oldpeak', 'slope',
                                'ca', 'thal', 'target']
            missing_cols = set(required_columns) - set(df.columns)
            if missing_cols:
                raise ValueError(f'Missing required columns: {missing_cols}')
            self.stdout.write(f'  [OK] Schema validated - {len(required_columns)} required columns present')

            # Data type validation
            valid_mask = pd.Series(True, index=df.index)
            validation_issues = []

            # Numeric range checks
            range_checks = {
                'age': (1, 120), 'trestbps': (50, 300), 'chol': (50, 600),
                'thalach': (40, 250), 'oldpeak': (0, 10), 'fbs': (0, 1),
                'exang': (0, 1), 'sex': (0, 1), 'cp': (0, 3),
                'restecg': (0, 2), 'slope': (0, 2), 'ca': (0, 4),
                'thal': (0, 3), 'target': (0, 1)
            }
            for col, (min_val, max_val) in range_checks.items():
                non_null = df[col].dropna()
                out_of_range = non_null[(non_null < min_val) | (non_null > max_val)]
                if len(out_of_range) > 0:
                    validation_issues.append(f'{col}: {len(out_of_range)} values out of range [{min_val}, {max_val}]')
                    valid_mask[out_of_range.index] = False

            # Missing value analysis
            missing_summary = df.isnull().sum()
            missing_cols_with_nulls = missing_summary[missing_summary > 0]
            for col, count in missing_cols_with_nulls.items():
                self.stdout.write(f'  [WARN] {col}: {count} missing values ({count/len(df)*100:.1f}%)')

            # Duplicate detection
            dup_count = df.duplicated().sum()
            etl_log.duplicates_detected = dup_count
            if dup_count > 0:
                self.stdout.write(f'  [WARN] {dup_count} duplicate rows detected')

            invalid_count = (~valid_mask).sum()
            etl_log.records_validated = int(valid_mask.sum())
            etl_log.records_invalid = int(invalid_count)
            self.stdout.write(f'  [OK] Validated: {etl_log.records_validated} valid, {invalid_count} invalid')

            # Data quality report
            quality_report = {
                'total_records': len(df),
                'valid_records': int(valid_mask.sum()),
                'invalid_records': int(invalid_count),
                'duplicates': int(dup_count),
                'missing_values': {col: int(count) for col, count in missing_cols_with_nulls.items()},
                'validation_issues': validation_issues,
                'column_count': len(df.columns),
                'columns': list(df.columns),
            }
            etl_log.data_quality_report = quality_report

            # ============================================================
            # PHASE 3: TRANSFORMATION
            # ============================================================
            self.stdout.write(self.style.MIGRATE_HEADING('\nPhase 3: Transformation'))

            # Remove duplicates
            if dup_count > 0:
                df = df.drop_duplicates()
                self.stdout.write(f'  [OK] Removed {dup_count} duplicate rows')

            # Handle missing values
            missing_handled = 0
            if df['chol'].isnull().any():
                chol_mean = df['chol'].mean()
                count = df['chol'].isnull().sum()
                df['chol'] = df['chol'].fillna(round(chol_mean, 1))
                missing_handled += count
                self.stdout.write(f'  [OK] Imputed {count} missing chol values with mean ({chol_mean:.1f})')

            if df['thalach'].isnull().any():
                thalach_mean = df['thalach'].mean()
                count = df['thalach'].isnull().sum()
                df['thalach'] = df['thalach'].fillna(round(thalach_mean, 1))
                missing_handled += count
                self.stdout.write(f'  [OK] Imputed {count} missing thalach values with mean ({thalach_mean:.1f})')

            etl_log.missing_values_handled = missing_handled

            # Derived attributes - Age Groups
            def get_age_group(age):
                if age < 30: return 'Under 30'
                elif age < 40: return '30-39'
                elif age < 50: return '40-49'
                elif age < 60: return '50-59'
                elif age < 70: return '60-69'
                else: return '70 and above'

            df['age_group'] = df['age'].apply(get_age_group)

            # Derived attributes - Cholesterol Category
            def get_chol_category(chol):
                if chol < 200: return 'Normal'
                elif chol < 240: return 'Borderline High'
                else: return 'High'

            df['chol_category'] = df['chol'].apply(get_chol_category)

            # Derived attributes - BP Category
            def get_bp_category(bp):
                if bp < 120: return 'Normal'
                elif bp < 140: return 'Elevated'
                else: return 'High'

            df['bp_category'] = df['trestbps'].apply(get_bp_category)

            # Derived attributes - Heart Rate Category
            def get_hr_category(hr):
                if hr < 100: return 'Low'
                elif hr < 170: return 'Normal'
                else: return 'High'

            df['hr_category'] = df['thalach'].apply(get_hr_category)

            # Categorical mappings
            gender_map = {1: 'Male', 0: 'Female'}
            cp_map = {0: 'Typical Angina', 1: 'Atypical Angina', 2: 'Non-anginal Pain', 3: 'Asymptomatic'}
            restecg_map = {0: 'Normal', 1: 'ST-T Wave Abnormality', 2: 'Left Ventricular Hypertrophy'}

            df['gender_name'] = df['sex'].map(gender_map)
            df['cp_name'] = df['cp'].map(cp_map)
            df['restecg_name'] = df['restecg'].map(restecg_map)

            etl_log.records_transformed = len(df)
            self.stdout.write(f'  [OK] Transformed {len(df)} records with derived attributes')

            # ============================================================
            # PHASE 4: LOADING - Star Schema
            # ============================================================
            self.stdout.write(self.style.MIGRATE_HEADING('\nPhase 4: Loading into Star Schema'))

            with transaction.atomic():
                # Load Dimension Tables (with pre-caching)
                self.stdout.write('  Loading dimensions...')

                # DimGender
                gender_cache = {}
                for name in ['Male', 'Female']:
                    obj, _ = DimGender.objects.get_or_create(gender_name=name)
                    gender_cache[name] = obj

                # DimAgeGroup
                age_group_defs = [
                    ('Under 30', 0, 29), ('30-39', 30, 39), ('40-49', 40, 49),
                    ('50-59', 50, 59), ('60-69', 60, 69), ('70 and above', 70, 120)
                ]
                age_group_cache = {}
                for age_range, min_a, max_a in age_group_defs:
                    obj, _ = DimAgeGroup.objects.update_or_create(
                        age_range=age_range,
                        defaults={'min_age': min_a, 'max_age': max_a}
                    )
                    age_group_cache[age_range] = obj

                # DimChestPainType - store cp_code for ML alignment
                cp_cache = {}
                for code, name in cp_map.items():
                    obj, _ = DimChestPainType.objects.update_or_create(
                        cp_code=code,
                        defaults={'cp_name': name}
                    )
                    cp_cache[name] = obj

                # DimRestECG - store ecg_code for ML alignment
                ecg_cache = {}
                for code, name in restecg_map.items():
                    obj, _ = DimRestECG.objects.update_or_create(
                        ecg_code=code,
                        defaults={'ecg_result': name}
                    )
                    ecg_cache[name] = obj

                # DimCholesterolCategory
                chol_cat_defs = [('Normal', 0, 199.9), ('Borderline High', 200, 239.9), ('High', 240, 9999)]
                chol_cache = {}
                for name, min_v, max_v in chol_cat_defs:
                    obj, _ = DimCholesterolCategory.objects.update_or_create(
                        category_name=name,
                        defaults={'min_value': min_v, 'max_value': max_v}
                    )
                    chol_cache[name] = obj

                # DimBPCategory
                bp_cat_defs = [('Normal', 0, 119.9), ('Elevated', 120, 139.9), ('High', 140, 9999)]
                bp_cache = {}
                for name, min_v, max_v in bp_cat_defs:
                    obj, _ = DimBPCategory.objects.update_or_create(
                        category_name=name,
                        defaults={'min_value': min_v, 'max_value': max_v}
                    )
                    bp_cache[name] = obj

                # DimHeartRateCategory
                hr_cat_defs = [('Low', 0, 99.9), ('Normal', 100, 169.9), ('High', 170, 9999)]
                hr_cache = {}
                for name, min_v, max_v in hr_cat_defs:
                    obj, _ = DimHeartRateCategory.objects.update_or_create(
                        category_name=name,
                        defaults={'min_value': min_v, 'max_value': max_v}
                    )
                    hr_cache[name] = obj

                # DimTime
                today = timezone.now().date()
                quarter = (today.month - 1) // 3 + 1
                etl_time, _ = DimTime.objects.get_or_create(
                    etl_date=today,
                    defaults={'year': today.year, 'month': today.month, 'quarter': quarter}
                )

                self.stdout.write('  [OK] All dimension tables populated')

                # Clear existing facts
                deleted_count = PatientFact.objects.all().delete()[0]
                if deleted_count > 0:
                    self.stdout.write(f'  [OK] Cleared {deleted_count} existing fact records')

                # Bulk create fact records
                facts_to_create = []
                for _, row in df.iterrows():
                    fact = PatientFact(
                        gender=gender_cache[row['gender_name']],
                        age_group=age_group_cache[row['age_group']],
                        cp_type=cp_cache[row['cp_name']],
                        rest_ecg=ecg_cache[row['restecg_name']],
                        chol_category=chol_cache.get(row['chol_category']),
                        bp_category=bp_cache.get(row['bp_category']),
                        hr_category=hr_cache.get(row['hr_category']),
                        etl_time=etl_time,
                        age=row['age'],
                        trestbps=row['trestbps'],
                        chol=row['chol'],
                        fbs=bool(row['fbs']),
                        thalach=row['thalach'],
                        exang=bool(row['exang']),
                        oldpeak=row['oldpeak'],
                        slope=int(row['slope']),
                        ca=int(row['ca']),
                        thal=int(row['thal']),
                        target=bool(row['target']),
                        etl_batch_id=batch_id,
                    )
                    facts_to_create.append(fact)

                PatientFact.objects.bulk_create(facts_to_create)
                etl_log.records_loaded = len(facts_to_create)

            # ============================================================
            # COMPLETE
            # ============================================================
            duration = round(time.time() - start_time, 2)
            etl_log.status = 'SUCCESS'
            etl_log.completed_at = timezone.now()
            etl_log.duration_seconds = duration
            etl_log.save()

            self.stdout.write(self.style.SUCCESS(f'\n{"="*60}'))
            self.stdout.write(self.style.SUCCESS(f'  ETL Pipeline Completed Successfully!'))
            self.stdout.write(self.style.SUCCESS(f'  Batch: {batch_id}'))
            self.stdout.write(self.style.SUCCESS(f'  Records: {etl_log.records_loaded} loaded'))
            self.stdout.write(self.style.SUCCESS(f'  Duration: {duration}s'))
            self.stdout.write(self.style.SUCCESS(f'{"="*60}\n'))

        except Exception as e:
            duration = round(time.time() - start_time, 2)
            etl_log.status = 'FAILED'
            etl_log.completed_at = timezone.now()
            etl_log.duration_seconds = duration
            etl_log.error_message = str(e)
            etl_log.save()
            self.stdout.write(self.style.ERROR(f'\n  [ERROR] ETL Failed: {e}'))
            raise
