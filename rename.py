import pandas as pd

# Load the CSV
df = pd.read_csv("labels.csv")

# Apply the mapping
label_map = {
    "front": "front_side",
    "side": "front_side",
    "back": "cardback",
    "tag": "tag",
}
df["label"] = df["label"].map(label_map)

# Save the updated CSV
df.to_csv("labels_combined.csv", index=False)
print("✅ Combined labels saved to labels_combined.csv")
