import os
import shutil
import pandas as pd

# Paths
CSV_PATH = "labels.csv"
DATASET_DIR = "dataset"

# Create class mapping
label_map = {
    "front": "front_side",
    "side": "front_side",
    "back": "cardback",
    "tag": "tag",
}

# Load CSV
df = pd.read_csv(CSV_PATH)

# Create dataset subfolders
for label in set(label_map.values()):
    os.makedirs(os.path.join(DATASET_DIR, label), exist_ok=True)

# Process and move files
for _, row in df.iterrows():
    image_path = row["image_path"].replace("\\", os.sep)  # Make path OS-agnostic
    label = row["label"].strip().lower()

    if label not in label_map:
        print(f"⚠️ Skipping unknown label: {label} ({image_path})")
        continue

    target_label = label_map[label]
    filename = os.path.basename(image_path)
    target_path = os.path.join(DATASET_DIR, target_label, filename)

    try:
        shutil.copy(image_path, target_path)
        print(f"✅ Copied: {image_path} → {target_path}")
    except FileNotFoundError:
        print(f"❌ File not found: {image_path}")
