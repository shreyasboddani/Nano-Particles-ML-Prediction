import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import cross_val_score, KFold
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score
import warnings
warnings.filterwarnings('ignore')

# 1. Load the NEW CLEAN dataset
print("Loading cleaned experimental data...")
df = pd.read_csv("agnp_ml_100plus_unique.csv")

# 2. Clean the Data - Drop rows where MIC_ug_ml is missing
df_clean = df.dropna(subset=["MIC_ug_ml"]).copy()
print(f"Dataset after cleaning: {len(df_clean)} rows with MIC data")

# 3. Feature Engineering - Separate features from target
cols_to_drop = ["zone_inhibition_mm", "zone_concentration_ug_ml",
                "MIC_ug_ml", "paper_source", "notes"]
X = df_clean.drop(columns=[c for c in cols_to_drop if c in df_clean.columns])
y = df_clean["MIC_ug_ml"]

# 4. Handle missing values
# Fill missing particle sizes with median
if X["particle_size_nm"].isnull().sum() > 0:
    median_size = X["particle_size_nm"].median()
    X["particle_size_nm"] = X["particle_size_nm"].fillna(median_size)
    print(f"Filled missing particle sizes with median: {median_size} nm")

# Fill missing categorical data with 'Unknown'
categorical_columns = ["shape", "coating", "bacteria", "gram_type"]
for col in categorical_columns:
    if col in X.columns:
        X[col] = X[col].fillna("Unknown")

# 5. One-Hot Encoding for categorical features
X_encoded = pd.get_dummies(X, columns=categorical_columns, drop_first=True)
print(f"Features after encoding: {X_encoded.shape[1]} total features")

# 6. 5-Fold Cross-Validation Setup
print("\nSetting up 5-Fold Cross-Validation...")
kf = KFold(n_splits=5, shuffle=True, random_state=42)

# 7. Train Random Forest with Cross-Validation
model = RandomForestRegressor(n_estimators=200, random_state=42)

# Perform cross-validation
cv_scores = cross_val_score(model, X_encoded, y, cv=kf, scoring='r2')
cv_mse_scores = -cross_val_score(model, X_encoded,
                                 y, cv=kf, scoring='neg_mean_squared_error')

# Train final model on all data for feature importance
model.fit(X_encoded, y)

# 8. Cross-Validation Results
print("\n" + "=" * 60)
print("5-FOLD CROSS-VALIDATION RESULTS")
print("=" * 60)
print(f"Average R² Score: {cv_scores.mean():.4f} ± {cv_scores.std():.4f}")
print(f"Individual R² scores: {[f'{score:.4f}' for score in cv_scores]}")
print(f"Average MSE: {cv_mse_scores.mean():.4f} ± {cv_mse_scores.std():.4f}")
print(f"Average RMSE: {np.sqrt(cv_mse_scores.mean()):.4f} µg/mL")
print("=" * 60)

# 9. TARGET SIMULATION - Taduri Lab Experiment
print("\n" + "=" * 60)
print("TADURI LAB SIMULATION")
print("=" * 60)

# Create the exact experimental parameters
target_params = {
    'particle_size_nm': 18.08,
    'shape': 'spherical',
    'coating': 'Nothapodytes nimmoniana leaf extract',
    'bacteria': 'Escherichia coli',
    'gram_type': 'Negative'
}

# Convert to DataFrame for prediction
target_df = pd.DataFrame([target_params])

# Apply same preprocessing
target_df["particle_size_nm"] = target_df["particle_size_nm"].fillna(
    X["particle_size_nm"].median())
for col in categorical_columns:
    target_df[col] = target_df[col].fillna("Unknown")

# One-hot encode (align with training data)
target_encoded = pd.get_dummies(
    target_df, columns=categorical_columns, drop_first=True)

# Align columns with training data
for col in X_encoded.columns:
    if col not in target_encoded.columns:
        target_encoded[col] = 0
target_encoded = target_encoded[X_encoded.columns]

# Make prediction
predicted_mic = model.predict(target_encoded)[0]

print(f"Target Parameters:")
print(f"  - Particle Size: {target_params['particle_size_nm']} nm")
print(f"  - Coating: {target_params['coating']}")
print(f"  - Shape: {target_params['shape']}")
print(f"  - Bacteria: {target_params['bacteria']}")
print(f"  - Gram Type: {target_params['gram_type']}")
print(f"\n🎯 TADURI LAB SIMULATION PREDICTED MIC: {predicted_mic:.2f} µg/mL")
print("=" * 60)

# --- PLOTTING ---

# 1. Feature Importance Plot
importances = model.feature_importances_
features = X_encoded.columns

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

# 2. Predicted vs Actual Plot (using cross-validation predictions)
plt.figure(figsize=(6, 6))
# Get cross-validation predictions
cv_predictions = cross_val_score(model, X_encoded, y, cv=kf)
plt.scatter(y, model.predict(X_encoded), alpha=0.7, color='steelblue',
            edgecolors='black', linewidth=0.5)
plt.xlabel("Actual MIC (µg/mL)", fontsize=12)
plt.ylabel("Predicted MIC (µg/mL)", fontsize=12)
plt.title("Actual vs Predicted MIC (Cross-Validation)",
          fontsize=14, fontweight='bold')
min_val = min(min(y), min(model.predict(X_encoded)))
max_val = max(max(y), max(model.predict(X_encoded)))
plt.plot([min_val, max_val], [min_val, max_val], 'r--',
         linewidth=2, label='Perfect Prediction')
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig("predicted_vs_actual.png", dpi=150, bbox_inches="tight")

# 3. Particle Size vs MIC Scatter Plot
plt.figure(figsize=(8, 6))
plt.scatter(df_clean['particle_size_nm'], df_clean['MIC_ug_ml'],
            alpha=0.7, color='darkblue', edgecolors='black', linewidth=0.5)
plt.xlabel("Particle Size (nm)", fontsize=12)
plt.ylabel("MIC (µg/mL)", fontsize=12)
plt.title("Particle Size vs Antibacterial Activity",
          fontsize=14, fontweight='bold')
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig("particle_size_vs_mic.png", dpi=150, bbox_inches="tight")

print("\n✅ TRAINING COMPLETE - All plots updated and saved!")
print(f"📊 Generated files: feature_importance.png, predicted_vs_actual.png, particle_size_vs_mic.png")
