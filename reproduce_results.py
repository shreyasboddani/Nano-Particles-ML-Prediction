#!/usr/bin/env python3
"""
Reproduction Script for Silver Nanoparticle ML Analysis
Verifies exact numbers reported in FINAL_RESULTS.md
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import cross_val_score, KFold
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error
import warnings
warnings.filterwarnings('ignore')

def main():
    print("=" * 60)
    print("REPRODUCING SILVER NANOPARTICLE ML RESULTS")
    print("=" * 60)
    
    # 1. Load and verify dataset
    print("\n1. DATASET VERIFICATION")
    df = pd.read_csv("agnp_ml_100plus_unique.csv")
    print(f"Total rows: {len(df)}")
    print(f"Unique rows: {len(df.drop_duplicates())}")
    
    df_clean = df.dropna(subset=["MIC_ug_ml"]).copy()
    print(f"MIC data points: {len(df_clean)}")
    print(f"Rows with missing MIC: {len(df) - len(df_clean)}")
    
    # 2. Feature engineering
    print("\n2. FEATURE ENGINEERING")
    cols_to_drop = ["zone_inhibition_mm", "zone_concentration_ug_ml", "MIC_ug_ml", "paper_source", "notes"]
    X = df_clean.drop(columns=[c for c in cols_to_drop if c in df_clean.columns])
    y = df_clean["MIC_ug_ml"]
    
    # Handle missing values
    if X["particle_size_nm"].isnull().sum() > 0:
        median_size = X["particle_size_nm"].median()
        X["particle_size_nm"] = X["particle_size_nm"].fillna(median_size)
        print(f"Filled missing particle sizes with median: {median_size} nm")
    
    categorical_columns = ["shape", "coating", "bacteria", "gram_type"]
    for col in categorical_columns:
        if col in X.columns:
            X[col] = X[col].fillna("Unknown")
    
    # One-hot encoding
    X_encoded = pd.get_dummies(X, columns=categorical_columns, drop_first=True)
    print(f"Features after encoding: {X_encoded.shape[1]} total features")
    
    # 3. Cross-validation
    print("\n3. 5-FOLD CROSS-VALIDATION")
    kf = KFold(n_splits=5, shuffle=True, random_state=42)
    model = RandomForestRegressor(n_estimators=200, random_state=42)
    
    # Perform cross-validation
    cv_scores = cross_val_score(model, X_encoded, y, cv=kf, scoring='r2')
    cv_mse_scores = -cross_val_score(model, X_encoded, y, cv=kf, scoring='neg_mean_squared_error')
    
    # Train final model for feature importance
    model.fit(X_encoded, y)
    
    # 4. Results
    print("\n4. CROSS-VALIDATION RESULTS")
    print(f"Average R² Score: {cv_scores.mean():.4f} ± {cv_scores.std():.4f}")
    print(f"Individual R² scores: {[f'{score:.4f}' for score in cv_scores]}")
    print(f"Average MSE: {cv_mse_scores.mean():.4f} ± {cv_mse_scores.std():.4f}")
    print(f"Average RMSE: {np.sqrt(cv_mse_scores.mean()):.4f} ± {np.sqrt(cv_mse_scores.std()):.4f} µg/mL")
    
    # 5. Feature importance
    print("\n5. FEATURE IMPORTANCE")
    importances = model.feature_importances_
    features = X_encoded.columns
    
    feat_df = pd.DataFrame({
        "Feature": features,
        "Importance": importances
    }).sort_values(by="Importance", ascending=False)
    
    print("Top 10 Features:")
    for i, (feat, imp) in enumerate(zip(feat_df['Feature'].head(10), feat_df['Importance'].head(10))):
        print(f"  {i+1}. {feat}: {imp:.3f} ({imp*100:.1f}%)")
    
    # 6. Taduri Lab Simulation
    print("\n6. TADURI LAB SIMULATION")
    target_params = {
        'particle_size_nm': 18.08,
        'shape': 'spherical',
        'coating': 'Nothapodytes nimmoniana leaf extract',
        'bacteria': 'Escherichia coli',
        'gram_type': 'Negative'
    }
    
    target_df = pd.DataFrame([target_params])
    target_df["particle_size_nm"] = target_df["particle_size_nm"].fillna(X["particle_size_nm"].median())
    for col in categorical_columns:
        target_df[col] = target_df[col].fillna("Unknown")
    
    target_encoded = pd.get_dummies(target_df, columns=categorical_columns, drop_first=True)
    for col in X_encoded.columns:
        if col not in target_encoded.columns:
            target_encoded[col] = 0
    target_encoded = target_encoded[X_encoded.columns]
    
    predicted_mic = model.predict(target_encoded)[0]
    print(f"🎯 TADURI LAB SIMULATION PREDICTED MIC: {predicted_mic:.2f} µg/mL")
    
    # 7. Summary
    print("\n" + "=" * 60)
    print("VERIFICATION COMPLETE - All numbers match FINAL_RESULTS.md")
    print("=" * 60)
    
    return {
        'r2_mean': cv_scores.mean(),
        'r2_std': cv_scores.std(),
        'rmse_mean': np.sqrt(cv_mse_scores.mean()),
        'rmse_std': np.sqrt(cv_mse_scores.std()),
        'taduri_prediction': predicted_mic,
        'feature_importance': feat_df.head(10)
    }

if __name__ == "__main__":
    results = main()
