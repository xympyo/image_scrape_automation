import os
import shutil
from PIL import Image
import torch
from torchvision import transforms, models

# Configuration
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
IMG_SIZE = 224
IMAGE_FOLDER = "front_side/dataset"
OUTPUT_FOLDER = "filtered"
CLASS_NAMES = ["cardback", "front_side", "tag"]
MODEL_PATH = "cardback_classifier.pth"

# Load model
model = models.resnet50(weights=None)
model.fc = torch.nn.Linear(model.fc.in_features, len(CLASS_NAMES))
model.load_state_dict(torch.load(MODEL_PATH, map_location=DEVICE))
model.eval().to(DEVICE)

# Transform
transform = transforms.Compose(
    [
        transforms.Resize((IMG_SIZE, IMG_SIZE)),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
    ]
)

# Make output dirs
for class_name in ["cardback", "front_side"]:
    os.makedirs(os.path.join(OUTPUT_FOLDER, class_name), exist_ok=True)

# Walk through all images in subfolders
for root, _, files in os.walk(IMAGE_FOLDER):
    for filename in files:
        if not filename.lower().endswith((".jpg", ".jpeg", ".png")):
            continue

        image_path = os.path.join(root, filename)

        try:
            image = Image.open(image_path).convert("RGB")
        except Exception as e:
            print(f"❌ Skipping broken image: {image_path} ({e})")
            continue

        input_tensor = transform(image).unsqueeze(0).to(DEVICE)
        with torch.no_grad():
            output = model(input_tensor)
            _, pred_idx = torch.max(output, 1)
            predicted = CLASS_NAMES[pred_idx.item()]

        if predicted == "tag":
            print(f"🗑️ Deleting: {image_path}")
            os.remove(image_path)
        else:
            # Build new destination
            rel_folder = os.path.basename(root)  # Use parent folder name
            dest_dir = os.path.join(OUTPUT_FOLDER, predicted, rel_folder)
            os.makedirs(dest_dir, exist_ok=True)

            dest_path = os.path.join(dest_dir, filename)
            print(f"📦 Moving {image_path} ➝ {dest_path}")
            shutil.copy2(image_path, dest_path)

print("\n✅ Done sorting!")
