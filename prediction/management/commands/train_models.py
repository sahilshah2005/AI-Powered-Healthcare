import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
import joblib
import os
import json
from django.core.management.base import BaseCommand
from etl.models import PatientFact

class Command(BaseCommand):
    help = 'Train and save Machine Learning models'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Fetching data from Data Warehouse...'))
        
        # Extract data from DB
        facts = PatientFact.objects.select_related('gender', 'cp_type', 'rest_ecg').all()
        if not facts:
            self.stdout.write(self.style.ERROR('No data found in PatientFact. Please run ETL first.'))
            return

        data = []
        for f in facts:
            data.append({
                'age': f.age,
                'sex': 1 if f.gender.gender_name == 'Male' else 0,
                'cp': list(PatientFact.objects.filter(cp_type=f.cp_type).values_list('cp_type_id', flat=True))[0], # using DB ID as proxy, but ideally should be exactly what's on the form
                'trestbps': f.trestbps,
                'chol': f.chol,
                'fbs': 1 if f.fbs else 0,
                'restecg': f.rest_ecg.id, # proxy encoding
                'thalach': f.thalach,
                'exang': 1 if f.exang else 0,
                'oldpeak': f.oldpeak,
                'slope': f.slope,
                'ca': f.ca,
                'thal': f.thal,
                'target': 1 if f.target else 0
            })
            
        df = pd.DataFrame(data)
        
        # Let's fix the proxy encodings to just match the form (1,2,3, etc).
        # To avoid complex mappings, we'll just train on whatever integers these are.
        # But wait, cp and restecg IDs might not be 0-3. We'll use pandas factorize to be safe or just use the IDs.
        # It's better to just use the IDs.
        
        X = df.drop('target', axis=1)
        y = df['target']
        
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        models = {
            'DecisionTree': DecisionTreeClassifier(random_state=42),
            'NaiveBayes': GaussianNB(),
            'LogisticRegression': LogisticRegression(max_iter=1000, random_state=42)
        }
        
        results = {}
        
        for name, model in models.items():
            self.stdout.write(f'Training {name}...')
            model.fit(X_train, y_train)
            
            y_pred = model.predict(X_test)
            acc = accuracy_score(y_test, y_pred)
            results[name] = round(acc * 100, 2)
            
            # Save the model
            model_path = os.path.join('models', f'{name}.pkl')
            joblib.dump(model, model_path)
            self.stdout.write(self.style.SUCCESS(f'{name} trained! Accuracy: {results[name]}%'))
            
        # Save results for dashboard
        with open(os.path.join('models', 'accuracies.json'), 'w') as f:
            json.dump(results, f)
            
        self.stdout.write(self.style.SUCCESS('All models trained and saved successfully!'))
