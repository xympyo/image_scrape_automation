import os
import cv2
import csv
import signal
import sys

input_dir = "images"
output_csv = "labels.csv"
labels = []


def resize_image(img, height=600):
    h, w = img.shape[:2]
    scale = height / h
    return cv2.resize(img, (int(w * scale), height))


def save_labels():
    if labels:
        with open(output_csv, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["image_path", "label"])
            writer.writerows(labels)
        print(f"\n💾 Saved {len(labels)} labels to {output_csv}")


# Handle Ctrl+C gracefully
def signal_handler(sig, frame):
    print("\n⛔ Exiting... saving progress.")
    save_labels()
    cv2.destroyAllWindows()
    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)

for folder in os.listdir(input_dir):
    folder_path = os.path.join(input_dir, folder)
    if not os.path.isdir(folder_path):
        continue

    for filename in os.listdir(folder_path):
        if not filename.lower().endswith((".jpg", ".jpeg", ".png")):
            continue

        img_path = os.path.join(folder_path, filename)
        img = cv2.imread(img_path)

        if img is None:
            continue

        resized = resize_image(img)
        cv2.imshow("Label (f=front, b=back, s=side, q=skip, d=tag)", resized)
        key = cv2.waitKey(0) & 0xFF

        if key == ord("q"):
            print(f"⏭️ Skipped {img_path}")
            continue
        elif key == ord("f"):
            label = "front"
        elif key == ord("b"):
            label = "back"
        elif key == ord("s"):
            label = "side"
        elif key == ord("d"):
            label = "tag"
        else:
            print(f"❓ Unrecognized key, skipping {img_path}")
            continue

        labels.append([img_path, label])
        print(f"✅ Labeled {img_path} as {label}")

cv2.destroyAllWindows()
save_labels()
