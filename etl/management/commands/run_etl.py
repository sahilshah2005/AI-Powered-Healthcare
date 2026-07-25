import pandas as pd
import numpy as np
import os
from django.core.management.base import BaseCommand
from etl.models import DimGender, DimAgeGroup, DimChestPainType, DimRestECG, PatientFact

class Command(BaseCommand):
    help = 'Run the ETL pipeline to load data from CSV into the Star Schema'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Starting ETL Process...'))

        csv_path = os.path.join('dataset', 'heart_disease.csv')
        if not os.path.exists(csv_path):
            self.stdout.write(self.style.ERROR(f'Dataset not found at {csv_path}'))
            return

        # 1. Extraction
        self.stdout.write('Extracting data...')
        df = pd.read_csv(csv_path)

        # 2. Transformation (Cleaning & Preprocessing)
        self.stdout.write('Transforming data (Handling Missing Values)...')
        df['chol'] = df['chol'].fillna(df['chol'].mean())
        df['thalach'] = df['thalach'].fillna(df['thalach'].mean())

        # Age Groups
        def get_age_group(age):
            if age < 30: return 'Under 30'
            elif 30 <= age < 40: return '30-39'
            elif 40 <= age < 50: return '40-49'
            elif 50 <= age < 60: return '50-59'
            elif 60 <= age < 70: return '60-69'
            else: return '70 and above'
        
        df['age_group'] = df['age'].apply(get_age_group)

        # Categorical Mappings
        gender_map = {1: 'Male', 0: 'Female'}
        cp_map = {0: 'Typical Angina', 1: 'Atypical Angina', 2: 'Non-anginal Pain', 3: 'Asymptomatic'}
        restecg_map = {0: 'Normal', 1: 'ST-T Wave Abnormality', 2: 'Left Ventricular Hypertrophy'}

        df['gender_name'] = df['sex'].map(gender_map)
        df['cp_name'] = df['cp'].map(cp_map)
        df['restecg_name'] = df['restecg'].map(restecg_map)

        # 3. Loading (Populate Star Schema)
        self.stdout.write('Loading Dimension Tables...')
        
        for g in df['gender_name'].unique():
            DimGender.objects.get_or_create(gender_name=g)
            
        for a in df['age_group'].unique():
            DimAgeGroup.objects.get_or_create(age_range=a)
            
        for c in df['cp_name'].unique():
            DimChestPainType.objects.get_or_create(cp_name=c)
            
        for r in df['restecg_name'].unique():
            DimRestECG.objects.get_or_create(ecg_result=r)

        self.stdout.write('Loading Fact Table...')
        
        # Clear existing facts to avoid duplicates on re-run
        PatientFact.objects.all().delete()
        
        facts_to_create = []
        for index, row in df.iterrows():
            gender = DimGender.objects.get(gender_name=row['gender_name'])
            age_group = DimAgeGroup.objects.get(age_range=row['age_group'])
            cp_type = DimChestPainType.objects.get(cp_name=row['cp_name'])
            rest_ecg = DimRestECG.objects.get(ecg_result=row['restecg_name'])
            
            fact = PatientFact(
                gender=gender,
                age_group=age_group,
                cp_type=cp_type,
                rest_ecg=rest_ecg,
                age=row['age'],
                trestbps=row['trestbps'],
                chol=row['chol'],
                fbs=bool(row['fbs']),
                thalach=row['thalach'],
                exang=bool(row['exang']),
                oldpeak=row['oldpeak'],
                slope=row['slope'],
                ca=row['ca'],
                thal=row['thal'],
                target=bool(row['target'])
            )
            facts_to_create.append(fact)

        PatientFact.objects.bulk_create(facts_to_create)

        self.stdout.write(self.style.SUCCESS(f'Successfully loaded {len(facts_to_create)} records into the Data Warehouse!'))
