from django.shortcuts import render
from django.contrib.auth.decorators import login_required
import os
import joblib
import pandas as pd
import json
from .forms import PredictionForm

@login_required
def predict_heart_disease(request):
    prediction = None
    probability = None
    feature_importance = None
    
    if request.method == 'POST':
        form = PredictionForm(request.POST)
        if form.is_valid():
            # Get input data
            input_dict = form.cleaned_data
            model_name = input_dict.pop('model_choice')
            
            # Prepare dataframe for prediction
            input_df = pd.DataFrame([input_dict])
            
            # Load model
            model_path = os.path.join('models', f'{model_name}.pkl')
            if os.path.exists(model_path):
                model = joblib.load(model_path)
                pred = model.predict(input_df)[0]
                
                # Predict probability if available
                if hasattr(model, 'predict_proba'):
                    prob = model.predict_proba(input_df)[0]
                    probability = round(prob[1] * 100, 2)
                else:
                    probability = 100 if pred == 1 else 0
                    
                prediction = "High Risk" if pred == 1 else "Low Risk"
                
                # Explainable AI (Feature Importance)
                features = list(input_dict.keys())
                importances = []
                
                if model_name == 'DecisionTree':
                    importances = model.feature_importances_.tolist()
                elif model_name == 'LogisticRegression':
                    importances = abs(model.coef_[0]).tolist()
                    
                if importances:
                    # Normalize importances
                    total = sum(importances)
                    importances = [round((i/total)*100, 2) for i in importances]
                    feature_importance = json.dumps({
                        'labels': features,
                        'data': importances
                    })
    else:
        form = PredictionForm()
        
    return render(request, 'prediction/predict.html', {
        'form': form,
        'prediction': prediction,
        'probability': probability,
        'feature_importance': feature_importance
    })

@login_required
def bulk_predict(request):
    # Optional logic for CSV bulk upload
    # Left simple for demonstration
    pass
