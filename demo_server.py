"""
Demo server with mock data (no MongoDB required)
"""
from flask import Flask, jsonify, request
from flask_cors import CORS
import pandas as pd
import joblib
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Load data and model
df = pd.read_csv('cleaned_churn_data.csv')
model = joblib.load('churn_model_rf.joblib')
scaler = joblib.load('scaler.joblib')
feature_names = joblib.load('feature_names.joblib')

def tenure_bucket(t):
    if t <= 12: return '0-12m'
    elif t <= 24: return '12-24m'
    elif t <= 48: return '24-48m'
    else: return '48m+'

def preprocess_input(customer_data):
    """Preprocess customer data for prediction"""
    df_input = pd.DataFrame([customer_data])
    df_input['TenureBucket'] = df_input['tenure'].apply(tenure_bucket)
    df_encoded = pd.get_dummies(df_input)
    
    X_pred = pd.DataFrame(columns=feature_names)
    for col in feature_names:
        X_pred.at[0, col] = df_encoded.at[0, col] if col in df_encoded.columns else 0
    
    return scaler.transform(X_pred)

@app.route('/api/analytics/churn-rate/', methods=['GET'])
def churn_rate():
    """Get churn rate analytics"""
    total = len(df)
    churned = len(df[df['Churn'] == 'Yes'])
    churn_rate = (churned / total * 100) if total > 0 else 0
    
    breakdown = df.groupby('Churn').agg({
        'MonthlyCharges': 'mean',
        'tenure': 'mean'
    }).reset_index()
    
    breakdown_list = []
    for _, row in breakdown.iterrows():
        breakdown_list.append({
            '_id': row['Churn'],
            'count': len(df[df['Churn'] == row['Churn']]),
            'avg_monthly_charges': float(row['MonthlyCharges']),
            'avg_tenure': float(row['tenure'])
        })
    
    return jsonify({
        'total_customers': total,
        'churned_customers': churned,
        'churn_rate': round(churn_rate, 2),
        'breakdown': breakdown_list
    })

@app.route('/api/analytics/segment-analysis/', methods=['GET'])
def segment_analysis():
    """Get segment analysis"""
    segment_by = request.args.get('segment_by', 'Contract')
    
    segments = []
    for segment_value in df[segment_by].unique():
        segment_df = df[df[segment_by] == segment_value]
        total = len(segment_df)
        churned = len(segment_df[segment_df['Churn'] == 'Yes'])
        
        segments.append({
            '_id': segment_value,
            'segment': segment_value,
            'total': total,
            'churned': churned,
            'churn_rate': round((churned / total * 100) if total > 0 else 0, 2),
            'avg_monthly_charges': round(segment_df['MonthlyCharges'].mean(), 2),
            'avg_tenure': round(segment_df['tenure'].mean(), 1)
        })
    
    # Sort by churn rate
    segments.sort(key=lambda x: x['churn_rate'], reverse=True)
    
    return jsonify({
        'segment_by': segment_by,
        'segments': segments
    })

@app.route('/api/predict/', methods=['POST'])
def predict():
    """Predict churn for single customer"""
    data = request.json
    
    try:
        # Preprocess
        X_scaled = preprocess_input(data)
        
        # Predict
        probability = float(model.predict_proba(X_scaled)[0][1])
        prediction = 'Yes' if probability > 0.5 else 'No'
        
        # Risk level
        if probability >= 0.7:
            risk_level = 'HIGH'
        elif probability >= 0.4:
            risk_level = 'MEDIUM'
        else:
            risk_level = 'LOW'
        
        return jsonify({
            'churn_probability': probability,
            'churn_prediction': prediction,
            'risk_level': risk_level,
            'confidence': float(max(probability, 1 - probability)),
            'prediction_date': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/customers/', methods=['GET'])
def customers():
    """List customers"""
    page = int(request.args.get('page', 1))
    page_size = int(request.args.get('page_size', 100))
    
    start = (page - 1) * page_size
    end = start + page_size
    
    results = df.iloc[start:end].to_dict('records')
    
    return jsonify({
        'count': len(df),
        'page': page,
        'page_size': page_size,
        'results': results
    })

if __name__ == '__main__':
    print("🚀 Starting Demo API Server...")
    print("📊 Loaded {} customer records".format(len(df)))
    print("🔗 API running at: http://localhost:8001")
    print("\n📍 Available endpoints:")
    print("   - GET  /api/analytics/churn-rate/")
    print("   - GET  /api/analytics/segment-analysis/")
    print("   - POST /api/predict/")
    print("   - GET  /api/customers/")
    print("\n✨ Open frontend/index.html in your browser!")
    
    app.run(host='0.0.0.0', port=8001, debug=True)
