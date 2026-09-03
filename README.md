# AI-Powered Healthcare Data Warehouse, Data Mining & Heart Disease Risk Analytics Platform

An enterprise-grade, academically defensible full-stack healthcare analytics and data warehousing platform engineered for **Data Warehousing & Mining (DWM)**. Integrates a dimensional **Star Schema**, an automated **ETL Pipeline**, interactive **OLAP Analytics** (Roll-up, Drill-down, Slice, Dice), **Supervised Machine Learning Classifiers** with **Explainable AI (XAI)**, **Unsupervised K-Means Clustering**, and **Apriori Association Rule Mining**.

---

## 📑 Table of Contents
- [Overview](#overview)
- [Problem Statement & Objectives](#problem-statement--objectives)
- [Key Features](#key-features)
- [Architecture & End-to-End Pipeline](#architecture--end-to-end-pipeline)
- [Technology Stack](#technology-stack)
- [DWM Concepts Implemented](#dwm-concepts-implemented)
- [Data Warehouse Design (Star Schema)](#data-warehouse-design-star-schema)
- [ETL Pipeline](#etl-pipeline)
- [OLAP Operations](#olap-operations)
- [Machine Learning & Classification](#machine-learning--classification)
- [Explainable AI (XAI)](#explainable-ai-xai)
- [K-Means Clustering](#k-means-clustering)
- [Apriori Association Rule Mining](#apriori-association-rule-mining)
- [Batch CSV Prediction & History](#batch-csv-prediction--history)
- [Dataset Specifications](#dataset-specifications)
- [Installation & Setup](#installation--setup)
- [Automated Testing](#automated-testing)
- [Limitations & Future Scope](#limitations--future-scope)
- [Medical Disclaimer](#medical-disclaimer)

---

## 🔬 Overview
This system serves as an interactive clinical decision-support and data exploration platform. Instead of operating as a disconnected machine learning demonstration, it builds a rigorous data lifecycle from raw tabular records to transformed analytical dimensions, relational fact storage, multidimensional cubes, and explainable inference.

---

## 🎯 Problem Statement & Objectives
- **Problem:** Clinical cardiovascular data is fragmented across operational records with missing observations, differing measurement scales, and lack of analytical structure suitable for ad-hoc multidimensional querying.
- **Objectives:**
  1. Build an automated Extraction, Validation, Cleaning, Transformation, and Loading (ETL) pipeline.
  2. Implement an 8-dimension Star Schema data warehouse with transaction safety and surrogate keys.
  3. Provide interactive OLAP multidimensional analytical querying (Slice, Dice, Roll-Up, Drill-Down).
  4. Train, evaluate, and persist reproducible scikit-learn classification pipelines (Logistic Regression, Decision Tree, Gaussian Naive Bayes, Random Forest).
  5. Provide feature importance explanations for patient-level predictions.
  6. Discover hidden risk cohorts via normalized K-Means clustering and cardiovascular risk patterns via Apriori association mining.

---

## ✨ Key Features
- **Executive Analytics Dashboard:** Dynamic KPIs (total records, positive/negative rates, active models, ETL status) and responsive Chart.js visualizers.
- **Dimensional Star Schema:** Fact table (`PatientFact`) tied to 8 normalized dimension tables (`DimGender`, `DimAgeGroup`, `DimChestPainType`, `DimRestECG`, `DimCholesterolCategory`, `DimBPCategory`, `DimHeartRateCategory`, `DimTime`).
- **Production ETL Pipeline:** Imputes missing data (`chol`, `thalach`), calculates derived analytical attributes, validates schemas, generates audit reports, and logs batch runs to `ETLLog`.
- **OLAP Engine:** Real-time Slice & Dice multidimensional filtering, Roll-Up summaries by age cohorts, and Drill-Down granular clinical views.
- **Multi-Model Machine Learning:** Trainable pipelines with `StandardScaler` ensuring zero data leakage and identical preprocessing between training and inference.
- **Model Comparison & ROC Curves:** Side-by-side performance matrix (Accuracy, Precision, Recall, F1-Score, ROC-AUC, 5-Fold Cross-Validation, Confusion Matrices).
- **Patient Profiling & Inference:** Real-time single patient prediction with risk percentage, categorical classification, and local feature importance.
- **Batch CSV Analysis:** Bulk patient scoring via CSV upload with schema validation, error detection, preview, and results export.
- **Historical Audit Trail:** Searchable, paginated history of all inference queries per authenticated clinician (`PredictionHistory`).
- **Unsupervised K-Means Mining:** Standardized clustering with Elbow Method inertia evaluation and Silhouette scoring.
- **Apriori Association Mining:** Configurable minimum support, confidence, and lift thresholds mining cardiovascular antecedent rules.

---

## 🏛 Architecture & End-to-End Pipeline

```
                     RAW DATA (heart_disease.csv)
                                  │
                                  ▼
                     ETL PIPELINE (run_etl command)
          [Extract -> Validate -> Clean/Impute -> Transform -> Load]
                                  │
                                  ▼
                     DATA WAREHOUSE (Star Schema)
       ┌──────────────────────────┼──────────────────────────┐
       ▼                          ▼                          ▼
  DIMENSIONS                   FACT TABLE                 ETL LOGS
(8 Normalized)               (PatientFact)              (Operational)
       │                          │                          │
       └──────────────────────────┼──────────────────────────┘
                                  │
                                  ▼
                            OLAP ANALYTICS
          [Roll-Up  •  Drill-Down  •  Slice  •  Dice]
                                  │
             ┌────────────────────┼────────────────────┐
             ▼                    ▼                    ▼
      CLASSIFICATION           CLUSTERING           APRIORI
    (4 ML Pipelines)          (K-Means)           (Rule Mining)
             │                    │                    │
             ▼                    ▼                    ▼
      PREDICTION ENGINE    PATIENT SEGMENTS     FREQUENT PATTERNS
     & EXPLAINABLE AI      & ELBOW ANALYSIS     & LIFT RANKINGS
             │                    │                    │
             └────────────────────┼────────────────────┘
                                  │
                                  ▼
                   INTERACTIVE CLINICAL DASHBOARD
             (Bootstrap 5 • Chart.js • Django Web App)
```

---

## 💻 Technology Stack
- **Backend Framework:** Django 6.1+ / Python 3.10+
- **Data Engineering & ETL:** Pandas, NumPy, Django ORM
- **Machine Learning & Pipeline:** Scikit-Learn (Pipelines, `StandardScaler`, `StratifiedKFold`), Joblib
- **Data Mining:** Mlxtend (Apriori & Association Rules), Scikit-Learn (KMeans, Silhouette Score)
- **Database:** SQLite (default development), PostgreSQL/MySQL compatible via `.env`
- **Frontend & Visualizations:** HTML5, CSS3 Glassmorphism, Bootstrap 5.3, Font Awesome 6.4, Chart.js

---

## 📚 DWM Concepts Implemented
| Syllabus Concept | Implementation in Project |
| :--- | :--- |
| **Data Warehouse** | Central relational repository structured for analytical querying rather than transactional OLTP. |
| **Star Schema** | `PatientFact` surrounded by `DimGender`, `DimAgeGroup`, `DimChestPainType`, `DimRestECG`, `DimCholesterolCategory`, `DimBPCategory`, `DimHeartRateCategory`, `DimTime`. |
| **ETL Pipeline** | Managed batch extraction, validation checks, missing value imputation, discretization, and transactional bulk insertion. |
| **Data Quality & Cleansing** | Range checking, duplicate detection, automated mean imputation for missing biometric attributes. |
| **OLAP: Roll-Up** | Aggregating patient metrics up the age hierarchy (`individual` $\rightarrow$ `age_group`). |
| **OLAP: Drill-Down** | De-aggregating age groups into granular clinical subgroups (`gender` + `chest pain type`). |
| **OLAP: Slice** | Filtering data along a single dimension (e.g., `sex = Male`). |
| **OLAP: Dice** | Multi-dimensional constraint intersections (e.g., `age_group = 50-59` AND `cp_type = Typical Angina` AND `chol_category = High`). |
| **Classification** | Supervised learning comparing Logistic Regression, Decision Trees, Gaussian Naïve Bayes, and Random Forest. |
| **Evaluation Metrics** | Accuracy, Precision, Recall, F1-Score, ROC-AUC, 5-Fold Stratified Cross Validation, Confusion Matrix. |
| **Clustering** | Unsupervised K-Means segmentation utilizing feature standardization, Elbow curve evaluation, and Silhouette scores. |
| **Association Rules** | Apriori transaction mining measuring Support, Confidence, and Lift on discretized clinical conditions. |

---

## 🗄 Data Warehouse Design (Star Schema)

```
                    ┌─────────────────────────┐
                    │        DimGender        │
                    ├─────────────────────────┤
                    │ id (PK)                 │
                    │ gender_name             │
                    └───────────┬─────────────┘
                                │
┌──────────────────────┐        │        ┌─────────────────────────┐
│     DimAgeGroup      │        │        │    DimChestPainType     │
├──────────────────────┤        │        ├─────────────────────────┤
│ id (PK)              │        │        │ id (PK)                 │
│ age_range            ├────────┼───────►│ cp_code (0-3)           │
│ min_age, max_age     │        │        │ cp_name                 │
└──────────────────────┘        │        └─────────────────────────┘
                                ▼
                    ┌─────────────────────────┐
                    │       PatientFact       │
                    ├─────────────────────────┤
                    │ id (PK)                 │
                    │ gender_id (FK)          │
                    │ age_group_id (FK)       │
                    │ cp_type_id (FK)         │
                    │ rest_ecg_id (FK)        │
                    │ chol_category_id (FK)   │
                    │ bp_category_id (FK)     │
                    │ hr_category_id (FK)     │
                    │ etl_time_id (FK)        │
                    │ age                     │
                    │ trestbps, chol, fbs     │
                    │ thalach, exang, oldpeak │
                    │ slope, ca, thal         │
                    │ target (0 or 1)         │
                    │ etl_batch_id            │
                    └───────────┬─────────────┘
                                │
┌──────────────────────┐        │        ┌─────────────────────────┐
│      DimRestECG      │        │        │  DimCholesterolCategory │
├──────────────────────┤        │        ├─────────────────────────┤
│ id (PK)              │◄───────┼────────┤ id (PK)                 │
│ ecg_code (0-2)       │        │        │ category_name           │
│ ecg_result           │        │        │ min_value, max_value    │
└──────────────────────┘        │        └─────────────────────────┘
                                │
┌──────────────────────┐        │        ┌─────────────────────────┐
│    DimBPCategory     │        │        │   DimHeartRateCategory  │
├──────────────────────┤        │        ├─────────────────────────┤
│ id (PK)              ├────────┼───────►│ id (PK)                 │
│ category_name        │        │        │ category_name           │
│ min_value, max_value │        │        │ min_value, max_value    │
└──────────────────────┘        │        └─────────────────────────┘
                                ▼
                    ┌─────────────────────────┐
                    │         DimTime         │
                    ├─────────────────────────┤
                    │ id (PK)                 │
                    │ etl_date, year, month   │
                    │ quarter                 │
                    └─────────────────────────┘
```

---

## ⚙️ ETL Pipeline
The ETL pipeline is executed using the custom Django management command:
```bash
python manage.py run_etl --force
```

### 1. Extraction
- Reads `dataset/heart_disease.csv` (1,000 records).
- Resolves paths securely via `settings.DATASET_DIR`.

### 2. Validation
- Schema conformity checks for all 14 mandatory attributes.
- Physiological boundary validation (e.g., $1 \le \text{age} \le 120$, $50 \le \text{chol} \le 600$).
- Detection of duplicate records and logging of missing cells.

### 3. Transformation & Cleansing
- Imputes missing numerical values (`chol`: 50 nulls, `thalach`: 50 nulls) using column means calculated from valid observations.
- Discretizes continuous metrics into analytical categories:
  - Age cohorts: *Under 30*, *30-39*, *40-49*, *50-59*, *60-69*, *70 and above*.
  - Cholesterol: *Normal* (<200), *Borderline High* (200-239), *High* ($\ge$240).
  - Resting Blood Pressure: *Normal* (<120), *Elevated* (120-139), *High* ($\ge$140).
  - Maximum Heart Rate: *Low* (<100), *Normal* (100-169), *High* ($\ge$170).

### 4. Loading
- Pre-caches dimension surrogate keys to avoid N+1 query bottlenecks.
- Loads 1,000 records into `PatientFact` using `bulk_create` within a `transaction.atomic()` block.
- Records audit metrics in `ETLLog` (batch ID, duration, status, quality report).

---

## 📊 OLAP Operations
Accessible via `/dashboard/olap/`:
- **Slice:** Filter across any single dimension (e.g., display only *Female* records).
- **Dice:** Multi-dimensional intersection (e.g., *Male* patients aged *50-59* with *Non-anginal Chest Pain* and *High Cholesterol*).
- **Roll-Up:** Summarize individual facts into aggregate metrics across `DimAgeGroup` cohorts.
- **Drill-Down:** Disaggregate age groups into detailed demographic and clinical cross-sections.

---

## 🤖 Machine Learning & Classification
Models are trained with standardized pipelines (`StandardScaler` + `Classifier`) using 80/20 stratified splits and 5-fold stratified cross-validation:

```bash
python manage.py train_models
```

### Evaluated Model Metrics on Actual Dataset
| Algorithm | Accuracy | Precision | Recall | F1-Score | ROC-AUC | 5-Fold CV Mean |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Logistic Regression** | **98.5%** | 98.26% | **99.12%** | **98.69%** | **99.76%** | **98.60%** |
| **Random Forest** | 93.5% | 94.69% | 93.86% | 94.27% | 98.81% | 93.20% |
| **Gaussian Naïve Bayes** | 91.0% | 93.64% | 90.35% | 91.96% | 97.80% | 89.90% |
| **Decision Tree** | 86.0% | 88.39% | 86.84% | 87.61% | 85.86% | 88.50% |

*Note: In medical diagnostics, **Recall** (sensitivity) is prioritized to minimize False Negatives. Logistic Regression achieved the highest overall Recall (99.12%) and F1-Score (98.69%).*

---

## 💡 Explainable AI (XAI)
To avoid "black-box" clinical outputs, predictions include local feature importance:
- **Tree-Based Models (Random Forest, Decision Tree):** Uses normalized Gini feature importance (`feature_importances_`).
- **Linear Models (Logistic Regression):** Uses absolute standardized coefficient weights (`coef_`).
- **Visual Display:** Dynamic Chart.js horizontal bar charts displaying relative feature contributions for individual patient predictions.

---

## 🔍 K-Means Clustering
Accessible via `/mining/clustering/`:
- **Features Selected:** `age`, `chol`, `trestbps`, `thalach`.
- **Scaling:** Continuous features are standardized using `StandardScaler` to prevent high-variance attributes (`chol`) from distorting Euclidean distances.
- **Elbow Method:** Evaluates inertia across $K \in [2, 10]$ to empirically determine optimal cluster counts.
- **Silhouette Scoring:** Evaluates cluster cohesion and separation.
- **Cluster Profiling:** Outputs real centroid means and categorical risk distributions for each discovered cohort.

---

## 🔗 Apriori Association Rule Mining
Accessible via `/mining/association-rules/`:
- Discretizes continuous metrics into categorical items.
- Configurable controls for **Minimum Support**, **Minimum Confidence**, and **Minimum Lift**.
- Formats antecedent and consequent rules, sorted by Lift to identify strong diagnostic associations.

---

## 📁 Dataset Specifications
- **Filename:** `dataset/heart_disease.csv`
- **Total Records:** 1,000 rows
- **Attributes:** 14 columns
- **Class Distribution:**
  - Presence of Heart Disease (`target = 1`): 571 (57.1%)
  - Absence of Heart Disease (`target = 0`): 429 (42.9%)
- **Identified Null Values:** `chol` (50 missing), `thalach` (50 missing)

---

## 🚀 Installation & Setup

### 1. Prerequisites
- Python 3.10+ installed
- Git

### 2. Clone Repository & Create Virtual Environment
```bash
git clone https://github.com/sahilshah2005/AI-Powered-Healthcare.git
cd AI-Powered-Healthcare

python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Database Setup & Migrations
```bash
python manage.py migrate
```

### 5. Execute ETL Pipeline & Train Models
```bash
# Populate 8-dimension Star Schema
python manage.py run_etl --force

# Train 4 ML pipelines and generate metrics
python manage.py train_models
```

### 6. Run Application Server
```bash
python manage.py runserver
```
Visit `http://127.0.0.1:8000/` in your web browser.

---

## 🧪 Automated Testing
The repository includes a comprehensive Django unit test suite covering all apps:
```bash
python manage.py test
```
**Test Coverage:**
- `etl.tests`: ETL extraction, data validation, dimension caching, Star Schema referential integrity.
- `prediction.tests`: Form bounds validation, pipeline inference, prediction persistence in history.
- `data_mining.tests`: K-Means clustering, feature scaling, elbow curve generation, Apriori rule extraction.
- `dashboard.tests`: Auth redirection, executive KPI calculations, OLAP Slice & Roll-Up queries.
- `accounts.tests`: User registration, authentication failure alerts, session redirect enforcement.

---

## ⚠️ Limitations & Future Scope
- **Limitations:**
  - Imputation uses feature means; advanced iterative techniques (e.g., MICE / KNN Imputer) could be evaluated for high missingness rates.
  - The single source dataset represents a finite cohort; cross-hospital data federation would be required for external clinical generalizability.
- **Future Scope:**
  - Transition to Apache Airflow / Cloud Composer for scheduled distributed ETL orchestration.
  - Integration with HL7 / FHIR healthcare interoperability standards.
  - Deep Learning architectures (MLP, TabNet) for continuous high-dimensional risk modeling.

---

## ⚕️ Medical Disclaimer
> **IMPORTANT:** This software application is developed as an educational prototype for academic evaluation in Data Warehousing and Mining (DWM). All outputs, metrics, cluster groupings, and predicted probabilities are statistical estimates based solely on the historical dataset. They must **not** be used for clinical diagnosis, treatment planning, or as a substitute for professional medical consultation.
