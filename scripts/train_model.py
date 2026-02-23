import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, roc_auc_score, confusion_matrix
import joblib

def train_model(file_path):
    df = pd.read_csv(file_path)
    
    # 1. Feature Engineering: Tenure Buckets
    def tenure_bucket(t):
        if t <= 12: return '0-12m'
        elif t <= 24: return '12-24m'
        elif t <= 48: return '24-48m'
        else: return '48m+'
    df['TenureBucket'] = df['tenure'].apply(tenure_bucket)
    
    # 2. Encoding
    le = LabelEncoder()
    df['Churn'] = le.fit_transform(df['Churn']) # Yes: 1, No: 0
    
    # Separate categorical and numerical
    cat_cols = df.select_dtypes(include=['object', 'string']).columns.tolist()
    if 'Churn' in cat_cols:
        cat_cols.remove('Churn')
    
    # One-hot encode categorical variables
    df_final = pd.get_dummies(df, columns=cat_cols, drop_first=True).astype(float)
    
    # 3. Model Preparation
    X = df_final.drop('Churn', axis=1)
    y = df_final['Churn']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    
    # Scaling
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # 4. Training
    # Baseline: Logistic Regression
    lr = LogisticRegression()
    lr.fit(X_train_scaled, y_train)
    lr_preds = lr.predict(X_test_scaled)
    
    # Advanced: Random Forest
    rf = RandomForestClassifier(n_estimators=100, random_state=42)
    rf.fit(X_train_scaled, y_train)
    rf_preds = rf.predict(X_test_scaled)
    
    # 5. Evaluation
    print("--- Logistic Regression ---")
    print(classification_report(y_test, lr_preds))
    print(f"ROC-AUC: {roc_auc_score(y_test, lr.predict_proba(X_test_scaled)[:, 1]):.4f}")
    
    print("\n--- Random Forest ---")
    print(classification_report(y_test, rf_preds))
    print(f"ROC-AUC: {roc_auc_score(y_test, rf.predict_proba(X_test_scaled)[:, 1]):.4f}")
    
    # 6. Save Model and Scaler for Dashboard
    joblib.dump(rf, 'churn_model_rf.joblib')
    joblib.dump(scaler, 'scaler.joblib')
    joblib.dump(X.columns.tolist(), 'feature_names.joblib')
    print("\nModel saved as churn_model_rf.joblib")

if __name__ == "__main__":
    train_model("cleaned_churn_data.csv")
