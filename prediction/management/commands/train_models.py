import os
import json
import joblib
import pandas as pd
from django.core.management.base import BaseCommand
from django.conf import settings

from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix

class Command(BaseCommand):
    help = 'Train and save Machine Learning models directly from CSV'

    def handle(self, *args, **kwargs):
        data_path = os.path.join(settings.DATASET_DIR, 'heart_disease.csv')
        
        self.stdout.write(self.style.SUCCESS(f'Reading data from {data_path}...'))
        
        if not os.path.exists(data_path):
            self.stdout.write(self.style.ERROR(f'Dataset not found at {data_path}'))
            return
            
        df = pd.read_csv(data_path)
        
        # Handle missing values
        df['chol'] = df['chol'].fillna(df['chol'].mean())
        df['thalach'] = df['thalach'].fillna(df['thalach'].mean())
        
        features = ['age', 'sex', 'cp', 'trestbps', 'chol', 'fbs', 'restecg', 'thalach', 'exang', 'oldpeak', 'slope', 'ca', 'thal']
        X = df[features]
        y = df['target']
        
        # Stratified split
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
        
        models = {
            'LogisticRegression': LogisticRegression(max_iter=1000, random_state=42),
            'DecisionTree': DecisionTreeClassifier(random_state=42),
            'GaussianNB': GaussianNB(),
            'RandomForestClassifier': RandomForestClassifier(random_state=42, n_estimators=100)
        }
        
        models_dir = os.path.join(settings.BASE_DIR, 'models')
        os.makedirs(models_dir, exist_ok=True)
        
        results = {}
        
        cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
        
        for name, clf in models.items():
            self.stdout.write(f'Training {name}...')
            
            pipeline = Pipeline([
                ('scaler', StandardScaler()),
                ('classifier', clf)
            ])
            
            # Cross validation
            cv_scores = cross_val_score(pipeline, X, y, cv=cv, scoring='accuracy')
            
            pipeline.fit(X_train, y_train)
            y_pred = pipeline.predict(X_test)
            
            if hasattr(pipeline, "predict_proba"):
                y_prob = pipeline.predict_proba(X_test)[:, 1]
                roc_auc = roc_auc_score(y_test, y_prob)
            else:
                roc_auc = roc_auc_score(y_test, y_pred)
                
            acc = accuracy_score(y_test, y_pred)
            prec = precision_score(y_test, y_pred)
            rec = recall_score(y_test, y_pred)
            f1 = f1_score(y_test, y_pred)
            cm = confusion_matrix(y_test, y_pred).tolist()
            
            results[name] = {
                'accuracy': round(acc * 100, 2),
                'precision': round(prec * 100, 2),
                'recall': round(rec * 100, 2),
                'f1_score': round(f1 * 100, 2),
                'roc_auc': round(roc_auc * 100, 2),
                'confusion_matrix': cm,
                'cv_mean': round(cv_scores.mean() * 100, 2),
                'cv_std': round(cv_scores.std() * 100, 2)
            }
            
            model_path = os.path.join(models_dir, f'{name}.pkl')
            joblib.dump(pipeline, model_path)
            
            self.stdout.write(self.style.SUCCESS(f'{name} trained! Accuracy: {results[name]["accuracy"]}%'))
            
        metrics_path = os.path.join(models_dir, 'model_metrics.json')
        with open(metrics_path, 'w') as f:
            json.dump(results, f, indent=4)
            
        self.stdout.write(self.style.SUCCESS(f'All models trained. Metrics saved to {metrics_path}'))
