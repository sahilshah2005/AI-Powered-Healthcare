from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.conf import settings
from django.contrib import messages
from django.http import HttpResponse
import os
import joblib
import pandas as pd
import json
import csv
import io
from .forms import PredictionForm
from .models import PredictionHistory
from sklearn.inspection import permutation_importance

# Module-level cache for models
MODEL_CACHE = {}

def get_model(model_name):
    if model_name in MODEL_CACHE:
        return MODEL_CACHE[model_name]
    
    model_path = os.path.join(settings.BASE_DIR, 'models', f'{model_name}.pkl')
    if os.path.exists(model_path):
        model = joblib.load(model_path)
        MODEL_CACHE[model_name] = model
        return model
    return None

FEATURE_COLUMNS = ['age', 'sex', 'cp', 'trestbps', 'chol', 'fbs', 'restecg', 'thalach', 'exang', 'oldpeak', 'slope', 'ca', 'thal']

@login_required
def predict_heart_disease(request):
    prediction = None
    probability = None
    feature_importance_json = None
    prediction_label = None
    model_used = None
    
    if request.method == 'POST':
        form = PredictionForm(request.POST)
        if form.is_valid():
            input_dict = form.cleaned_data
            model_name = input_dict.pop('model_choice')
            
            # Reorder exactly as trained
            input_data = {feat: input_dict[feat] for feat in FEATURE_COLUMNS}
            input_df = pd.DataFrame([input_data])
            
            model = get_model(model_name)
            
            if not model:
                messages.error(request, f"Model {model_name} not found. Please run 'python manage.py train_models' first.")
            else:
                pred = model.predict(input_df)[0]
                
                if hasattr(model, 'predict_proba'):
                    prob = model.predict_proba(input_df)[0]
                    probability = round(prob[1] * 100, 2)
                else:
                    probability = 100 if pred == 1 else 0
                    
                prediction_label = "Higher Likelihood" if pred == 1 else "Lower Likelihood"
                model_used = dict(form.fields['model_choice'].choices).get(model_name, model_name)
                
                # Feature importance
                importances = []
                try:
                    # Model is a pipeline. The actual classifier is the last step.
                    classifier = model.steps[-1][1]
                    if hasattr(classifier, 'feature_importances_'):
                        importances = classifier.feature_importances_.tolist()
                    elif hasattr(classifier, 'coef_'):
                        importances = [abs(x) for x in classifier.coef_[0]]
                    
                    if importances:
                        total = sum(importances)
                        if total > 0:
                            importances = [round((i/total)*100, 2) for i in importances]
                        feature_importance_json = json.dumps({
                            'labels': FEATURE_COLUMNS,
                            'data': importances
                        })
                except Exception as e:
                    pass
                
                prediction = pred
                # Save to history
                PredictionHistory.objects.create(
                    user=request.user,
                    **input_data,
                    model_used=model_used,
                    prediction=pred,
                    prediction_label=prediction_label,
                    probability=probability,
                    feature_importance_json=feature_importance_json
                )
    else:
        form = PredictionForm()
        
    return render(request, 'prediction/predict.html', {
        'form': form,
        'prediction': prediction,
        'prediction_label': prediction_label,
        'probability': probability,
        'feature_importance': feature_importance_json,
        'model_used': model_used
    })

@login_required
def prediction_history(request):
    history = PredictionHistory.objects.filter(user=request.user).order_by('-created_at')
    
    result_filter = request.GET.get('result')
    if result_filter in ['0', '1']:
        history = history.filter(prediction=int(result_filter))
        
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    if start_date:
        history = history.filter(created_at__gte=start_date)
    if end_date:
        history = history.filter(created_at__lte=end_date)
        
    paginator = Paginator(history, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'prediction/history.html', {'page_obj': page_obj})

@login_required
def prediction_detail(request, pk):
    prediction = get_object_or_404(PredictionHistory, pk=pk, user=request.user)
    return render(request, 'prediction/prediction_detail.html', {'prediction': prediction})

@login_required
def model_comparison(request):
    metrics_path = os.path.join(settings.BASE_DIR, 'models', 'model_metrics.json')
    metrics = {}
    if os.path.exists(metrics_path):
        with open(metrics_path, 'r') as f:
            metrics = json.load(f)
            
    return render(request, 'prediction/model_comparison.html', {'metrics': metrics})

@login_required
def batch_predict(request):
    results = None
    
    # Handle CSV download request from previously uploaded file cached in session
    if request.method == 'POST' and request.POST.get('download'):
        csv_data = request.session.get('last_batch_predictions')
        if csv_data:
            response = HttpResponse(csv_data, content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="batch_predictions.csv"'
            return response
        else:
            messages.error(request, "No batch prediction session found. Please upload a file first.")
            return render(request, 'prediction/batch.html')

    if request.method == 'POST' and request.FILES.get('csv_file'):
        csv_file = request.FILES['csv_file']
        if not csv_file.name.endswith('.csv'):
            messages.error(request, "Please upload a valid CSV file.")
            return render(request, 'prediction/batch.html')
            
        try:
            df = pd.read_csv(csv_file)
            # Check required feature columns
            missing_cols = [col for col in FEATURE_COLUMNS if col not in df.columns]
            if missing_cols:
                messages.error(request, f"Missing required columns in CSV: {', '.join(missing_cols)}")
                return render(request, 'prediction/batch.html')
                
            model = get_model('RandomForestClassifier')
            if not model:
                messages.error(request, "Model pipeline not found. Please train models first.")
                return render(request, 'prediction/batch.html')
                
            X = df[FEATURE_COLUMNS]
            predictions = model.predict(X)
            probs = model.predict_proba(X)[:, 1] if hasattr(model, 'predict_proba') else predictions
            
            df['prediction'] = predictions
            df['probability'] = [round(float(p) * 100, 2) for p in probs]
            df['prediction_label'] = df['prediction'].apply(lambda x: "Higher Likelihood" if x == 1 else "Lower Likelihood")
            
            # Cache CSV output in session for one-click download
            request.session['last_batch_predictions'] = df.to_csv(index=False)
            
            results = {
                'total': len(df),
                'high_risk': int((df['prediction'] == 1).sum()),
                'low_risk': int((df['prediction'] == 0).sum()),
                'preview': df.head(10).to_dict('records')
            }
                
        except Exception as e:
            messages.error(request, f"Error processing file: {str(e)}")
            
    return render(request, 'prediction/batch.html', {'results': results})

