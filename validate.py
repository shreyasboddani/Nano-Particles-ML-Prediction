import pandas as pd
import numpy as np

# Load and validate the newest dataset
df = pd.read_csv('agnp_ml_100plus_unique (1).csv')

print('=== DATASET VALIDATION ===')
print(f'Total rows: {len(df)}')
print(f'Columns: {list(df.columns)}')

# Data quality checks
print(f'\nMissing values:')
print(df.isnull().sum())

print(f'\nUnique values:')
print(f'Coatings: {df["coating"].nunique()} unique')
print(f'Bacteria: {df["bacteria"].nunique()} unique')
print(f'Shapes: {df["shape"].nunique()} unique')

# Count metrics
mic_rows = df[df['MIC_ug_ml'].notna()]
zoi_rows = df[df['zone_inhibition_mm'].notna()]
both_rows = df[df['MIC_ug_ml'].notna() & df['zone_inhibition_mm'].notna()]

print(f'\nMETRIC COVERAGE:')
print(f'Rows with MIC: {len(mic_rows)}')
print(f'Rows with ZOI: {len(zoi_rows)}')
print(f'Rows with both: {len(both_rows)}')

# Taduri data check
taduri_rows = df[df['notes'].str.contains('Taduri', na=False)]
print(f'\nTADURI DATA:')
print(f'Rows: {len(taduri_rows)}')
if len(taduri_rows) > 0:
    print('Taduri coatings:', taduri_rows['coating'].unique())
    print('Taduri sizes:', taduri_rows['particle_size_nm'].unique())

# Basic statistics
print(f'\nBASIC STATISTICS:')
print(
    f'Size range: {df["particle_size_nm"].min():.2f} - {df["particle_size_nm"].max():.2f} nm')
print(
    f'MIC range: {df["MIC_ug_ml"].min():.2f} - {df["MIC_ug_ml"].max():.2f} µg/mL')

# Gram type distribution
print(f'\nGRAM TYPE DISTRIBUTION:')
gram_counts = df['gram_type'].value_counts()
print(gram_counts)

# Paper sources
print(f'\nPAPER SOURCES:')
source_counts = df['paper_source'].value_counts()
print(source_counts.head(10))
