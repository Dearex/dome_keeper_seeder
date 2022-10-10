import os
import shutil
import time

# CHANGE THESE DEPENDING ON SEED
# Important: Has to be a valid Folder name!
MODE = "RH FS NSG N S"

# CHANGE THESE ONE TIME
SOURCE = r"C:\Users\USERNAME\AppData\Roaming\Godot\app_userdata\Dome Keeper"
SEED_STORAGE_PATH = r"C:\EXAMPLE\LOCATION" # has to exist!
SEED_CHECK_FREQUENCY = 2 # in seconds

# NEEDS TO BE MODIFIED IF SAVE LOGIC OF DOMEKEEPER CHANGES
# Include all files that belong to one savegame and should be saved every time
SAVE_GAME_FILES = ["savegame_0.json", "savegame_0_map.scn"]

# DO NOT TOUCH UNLESS YOU KNOW WHAT YOU DO AND WANT TO MODIFY THE LOGIC

seed_mode_path = os.path.join(SEED_STORAGE_PATH, MODE)
if not os.path.exists(seed_mode_path):
    try:
        os.mkdir(seed_mode_path)
    except Exception as e:
        print(f"Can't create the folder! Reason: {str(e)}")
        quit()

seeds = os.listdir(seed_mode_path)
print(f"Found {len(seeds)} stored seeds...")
if seeds:
    current_folder = int(max([int(seed) for seed in seeds])) + 1
else:
    current_folder = 1
print(f'...continuing with folder {current_folder}')

save_file_path = os.path.join(SOURCE, SAVE_GAME_FILES[0])    
with open(save_file_path, "rb") as file:
    last_data = file.read()

while True:
    with open(save_file_path, "rb") as file:
        data = file.read()
    if data != last_data:
        current_folder_path = os.path.join(seed_mode_path, str(current_folder))
        os.mkdir(current_folder_path)
        for file in SAVE_GAME_FILES:
            shutil.copy(os.path.join(SOURCE, file), current_folder_path)
        print(f"Changed seed stored to {current_folder}")
        current_folder += 1
        last_data = data
    time.sleep(SEED_CHECK_FREQUENCY)
