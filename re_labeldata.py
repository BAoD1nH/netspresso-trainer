import os
import glob
import shutil
from tqdm import tqdm

# ================= CONFIGURATION =================
# Path to the LABELS folder of the intersection_traffic dataset
# NOTE: Update this path if your folder structure is different
TARGET_FOLDER = "./data/intersection_traffic/train/labels"

# MAPPING RULES
# Format: { Original_ID: New_ID }
# Use -1 to DELETE a class
TRAFFIC_MAPPING = {
    0: -1,  # bicycle -> DELETE
    1: 3,   # bus -> bus
    2: 1,   # car -> car
    3: -1,  # license-plate -> DELETE
    4: 0    # motorcycle -> motorbike
}
# =================================================

def backup_data(folder):
    """Creates a backup of the labels folder before modifying."""
    parent_dir = os.path.dirname(folder)
    backup_path = folder + "_BACKUP"
    if not os.path.exists(backup_path):
        print(f"Creating backup at: {backup_path}...")
        shutil.copytree(folder, backup_path)
    else:
        print(f"Backup already exists at: {backup_path}. Skipping backup.")

def fix_labels():
    # 1. Verify Path
    if not os.path.exists(TARGET_FOLDER):
        print(f"Error: Folder not found at '{TARGET_FOLDER}'")
        print("Please check the path in the CONFIGURATION section of the script.")
        return

    # 2. Create Backup
    backup_data(TARGET_FOLDER)

    # 3. Get all text files
    txt_files = glob.glob(os.path.join(TARGET_FOLDER, "*.txt"))
    print(f"Found {len(txt_files)} label files. Starting processing...")

    modified_count = 0
    deleted_objects = 0

    # 4. Process files
    for file_path in tqdm(txt_files, desc="Fixing Labels"):
        with open(file_path, 'r') as f:
            lines = f.readlines()
        
        new_lines = []
        file_changed = False
        
        for line in lines:
            parts = line.strip().split()
            if not parts: continue
            
            try:
                original_id = int(parts[0])
                
                if original_id in TRAFFIC_MAPPING:
                    new_id = TRAFFIC_MAPPING[original_id]
                    
                    # Case A: DELETE (bicycle, license-plate)
                    if new_id == -1:
                        file_changed = True
                        deleted_objects += 1
                        continue
                    
                    # Case B: REMAP (bus, car, motorcycle)
                    if new_id != original_id:
                        parts[0] = str(new_id)
                        new_line = " ".join(parts) + "\n"
                        new_lines.append(new_line)
                        file_changed = True
                    
                    # Case C: KEEP (If IDs matched, though rare here)
                    else:
                        new_lines.append(line)
                else:
                    # Case D: Unknown ID (Safety: Keep it or Delete it?)
                    # For this specific dataset, we assume the map covers everything.
                    # We will keep it to be safe, but warn if needed.
                    new_lines.append(line)
            
            except ValueError:
                continue

        # 5. Overwrite file only if changes happened
        if file_changed:
            with open(file_path, 'w') as f:
                f.writelines(new_lines)
            modified_count += 1

    print("-" * 30)
    print("PROCESSING COMPLETE")
    print(f"Files modified: {modified_count}")
    print(f"Objects deleted (bicycles/plates): {deleted_objects}")
    print(f"Backup saved at: {TARGET_FOLDER}_BACKUP")

if __name__ == "__main__":
    fix_labels()