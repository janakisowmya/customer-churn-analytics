import pandas as pd
import numpy as np
import random

def generate_mock_churn_data(n=200):
    np.random.seed(42)
    random.seed(42)
    
    data = []
    for _ in range(n):
        tenure = random.randint(1, 72)
        contract = random.choice(['Month-to-month', 'One year', 'Two year'])
        internet = random.choice(['Fiber optic', 'DSL', 'No'])
        tech_support = random.choice(['Yes', 'No', 'No internet service'])
        payment = random.choice(['Electronic check', 'Mailed check', 'Bank transfer (automatic)', 'Credit card (automatic)'])
        paperless = random.choice(['Yes', 'No'])
        monthly = round(random.uniform(20.0, 120.0), 2)
        senior = random.choice([0, 1])
        multiple = random.choice(['Yes', 'No', 'No phone service'])
        
        # simple heuristic for churn to make the model learn something
        churn_prob = 0.1
        if tenure < 6: churn_prob += 0.4
        elif tenure > 48: churn_prob -= 0.1
        if contract == 'Month-to-month': churn_prob += 0.3
        if internet == 'Fiber optic': churn_prob += 0.1
        if monthly > 80: churn_prob += 0.1
        
        churn_prob = max(0.01, min(0.99, churn_prob))
        churn = 'Yes' if random.random() < churn_prob else 'No'
        
        data.append({
            'tenure': tenure,
            'Contract': contract,
            'InternetService': internet,
            'TechSupport': tech_support,
            'PaymentMethod': payment,
            'PaperlessBilling': paperless,
            'MonthlyCharges': monthly,
            'SeniorCitizen': senior,
            'MultipleLines': multiple,
            'Churn': churn
        })
        
    df = pd.DataFrame(data)
    df.to_csv('cleaned_churn_data.csv', index=False)
    print("Generated cleaned_churn_data.csv")

if __name__ == '__main__':
    generate_mock_churn_data()
