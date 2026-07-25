from django import forms

class PredictionForm(forms.Form):
    age = forms.IntegerField(label='Age (in years)')
    sex = forms.TypedChoiceField(choices=[(1, 'Male'), (0, 'Female')], coerce=int, label='Gender')
    cp = forms.TypedChoiceField(choices=[(0, 'Typical Angina'), (1, 'Atypical Angina'), (2, 'Non-anginal Pain'), (3, 'Asymptomatic')], coerce=int, label='Chest Pain Type')
    trestbps = forms.FloatField(label='Resting Blood Pressure (mm Hg)')
    chol = forms.FloatField(label='Serum Cholestoral (mg/dl)')
    fbs = forms.TypedChoiceField(choices=[(1, 'Yes (> 120 mg/dl)'), (0, 'No')], coerce=int, label='Fasting Blood Sugar')
    restecg = forms.TypedChoiceField(choices=[(0, 'Normal'), (1, 'ST-T wave abnormality'), (2, 'Left ventricular hypertrophy')], coerce=int, label='Resting ECG')
    thalach = forms.FloatField(label='Maximum Heart Rate')
    exang = forms.TypedChoiceField(choices=[(1, 'Yes'), (0, 'No')], coerce=int, label='Exercise Induced Angina')
    oldpeak = forms.FloatField(label='ST Depression (Oldpeak)')
    slope = forms.TypedChoiceField(choices=[(0, 'Upsloping'), (1, 'Flat'), (2, 'Downsloping')], coerce=int, label='Slope of Peak Exercise ST')
    ca = forms.TypedChoiceField(choices=[(0, '0'), (1, '1'), (2, '2'), (3, '3'), (4, '4')], coerce=int, label='Number of Major Vessels')
    thal = forms.TypedChoiceField(choices=[(0, '0'), (1, 'Normal (1)'), (2, 'Fixed Defect (2)'), (3, 'Reversable Defect (3)')], coerce=int, label='Thalassemia')
    
    model_choice = forms.ChoiceField(choices=[
        ('LogisticRegression', 'Logistic Regression'),
        ('DecisionTree', 'Decision Tree'),
        ('NaiveBayes', 'Naive Bayes')
    ], label='Select Model')
