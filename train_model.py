import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import mean_squared_error, r2_score

# Load dataset
df = pd.read_csv("agnp_120_dataset.csv")

# Encode categorical features
le_dict = {}
df_encoded = df.copy()
for col in ["shape", "coating", "bacteria", "gram_type"]:
    le = LabelEncoder()
    df_encoded[col] = le.fit_transform(df[col])
    le_dict[col] = le

# Features & target
X = df_encoded.drop(["MIC_ug_ml", "zone_inhibition_mm"], axis=1)
y = df_encoded["MIC_ug_ml"]

# Split data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train Random Forest model
model = RandomForestRegressor(n_estimators=200, random_state=42)
model.fit(X_train, y_train)

# Predictions
y_pred = model.predict(X_test)

# Evaluation metrics
mse = mean_squared_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)

print("=" * 50)
print("ML MODEL PERFORMANCE")
print("=" * 50)
print(f"Mean Squared Error (MSE): {mse:.4f}")
print(f"R² Score: {r2:.4f}")
print(f"RMSE: {np.sqrt(mse):.4f}")
print("=" * 50)

# 1. Feature Importance Plot
importances = model.feature_importances_
features = X.columns

feat_df = pd.DataFrame({
    "Feature": features,
    "Importance": importances
}).sort_values(by="Importance", ascending=False)

plt.figure(figsize=(8, 5))
sns.barplot(data=feat_df, y="Feature", x="Importance", palette="viridis")
plt.title("Feature Importance in Predicting MIC", fontsize=14, fontweight='bold')
plt.xlabel("Importance Score")
plt.ylabel("Feature")
plt.tight_layout()
plt.savefig("feature_importance.png", dpi=150, bbox_inches="tight")
print("Plot saved: feature_importance.png")

# 2. Predicted vs Actual Plot
plt.figure(figsize=(6, 6))
plt.scatter(y_test, y_pred, alpha=0.7, color='steelblue', edgecolors='black', linewidth=0.5)
plt.xlabel("Actual MIC (µg/mL)", fontsize=12)
plt.ylabel("Predicted MIC (µg/mL)", fontsize=12)
plt.title("Actual vs Predicted MIC", fontsize=14, fontweight='bold')
min_val = min(min(y_test), min(y_pred))
max_val = max(max(y_test), max(y_pred))
plt.plot([min_val, max_val], [min_val, max_val], 'r--', linewidth=2, label='Perfect Prediction')
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig("predicted_vs_actual.png", dpi=150, bbox_inches="tight")
print("Plot saved: predicted_vs_actual.png")

# 3. Residual Distribution Plot
residuals = y_test - y_pred

plt.figure(figsize=(6, 5))
sns.histplot(residuals, kde=True, color='teal', bins=15)
plt.axvline(x=0, color='red', linestyle='--', linewidth=2, label='Zero Error')
plt.title("Residual Distribution", fontsize=14, fontweight='bold')
plt.xlabel("Prediction Error (µg/mL)")
plt.ylabel("Count")
plt.legend()
plt.tight_layout()
plt.savefig("residual_distribution.png", dpi=150, bbox_inches="tight")
print("Plot saved: residual_distribution.png")

print("\n" + "=" * 50)
print("TRAINING COMPLETE - All plots generated!")
print("=" * 50)
