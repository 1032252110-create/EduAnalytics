"""
Machine Learning Module:
1. Linear Regression -> Predicts final exam percentage (0-100%).
2. Random Forest     -> Classifies academic risk (Low, Medium, High Risk).
"""
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestClassifier

# Step 1: Create 200 synthetic student samples for training
np.random.seed(42)
internals = np.random.uniform(10, 40, 200)       # out of 40
attendance = np.random.uniform(40, 98, 200)      # %
assignments = np.random.uniform(40, 98, 200)     # %
prev_sem = np.random.uniform(40, 95, 200)        # %

X = np.column_stack([internals, attendance, assignments, prev_sem])

# Expected score formula: 35% internals + 20% attendance + 15% assignments + 30% past grade
y_score = np.clip((internals / 40 * 100) * 0.35 + attendance * 0.20 + assignments * 0.15 + prev_sem * 0.30, 20, 100)

# Risk categories: Low Risk, High Risk, or Medium Risk
y_risk = []
for score, att in zip(y_score, attendance):
    if score >= 75 and att >= 75:
        y_risk.append("Low Risk")
    elif score < 50 or att < 60:
        y_risk.append("High Risk")
    else:
        y_risk.append("Medium Risk")

# Step 2: Train both models
regressor = LinearRegression().fit(X, y_score)
classifier = RandomForestClassifier(n_estimators=30, random_state=42).fit(X, y_risk)

def predict(internal, att, assign, prev):
    """Predicts expected score, risk level, and generates advice."""
    features = np.array([[float(internal), float(att), float(assign), float(prev)]])
    score = round(float(np.clip(regressor.predict(features)[0], 0, 100)), 1)
    risk = str(classifier.predict(features)[0])
    probs = {cls: round(p * 100, 1) for cls, p in zip(classifier.classes_, classifier.predict_proba(features)[0])}

    # Generate quick explanation
    if risk == "Low Risk":
        advice = "Low Risk: Steady marks and good attendance. On track for strong grades."
    elif risk == "High Risk":
        advice = "High Risk: Low attendance or low marks. Immediate teacher support needed."
    else:
        advice = "Medium Risk: Moderate performance. Focus on weak subjects to improve."

    return {"predicted_score": score, "risk_level": risk, "probabilities": probs, "insights": advice}

class Predictor:
    predict = staticmethod(predict)

predictor = Predictor()
