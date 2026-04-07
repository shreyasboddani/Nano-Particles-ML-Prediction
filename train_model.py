import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import cross_val_score, KFold
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import warnings
warnings.filterwarnings('ignore')

# 1. Load the CURRENT dataset
print("Loading current dataset...")
df = pd.read_csv("agnp_ml_100plus_unique.csv")

# 2. Data Audit
print(f"\n=== DATA AUDIT ===")
print(f"Total rows: {len(df)}")
print(f"Rows with MIC: {len(df[df['MIC_ug_ml'].notna()])}")
print(f"Rows with ZOI: {len(df[df['zone_inhibition_mm'].notna()])}")
print(
    f"Rows with both: {len(df[df['MIC_ug_ml'].notna() & df['zone_inhibition_mm'].notna()])}")
print(f"Unique coatings: {df['coating'].nunique()}")
print(f"Unique bacteria: {df['bacteria'].nunique()}")
print(f"Gram-negative: {len(df[df['gram_type'] == 'Negative'])}")
print(f"Gram-positive: {len(df[df['gram_type'] == 'Positive'])}")

# 3. Clean the Data - Use only MIC data for regression
df_clean = df.dropna(subset=["MIC_ug_ml"]).copy()
print(f"\nDataset for ML: {len(df_clean)} rows with MIC data")

# 4. Feature Engineering
cols_to_drop = ["zone_inhibition_mm", "zone_concentration_ug_ml",
                "MIC_ug_ml", "paper_source", "notes", "row_number"]
X = df_clean.drop(columns=[c for c in cols_to_drop if c in df_clean.columns])
y = df_clean["MIC_ug_ml"]

# 5. Handle missing values
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

# 6. One-Hot Encoding
X_encoded = pd.get_dummies(X, columns=categorical_columns, drop_first=True)
print(f"Features after encoding: {X_encoded.shape[1]} total features")

# 7. 5-Fold Cross-Validation
print("\n=== MODELING ===")
kf = KFold(n_splits=5, shuffle=True, random_state=42)
model = RandomForestRegressor(n_estimators=200, random_state=42)

# Perform cross-validation
cv_scores = cross_val_score(model, X_encoded, y, cv=kf, scoring='r2')
cv_mse_scores = -cross_val_score(model, X_encoded,
                                 y, cv=kf, scoring='neg_mean_squared_error')
cv_mae_scores = -cross_val_score(model, X_encoded,
                                 y, cv=kf, scoring='neg_mean_absolute_error')

# Train final model on all data for feature importance
model.fit(X_encoded, y)

# 8. Cross-Validation Results
print(f"Average R² Score: {cv_scores.mean():.4f} ± {cv_scores.std():.4f}")
print(f"Individual R² scores: {[f'{score:.4f}' for score in cv_scores]}")
print(f"Average MSE: {cv_mse_scores.mean():.4f} ± {cv_mse_scores.std():.4f}")
print(f"Average RMSE: {np.sqrt(cv_mse_scores.mean()):.4f} µg/mL")
print(
    f"Average MAE: {cv_mae_scores.mean():.4f} ± {cv_mae_scores.std():.4f} µg/mL")

# 9. Feature Importance
importances = model.feature_importances_
features = X_encoded.columns

feat_df = pd.DataFrame({
    "Feature": features,
    "Importance": importances
}).sort_values(by="Importance", ascending=False).head(10)

print("\n=== TOP 10 FEATURE IMPORTANCE ===")
for i, (feat, imp) in enumerate(zip(feat_df['Feature'], feat_df['Importance'])):
    print(f"{i+1:2d}. {feat}: {imp:.4f} ({imp*100:.1f}%)")

# 10. TADURI LAB SIMULATION
print("\n=== TADURI LAB SIMULATION ===")
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

# 11. VISUALIZATIONS
plt.style.use('default')

# Feature Importance Plot
plt.figure(figsize=(10, 6))
sns.barplot(data=feat_df, y="Feature", x="Importance", palette="viridis")
plt.title("Top 10 Feature Importances in Predicting MIC",
          fontsize=14, fontweight='bold')
plt.xlabel("Importance Score")
plt.ylabel("Feature")
plt.tight_layout()
plt.savefig("feature_importance.png", dpi=150, bbox_inches="tight")

# Predicted vs Actual Plot
plt.figure(figsize=(8, 8))
y_pred = model.predict(X_encoded)
plt.scatter(y, y_pred, alpha=0.7, color='steelblue',
            edgecolors='black', linewidth=0.5)
plt.xlabel("Actual MIC (µg/mL)", fontsize=12)
plt.ylabel("Predicted MIC (µg/mL)", fontsize=12)
plt.title("Actual vs Predicted MIC (Cross-Validation)",
          fontsize=14, fontweight='bold')
min_val = min(min(y), min(y_pred))
max_val = max(max(y), max(y_pred))
plt.plot([min_val, max_val], [min_val, max_val], 'r--',
         linewidth=2, label='Perfect Prediction')
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig("predicted_vs_actual.png", dpi=150, bbox_inches="tight")

# Particle Size vs MIC Scatter Plot
plt.figure(figsize=(10, 6))
plt.scatter(df_clean['particle_size_nm'], df_clean['MIC_ug_ml'],
            alpha=0.7, color='darkblue', edgecolors='black', linewidth=0.5)
plt.xlabel("Particle Size (nm)", fontsize=12)
plt.ylabel("MIC (µg/mL)", fontsize=12)
plt.title("Particle Size vs Antibacterial Activity",
          fontsize=14, fontweight='bold')
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig("particle_size_vs_mic.png", dpi=150, bbox_inches="tight")

# Cross-Validation Performance Plot
plt.figure(figsize=(8, 6))
fold_numbers = range(1, 6)
plt.bar(fold_numbers, cv_scores, alpha=0.7, color='green', edgecolor='black')
plt.axhline(y=cv_scores.mean(), color='red', linestyle='--',
            linewidth=2, label=f'Mean R² = {cv_scores.mean():.3f}')
plt.xlabel('Fold')
plt.ylabel('R² Score')
plt.title('5-Fold Cross-Validation Performance',
          fontsize=14, fontweight='bold')
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig("cv_performance.png", dpi=150, bbox_inches="tight")

print("\n✅ TRAINING COMPLETE - All plots saved!")
print(f"📊 Generated files: feature_importance.png, predicted_vs_actual.png, particle_size_vs_mic.png, cv_performance.png")
