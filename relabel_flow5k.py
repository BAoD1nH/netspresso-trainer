import os
import glob
import shutil
from tqdm import tqdm

# ================= CONFIGURATION =================
# Path to the MAIN LABELS folder
# We use recursive search, so this will find 'train' and 'val' inside automatically.
TARGET_FOLDER = "/home/baodinh/netspresso-trainer/data/intersection_flow5k/labels"

# TARGET CLASS LIST (Your Standard):
# 0: motorbike
# 1: car
# 2: bus
# 3: truck

# DATASET ORIGINAL CLASSES:
# 0: vehicle (Assumed -> car)
# 1: bus
# 2: bicycle
# 3: pedestrian
# 4: engine (Assumed -> motorbike/motorcycle)
# 5: truck
# 6: tricycle
# 7: obstacle

# MAPPING RULES { Original_ID: New_ID }
# Use -1 to DELETE a class
TRAFFIC_MAPPING = {
    0: 1,   # vehicle -> car
    1: 2,   # bus -> bus
    2: -1,  # bicycle -> DELETE
    3: -1,  # pedestrian -> DELETE
    4: 0,   # engine -> motorbike (Check this! If 'engine' means construction vehicle, delete it)
    5: 3,   # truck -> truck
    6: -1,  # tricycle -> DELETE
    7: -1   # obstacle -> DELETE
}
# =================================================

def backup_data(folder):
    """Creates a backup of the labels folder before modifying."""
    # Since folder is "labels", backup will be "labels_BACKUP"
    # We go one level up to avoid creating backup INSIDE the folder if we aren't careful
    parent_dir = os.path.dirname(folder.rstrip('/'))
    backup_name = os.path.basename(folder.rstrip('/')) + "_BACKUP"
    backup_path = os.path.join(parent_dir, backup_name)
    
    if not os.path.exists(backup_path):
        print(f"Creating backup at: {backup_path}...")
        shutil.copytree(folder, backup_path)
    else:
        print(f"Backup already exists at: {backup_path}. Skipping backup.")

def fix_labels():
    # 1. Verify Path
    if not os.path.exists(TARGET_FOLDER):
        print(f"Error: Folder not found at '{TARGET_FOLDER}'")
        return

    # 2. Create Backup
    backup_data(TARGET_FOLDER)

    # 3. Get all text files (RECURSIVE now)
    # This finds labels/train/*.txt AND labels/val/*.txt
    search_pattern = os.path.join(TARGET_FOLDER, "**", "*.txt")
    txt_files = glob.glob(search_pattern, recursive=True)
    
    print(f"Found {len(txt_files)} label files in total (train/val/etc).")
    
    if len(txt_files) == 0:
        print("No .txt files found! Check your path.")
        return

    modified_count = 0
    deleted_objects = 0

    # 4. Process files
    for file_path in tqdm(txt_files, desc="Relabeling"):
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
                    
                    # Case A: DELETE
                    if new_id == -1:
                        file_changed = True
                        deleted_objects += 1
                        continue
                    
                    # Case B: REMAP
                    if new_id != original_id:
                        parts[0] = str(new_id)
                        new_line = " ".join(parts) + "\n"
                        new_lines.append(new_line)
                        file_changed = True
                    
                    # Case C: KEEP (ID stayed the same)
                    else:
                        new_lines.append(line)
                else:
                    # Case D: Unknown ID - Keep it safe
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
    print(f"Objects deleted: {deleted_objects}")
    print(f"Backup location: {TARGET_FOLDER}_BACKUP (Check this if mistakes were made!)")

if __name__ == "__main__":
    fix_labels()