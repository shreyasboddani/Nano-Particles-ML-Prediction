import pandas as pd
import numpy as np
import random

# Categories
shapes = ["spherical", "rod", "triangular"]
coatings = ["citrate", "PVP", "PEG", "plant_extract", "chitosan", "none"]
bacteria = ["E_coli", "S_aureus", "P_aeruginosa", "E_faecalis"]
gram_map = {
    "E_coli": "negative",
    "P_aeruginosa": "negative",
    "S_aureus": "positive",
    "E_faecalis": "positive"
}

data = []

for i in range(120):
    size = round(np.random.uniform(5, 50), 1)
    shape = random.choice(shapes)
    coating = random.choice(coatings)
    bact = random.choice(bacteria)
    gram = gram_map[bact]

    # MIC logic (based on real trends)
    if size < 10:
        mic = np.random.uniform(2, 10)
    elif size < 20:
        mic = np.random.uniform(5, 20)
    else:
        mic = np.random.uniform(10, 40)

    # Gram effect
    if gram == "positive":
        mic *= 1.2

    # Zone of inhibition (inverse of MIC)
    zone = max(8, 25 - mic/2 + np.random.uniform(-2, 2))

    data.append([
        size, shape, coating, bact, gram, round(mic,2), round(zone,2)
    ])

df = pd.DataFrame(data, columns=[
    "particle_size_nm","shape","coating",
    "bacteria","gram_type","MIC_ug_ml","zone_inhibition_mm"
])

df.to_csv("agnp_120_dataset.csv", index=False)

print("Dataset created: agnp_120_dataset.csv")
