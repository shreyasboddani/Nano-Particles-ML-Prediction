import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score

# 1. Load the REAL dataset
print("Loading real experimental data...")
df = pd.read_csv("agnp_dataset.csv")

# 2. Clean the Data (Handling the blanks!)
# Drop rows where our target (MIC_ug_ml) is missing. We can't train on blank answers.
df = df.dropna(subset=["MIC_ug_ml"])

# Separate features (X) from the target (y)
# We also drop the zone columns because they are outcomes, not input properties
cols_to_drop = ["zone_inhibition_mm", "zone_concentration_ug_ml", "MIC_ug_ml"]
X = df.drop(columns=[c for c in cols_to_drop if c in df.columns])
y = df["MIC_ug_ml"]

# 3. Handle missing values in Features (Imputation)
# Fill missing particle sizes with the median size of the dataset
if X["particle_size_nm"].isnull().sum() > 0:
    median_size = X["particle_size_nm"].median()
    X["particle_size_nm"] = X["particle_size_nm"].fillna(median_size)
    print(f"Filled missing particle sizes with median: {median_size} nm")

# Fill missing categorical data with 'Unknown'
categorical_columns = ["shape", "coating", "bacteria", "gram_type"]
for col in categorical_columns:
    if col in X.columns:
        X[col] = X[col].fillna("Unknown")

# 4. One-Hot Encoding
# Converts text categories into true/false numeric columns
X_encoded = pd.get_dummies(X, columns=categorical_columns, drop_first=True)

# 5. Split data (80% for training, 20% for testing)
X_train, X_test, y_train, y_test = train_test_split(
    X_encoded, y, test_size=0.2, random_state=42)

# 6. Train Random Forest model
print("Training Random Forest model on real data...")
model = RandomForestRegressor(n_estimators=200, random_state=42)
model.fit(X_train, y_train)

# 7. Predictions & Evaluation
y_pred = model.predict(X_test)

mse = mean_squared_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)

print("\n" + "=" * 50)
print("ML MODEL PERFORMANCE (REAL DATA)")
print("=" * 50)
print(f"Mean Squared Error (MSE): {mse:.4f}")
print(f"R² Score: {r2:.4f}")
print(f"RMSE: {np.sqrt(mse):.4f} µg/mL")
print("=" * 50)

# --- PLOTTING ---

# 1. Feature Importance Plot
importances = model.feature_importances_
features = X_encoded.columns

# Get the top 10 most important features so the graph isn't too crowded
feat_df = pd.DataFrame({
    "Feature": features,
    "Importance": importances
}).sort_values(by="Importance", ascending=False).head(10)

plt.figure(figsize=(10, 6))
sns.barplot(data=feat_df, y="Feature", x="Importance", palette="viridis")
plt.title("Top 10 Feature Importances in Predicting MIC",
          fontsize=14, fontweight='bold')
plt.xlabel("Importance Score")
plt.ylabel("Feature")
plt.tight_layout()
plt.savefig("feature_importance.png", dpi=150, bbox_inches="tight")

# 2. Predicted vs Actual Plot
plt.figure(figsize=(6, 6))
plt.scatter(y_test, y_pred, alpha=0.7, color='steelblue',
            edgecolors='black', linewidth=0.5)
plt.xlabel("Actual MIC (µg/mL)", fontsize=12)
plt.ylabel("Predicted MIC (µg/mL)", fontsize=12)
plt.title("Actual vs Predicted MIC", fontsize=14, fontweight='bold')
min_val = min(min(y_test), min(y_pred))
max_val = max(max(y_test), max(y_pred))
plt.plot([min_val, max_val], [min_val, max_val], 'r--',
         linewidth=2, label='Perfect Prediction')
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig("predicted_vs_actual.png", dpi=150, bbox_inches="tight")

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

print("\nTRAINING COMPLETE - All plots updated and saved!")
