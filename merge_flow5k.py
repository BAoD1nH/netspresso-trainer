import os
import shutil
import glob
from tqdm import tqdm

# ================= CONFIGURATION =================
# Update this to the exact path of your dataset folder
DATASET_ROOT = "./data/intersection_flow5k" 

# Source and Destination paths
SRC_IMAGES = os.path.join(DATASET_ROOT, "images", "test")
SRC_LABELS = os.path.join(DATASET_ROOT, "labels", "test")

DST_IMAGES = os.path.join(DATASET_ROOT, "images", "val")
DST_LABELS = os.path.join(DATASET_ROOT, "labels", "val")
# =================================================

def move_files(src_dir, dst_dir, file_type="files"):
    # Check if source exists
    if not os.path.exists(src_dir):
        print(f"Warning: Source directory {src_dir} does not exist. Skipping.")
        return

    # Ensure destination exists
    os.makedirs(dst_dir, exist_ok=True)

    # Get all files
    files = os.listdir(src_dir)
    print(f"Moving {len(files)} {file_type} from 'test' to 'val'...")

    moved_count = 0
    for filename in tqdm(files):
        src_path = os.path.join(src_dir, filename)
        dst_path = os.path.join(dst_dir, filename)

        # Skip directories
        if os.path.isdir(src_path):
            continue

        # Handle duplicates: append '_dup' if file exists
        if os.path.exists(dst_path):
            base, ext = os.path.splitext(filename)
            dst_path = os.path.join(dst_dir, f"{base}_test_merge{ext}")

        shutil.move(src_path, dst_path)
        moved_count += 1
    
    print(f"Successfully moved {moved_count} {file_type}.")

def main():
    print(f"--- Merging Dataset: {DATASET_ROOT} ---")
    
    # 1. Move Images
    move_files(SRC_IMAGES, DST_IMAGES, "images")
    
    # 2. Move Labels
    move_files(SRC_LABELS, DST_LABELS, "labels")

    # 3. Cleanup (Optional)
    # Remove the empty 'test' folders to avoid confusion later
    if os.path.exists(SRC_IMAGES) and not os.listdir(SRC_IMAGES):
        os.rmdir(SRC_IMAGES)
    if os.path.exists(SRC_LABELS) and not os.listdir(SRC_LABELS):
        os.rmdir(SRC_LABELS)
        
    print("-" * 30)
    print("Merge Complete! You can now use 'val' for validation/testing.")

if __name__ == "__main__":
    main()