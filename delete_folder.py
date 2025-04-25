import os
import shutil

def clean_non_hotwheels_folders(images_root="images"):
    keep_keywords = ["hotwheels", "hot-wheels", "hw"]

    if not os.path.isdir(images_root):
        print(f"❌ Folder '{images_root}' not found.")
        return

    for folder_name in os.listdir(images_root):
        folder_path = os.path.join(images_root, folder_name)
        if not os.path.isdir(folder_path):
            continue

        folder_name_lower = folder_name.lower()
        if not any(keyword in folder_name_lower for keyword in keep_keywords):
            try:
                shutil.rmtree(folder_path)
                print(f"🗑️ Deleted: {folder_name}")
            except Exception as e:
                print(f"❌ Failed to delete {folder_name}: {e}")
        else:
            print(f"✅ Kept: {folder_name}")

# Run the cleaner
clean_non_hotwheels_folders()
