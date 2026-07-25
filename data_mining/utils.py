import pandas as pd
from sklearn.cluster import KMeans
from mlxtend.frequent_patterns import apriori, association_rules
from etl.models import PatientFact

def get_patient_dataframe():
    facts = PatientFact.objects.select_related('gender', 'cp_type', 'rest_ecg').all()
    data = []
    for f in facts:
        data.append({
            'age': f.age,
            'sex': f.gender.gender_name,
            'cp': f.cp_type.cp_name,
            'trestbps': f.trestbps,
            'chol': f.chol,
            'fbs': 'Yes' if f.fbs else 'No',
            'restecg': f.rest_ecg.ecg_result,
            'thalach': f.thalach,
            'exang': 'Yes' if f.exang else 'No',
            'target': 'Heart Disease' if f.target else 'Normal'
        })
    return pd.DataFrame(data)

def run_kmeans():
    df = get_patient_dataframe()
    if df.empty: return []
    
    # We will cluster based on age, cholesterol, resting bp, max heart rate
    X = df[['age', 'chol', 'trestbps', 'thalach']].dropna()
    
    kmeans = KMeans(n_clusters=3, random_state=42)
    clusters = kmeans.fit_predict(X)
    
    X['Cluster'] = clusters
    
    # Map cluster numbers to labels based on average cholesterol
    # Higher cholesterol -> Higher risk
    cluster_centers = X.groupby('Cluster').mean()
    sorted_clusters = cluster_centers.sort_values(by='chol').index.tolist()
    
    risk_mapping = {
        sorted_clusters[0]: 'Low Risk',
        sorted_clusters[1]: 'Medium Risk',
        sorted_clusters[2]: 'High Risk'
    }
    
    X['Risk_Level'] = X['Cluster'].map(risk_mapping)
    
    # Return sample for visualization
    results = X[['age', 'chol', 'trestbps', 'thalach', 'Risk_Level']].head(50).to_dict('records')
    
    # Return aggregation
    summary = X['Risk_Level'].value_counts().to_dict()
    
    return {'samples': results, 'summary': summary}

def run_apriori():
    df = get_patient_dataframe()
    if df.empty: return []
    
    # Apriori requires categorical data (one-hot encoded)
    # We will convert numeric variables to categories
    df['age_cat'] = pd.cut(df['age'], bins=[0, 40, 60, 100], labels=['Young', 'Middle-Aged', 'Senior'])
    df['chol_cat'] = pd.cut(df['chol'], bins=[0, 200, 240, 600], labels=['Normal Chol', 'Borderline Chol', 'High Chol'])
    df['bp_cat'] = pd.cut(df['trestbps'], bins=[0, 120, 140, 300], labels=['Normal BP', 'Elevated BP', 'High BP'])
    
    apriori_df = df[['age_cat', 'sex', 'cp', 'chol_cat', 'bp_cat', 'fbs', 'exang', 'target']]
    
    # One hot encoding
    encoded_df = pd.get_dummies(apriori_df).astype(bool)
    
    # Run apriori
    frequent_itemsets = apriori(encoded_df, min_support=0.1, use_colnames=True)
    
    if frequent_itemsets.empty:
        return []
        
    rules = association_rules(frequent_itemsets, metric="confidence", min_threshold=0.6)
    
    # Filter rules that imply target_Heart Disease
    target_rules = rules[rules['consequents'] == frozenset({'target_Heart Disease'})]
    
    # Format rules
    formatted_rules = []
    for _, row in target_rules.iterrows():
        formatted_rules.append({
            'antecedents': ', '.join(list(row['antecedents'])),
            'support': round(row['support'], 3),
            'confidence': round(row['confidence'], 3),
            'lift': round(row['lift'], 3)
        })
        
    # Sort by lift and return top 10
    formatted_rules.sort(key=lambda x: x['lift'], reverse=True)
    return formatted_rules[:10]
