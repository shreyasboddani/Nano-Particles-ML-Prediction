import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd

df = pd.read_csv("agnp_120_dataset.csv")

plt.figure(figsize=(8,5))
sns.scatterplot(data=df, x="particle_size_nm", y="MIC_ug_ml", hue="gram_type")
plt.title("Particle Size vs MIC")
plt.xlabel("Particle Size (nm)")
plt.ylabel("MIC (µg/mL)")
plt.savefig("particle_size_vs_mic.png", dpi=150, bbox_inches="tight")
print("Plot saved: particle_size_vs_mic.png")

plt.figure(figsize=(6,5))
sns.boxplot(data=df, x="gram_type", y="MIC_ug_ml")
plt.title("Gram Type vs MIC")
plt.savefig("gram_type_vs_mic.png", dpi=150, bbox_inches="tight")
print("Plot saved: gram_type_vs_mic.png")

plt.figure(figsize=(10,5))
sns.boxplot(data=df, x="coating", y="zone_inhibition_mm")
plt.xticks(rotation=45)
plt.title("Coating vs Zone of Inhibition")
plt.savefig("coating_vs_zone.png", dpi=150, bbox_inches="tight")
print("Plot saved: coating_vs_zone.png")

import numpy as np

numeric_df = df[["particle_size_nm","MIC_ug_ml","zone_inhibition_mm"]]

plt.figure(figsize=(6,5))
sns.heatmap(numeric_df.corr(), annot=True, cmap="coolwarm")
plt.title("Feature Correlation")
plt.savefig("correlation_heatmap.png", dpi=150, bbox_inches="tight")
print("Plot saved: correlation_heatmap.png")
