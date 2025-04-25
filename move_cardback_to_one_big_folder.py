import os
import shutil

# Set the path to your source directories and target directory
source_directory = (
    "filtered/front_side"  # Replace with your folder path containing 1000 subfolders
)
target_directory = "front_side/dataset"  # Replace with your desired target folder

# Ensure the target directory exists
if not os.path.exists(target_directory):
    os.makedirs(target_directory)

# Iterate over all subdirectories in the source directory
for subdir, _, files in os.walk(source_directory):
    for file in files:
        # Check if the file is an image (you can adjust extensions as needed)
        if file.lower().endswith((".png", ".jpg", ".jpeg", ".bmp", ".gif")):
            source_file = os.path.join(subdir, file)
            target_file = os.path.join(target_directory, file)

            # Avoid overwriting files with the same name by checking if it already exists in the target folder
            if os.path.exists(target_file):
                # Optionally, you can add a suffix to the filename to prevent overwriting
                base, ext = os.path.splitext(file)
                counter = 1
                while os.path.exists(target_file):
                    target_file = os.path.join(
                        target_directory, f"{base}_{counter}{ext}"
                    )
                    counter += 1

            # Move the file to the target directory
            shutil.move(source_file, target_file)
            print(f"Moved: {file}")

print("Files have been moved successfully.")
