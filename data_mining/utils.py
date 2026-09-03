import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score
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

def run_kmeans(n_clusters=None):
    df = get_patient_dataframe()
    if df.empty:
        return {'samples': [], 'summary': {}, 'profiles': {}, 'elbow_data': {}, 'cluster_centers': {}}
    
    X = df[['age', 'chol', 'trestbps', 'thalach']].dropna()
    if X.empty:
        return {'samples': [], 'summary': {}, 'profiles': {}, 'elbow_data': {}, 'cluster_centers': {}}

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    elbow_data = {'k': [], 'inertia': [], 'silhouette': []}
    
    if n_clusters is None:
        for k in range(2, 11):
            if k >= len(X):
                break
            kmeans = KMeans(n_clusters=k, random_state=42, n_init='auto')
            clusters = kmeans.fit_predict(X_scaled)
            elbow_data['k'].append(k)
            elbow_data['inertia'].append(float(kmeans.inertia_))
            elbow_data['silhouette'].append(float(silhouette_score(X_scaled, clusters)))
        
        n_clusters = 3
    
    n_clusters = min(n_clusters, len(X))
    if n_clusters < 2:
        return {'samples': [], 'summary': {}, 'profiles': {}, 'elbow_data': elbow_data, 'cluster_centers': {}}

    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init='auto')
    clusters = kmeans.fit_predict(X_scaled)
    X['Cluster'] = [f'Cluster {c + 1}' for c in clusters]
    X['target'] = df.loc[X.index, 'target']
    
    cluster_centers_scaled = kmeans.cluster_centers_
    cluster_centers = scaler.inverse_transform(cluster_centers_scaled)
    cluster_centers_dict = {f'Cluster {i+1}': center.tolist() for i, center in enumerate(cluster_centers)}
    
    profiles = {}
    summary = {}
    
    for c in range(1, n_clusters + 1):
        c_name = f'Cluster {c}'
        c_data = X[X['Cluster'] == c_name]
        summary[c_name] = len(c_data)
        profiles[c_name] = {
            'age_mean': float(c_data['age'].mean()) if not c_data.empty else 0,
            'chol_mean': float(c_data['chol'].mean()) if not c_data.empty else 0,
            'trestbps_mean': float(c_data['trestbps'].mean()) if not c_data.empty else 0,
            'thalach_mean': float(c_data['thalach'].mean()) if not c_data.empty else 0,
            'target_dist': c_data['target'].value_counts().to_dict()
        }
    
    samples = X.head(50).to_dict('records')
    
    return {
        'samples': samples,
        'summary': summary,
        'profiles': profiles,
        'elbow_data': elbow_data,
        'cluster_centers': cluster_centers_dict
    }

def run_apriori(min_support=0.1, min_confidence=0.6, min_lift=1.0):
    df = get_patient_dataframe()
    if df.empty: return []
    
    df['age_cat'] = pd.cut(df['age'], bins=[0, 40, 60, 100], labels=['Young', 'Middle-Aged', 'Senior'])
    df['chol_cat'] = pd.cut(df['chol'], bins=[0, 200, 240, 1000], labels=['Normal', 'Borderline', 'High'])
    df['bp_cat'] = pd.cut(df['trestbps'], bins=[0, 120, 140, 300], labels=['Normal', 'Elevated', 'High'])
    
    apriori_df = df[['age_cat', 'sex', 'cp', 'chol_cat', 'bp_cat', 'fbs', 'exang', 'target']]
    
    encoded_df = pd.get_dummies(apriori_df).astype(bool)
    
    frequent_itemsets = apriori(encoded_df, min_support=min_support, use_colnames=True)
    
    if frequent_itemsets.empty:
        return []
        
    rules = association_rules(frequent_itemsets, metric="confidence", min_threshold=min_confidence)
    if rules.empty:
        return []
        
    rules = rules[rules['lift'] >= min_lift]
    
    formatted_rules = []
    for _, row in rules.iterrows():
        formatted_rules.append({
            'antecedents': [str(a) for a in row['antecedents']],
            'consequents': [str(c) for c in row['consequents']],
            'support': round(float(row['support']), 3),
            'confidence': round(float(row['confidence']), 3),
            'lift': round(float(row['lift']), 3)
        })
        
    formatted_rules.sort(key=lambda x: x['lift'], reverse=True)
    return formatted_rules
