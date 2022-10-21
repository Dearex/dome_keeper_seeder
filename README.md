import platform

if system:=platform.system() != "Windows":
    print(f"This was designed for Windows (you have '{system}') and won't work anywhere else. ")
    exit()

# Imports
import json
import os
import shutil
import time
import webbrowser
from ctypes import windll

import numpy
import win32api
import win32con
import win32gui
import win32ui
from PIL import Image, ImageOps

# CHECK/SET PATH
code_folder = os.path.abspath(__file__)
code_folder = os.path.split(code_folder)[0]
os.chdir(code_folder)

# LOAD SETTINGS
settings = json.load(open("settings.json"))
MAP_SIZE = settings["map_size"]
DIFFICULTY = settings["difficulty"]
QUICK_AND_FEEBLE = settings["modifiers"]["quick_and_feeble"]
LONG_CYCLES = settings["modifiers"]["long_cycles"]
MAZE = settings["modifiers"]["maze"]
DOUBLE_IRON = settings["modifiers"]["double_iron"]

CONVERT_SAVEGAME = settings["convert_savegame"]
CONVERSION_FOLDER = settings["conversion_folder"]

# If you have trouble with desyncing inputs, increase this value.
# All idle times will be multiplied with this.
# Do not go below 1, some inputs have fixed minimum animation lengths
PC_SPEED_MODIFIER = 1

# Timeout for game launch
GAME_OPEN_TIMER = 60

# ONLY CHANGE IF THE GAME CHANGES:
GAME_DATA_PATH = os.path.join(os.getenv('APPDATA'), r"Godot\app_userdata\Dome Keeper")
SEED_STORAGE_PATH = f'{GAME_DATA_PATH} Seeds'

# Find the correct values for your key here:
# https://learn.microsoft.com/en-us/windows/win32/inputdev/virtual-key-codes
KEY_CONFIRM = 0x20
KEY_UP = 0x57
KEY_DOWN = 0x53
KEY_LEFT = 0x41
KEY_RIGHT = 0x44
KEY_ESCAPE = 0x1B

ACTIVE_COLOR = (255, 227, 191)


class Game():

    def __init__(self) -> None:
        self.game_window = None
        self.source_json_path = os.path.join(GAME_DATA_PATH, "savegame_0.json")
        self.source_map_path = os.path.join(GAME_DATA_PATH, "savegame_0_map.scn")
        self.folder_name = f'{MAP_SIZE[0]}{DIFFICULTY[0]}'
        if QUICK_AND_FEEBLE:
            self.folder_name += "q"
        if LONG_CYCLES:
            self.folder_name += "l"
        if MAZE:
            self.folder_name += "m"
        if DOUBLE_IRON:
            self.folder_name += "d"
        self.seed_folder = os.path.join(SEED_STORAGE_PATH, self.folder_name)
        if not os.path.exists(self.seed_folder):
            os.mkdir(self.seed_folder)

        if seeds:=os.listdir(self.seed_folder):
            self.current_folder = int(max([int(seed) for seed in seeds])) + 1
        else:
            self.current_folder = 1
        
        self.current_decoded_save_json = os.path.join(self.seed_folder, str(self.current_folder), "savegame_0_decrypted.json")
        self.current_decoded_save_map = os.path.join(self.seed_folder, str(self.current_folder), "savegame_0_map.tscn")

    # just gives infos about the game
    def is_running(self):
        self.game_window = win32gui.FindWindow("Engine", "Dome Keeper")
        if self.game_window:
            return True
        else:
            return False

    def is_main_menu(self):
        pass

    def save_file_exists(self):
        # Maybe redo with if... elif... else
        match (os.path.exists(self.source_json_path)) + (os.path.exists(self.source_map_path)):
            case 0:
                return False
            case 1:
                print("Warning: Partial save file detected! Something corrupted your save!")
                return False
            case 2:
                return True

    def get_window_size(self):
        size = win32gui.GetWindowRect(self.game_window)
        csize = win32gui.GetClientRect(self.game_window)
        w, h = size[2]-size[0], size[3]-size[1]
        h_border = (w - csize[2]) // 2
        t_border = (h - csize[3]) - h_border
        w -= h_border*2
        h -= t_border + h_border
        return w, h

    def get_window_frame(self):
        self.show()
        width, height = self.get_window_size()

        # OBTAIN IMAGE OF THE WINDOW SCREEN
        hwnd_dc = win32gui.GetWindowDC(self.game_window)
        mfc_dc = win32ui.CreateDCFromHandle(hwnd_dc)
        save_dc = mfc_dc.CreateCompatibleDC()
        save_bit_map = win32ui.CreateBitmap()
        save_bit_map.CreateCompatibleBitmap(mfc_dc, width, height)
        save_dc.SelectObject(save_bit_map)
        result = windll.user32.PrintWindow(self.game_window, save_dc.GetSafeHdc(), 1)
        if result == 0:
            return False
        bmpinfo = save_bit_map.GetInfo()
        bmpstr = save_bit_map.GetBitmapBits(True)
        img = Image.frombuffer(
            'RGB',
            (bmpinfo['bmWidth'], bmpinfo['bmHeight']),
            bmpstr, 'raw', 'BGRX', 0, 1)
        win32gui.DeleteObject(save_bit_map.GetHandle())
        save_dc.DeleteDC()
        mfc_dc.DeleteDC()
        win32gui.ReleaseDC(self.game_window, hwnd_dc)
        return img

    # modify just the window
    def show(self):
        ''' 
        Shows the Window if it is minimized
        '''
        if win32gui.GetWindowPlacement(self.game_window)[1] == win32con.SW_SHOWMINIMIZED:
            print("Window must not be minimized (but can be in Background or another virtual Desktop)")
            win32gui.ShowWindow(self.game_window, win32con.SW_NORMAL)
            time.sleep(3*PC_SPEED_MODIFIER)
        return True

    # interact with the window
    def press_key(self, key_code):
        win32api.PostMessage(self.game_window, win32con.WM_KEYDOWN, key_code, 0)
        time.sleep(0.05*PC_SPEED_MODIFIER)
        win32api.PostMessage(self.game_window, win32con.WM_KEYUP, key_code, 0)
        time.sleep(0.05*PC_SPEED_MODIFIER)
        return True

    # modify the state of the game
    def start(self):
        # TODO: Check if steam is open! Problems occur when steam is started through this
        webbrowser.open("steam://rungameid/1637320")
        SLEEP_TIME = 2
        retry_time = GAME_OPEN_TIMER * PC_SPEED_MODIFIER
        while retry_time > 0:
            self.game_window = win32gui.FindWindow("Engine", "Dome Keeper")
            if not self.game_window:
                time.sleep(SLEEP_TIME*PC_SPEED_MODIFIER)
                retry_time -= SLEEP_TIME*PC_SPEED_MODIFIER
                continue
            return True
        return False

    def new_game(self, continue_button_exists):
        # Enter Loadout Selection
        if continue_button_exists:
            self.press_key(KEY_RIGHT)
        self.press_key(KEY_CONFIRM)

        time.sleep(2*PC_SPEED_MODIFIER)

        # Enter Map selection
        self.press_key(KEY_CONFIRM)

        # Set difficulty
        difficulties = {
            "normal": 0,
            "hard": 1,
            "brutal": 2,
            "YAFI": 3
        }
        for _ in range(4):
            self.press_key(KEY_UP)
        for _ in range(2):
            self.press_key(KEY_LEFT)
        for _ in range(difficulties[DIFFICULTY]):
            self.press_key(KEY_RIGHT)
        self.press_key(KEY_CONFIRM)
        for _ in range(difficulties[DIFFICULTY]):
            self.press_key(KEY_LEFT)
        
        self.press_key(KEY_DOWN)
        # set map size
        sizes = {
            "small": 0,
            "medium": 1,
            "large": 2,
            "huge": 3
        }
        for _ in range(sizes[MAP_SIZE]):
            self.press_key(KEY_RIGHT)
        self.press_key(KEY_CONFIRM)
        for _ in range(sizes[MAP_SIZE]):
            self.press_key(KEY_LEFT)
        self.press_key(KEY_DOWN)
        picture = self.get_window_frame()

        pixels = picture.load()
        size = self.get_window_size()

        window_ratio = size[0]/size[1]
        o_size = size
        if window_ratio < 16/9:
            size = size[0], size[0]/16*9
        else:
            size = size[1]/9*16, size[1]

        box_size = int(size[0]*0.01)

        w1 = size[0]*0.295 + (o_size[0] - size[0])/2
        w2 = size[0]*0.521 + (o_size[0] - size[0])/2
        h1 = size[1]*0.710 + (o_size[1] - size[1])/2
        h2 = size[1]*0.775 + (o_size[1] - size[1])/2

        w1, w2, h1, h2 = [int(x) for x in [w1, w2, h1, h2]]

        def is_active(w, h):
            active_pixels = 0
            for x in range(w-box_size, w+box_size):
                for y in range(h-box_size, h+box_size):
                    if pixels[x, y] == ACTIVE_COLOR:
                        active_pixels += 1
            return active_pixels > 0

        # Colors as of 2022-10-21
        # inactive Color: (18, 18, 26)
        # active Color: (255, 227, 191)

        if QUICK_AND_FEEBLE != is_active(w1, h1):
            self.press_key(KEY_CONFIRM)
        self.press_key(KEY_RIGHT)
        if LONG_CYCLES != is_active(w2, h1):
            self.press_key(KEY_CONFIRM)
        self.press_key(KEY_LEFT)
        self.press_key(KEY_DOWN)
        if MAZE != is_active(w1, h2):
            self.press_key(KEY_CONFIRM)
        self.press_key(KEY_RIGHT)
        if DOUBLE_IRON != is_active(w2, h2):
            self.press_key(KEY_CONFIRM)
        self.press_key(KEY_DOWN)

        # Enter Game
        self.press_key(KEY_CONFIRM)           

    def next_seed(self):
        self.current_folder += 1
        self.current_decoded_save_json = os.path.join(self.seed_folder, str(self.current_folder), "savegame_0_decrypted.json")
        self.current_decoded_save_map = os.path.join(self.seed_folder, str(self.current_folder), "savegame_0_map.tscn")

    def quit_to_title(self):
        inputs = [
            [KEY_ESCAPE, 0.3],
            [KEY_DOWN, 0.2],
            [KEY_DOWN, 0.2],
            [KEY_CONFIRM, 0.1],
            [KEY_CONFIRM, 3]
        ]
        for input in inputs:
            self.press_key(input[0])
            time.sleep(input[1]*PC_SPEED_MODIFIER)


    def select_loadout(self):
        # TODO: Implement maybe
        inputs = [
            KEY_UP,
            KEY_UP,
            KEY_UP,
            KEY_LEFT,
            KEY_CONFIRM,
            # 
        ]
        return True

    # Modify/move/etc. the savefiles
    def store_save(self):
        current_storage_folder = os.path.join(self.seed_folder, str(self.current_folder))
        os.mkdir(current_storage_folder)
        shutil.copy(self.source_json_path, current_storage_folder)
        shutil.copy(self.source_map_path, current_storage_folder)

    def convert_savefiles(self):
        cwd = os.getcwd()
        # thanks to https://github.com/rubychill/godot-scn-to-tscn
        shutil.copy(self.source_json_path, CONVERSION_FOLDER)
        shutil.copy(self.source_map_path, CONVERSION_FOLDER)
        os.chdir(CONVERSION_FOLDER)
        # TODO: Supress Code Errors
        os.system('cmd /c "godot -s scn_to_tscn.gd --no-window --quiet"')
        os.system('cmd /c "godot -s json_decrypt.gd --no-window --quiet"')
        shutil.move(os.path.join(CONVERSION_FOLDER, "savegame_0_decrypted.json"), self.current_decoded_save_json)
        shutil.move(os.path.join(CONVERSION_FOLDER, "savegame_0_map.tscn"), self.current_decoded_save_map)
        os.chdir(cwd)

    def seed_ranking(self):
        pass

    def seed_hash(self):
        pass

    # other helper functions
    # could be moved out of the class but more convenient here
if CONVERT_SAVEGAME:
    images = { # TODO: MOVE TO OTHER LOCATIONr
        "iron":   Image.open(os.path.join(CONVERSION_FOLDER, r"content\icons\icon_iron.png")),
        "cobalt": Image.open(os.path.join(CONVERSION_FOLDER, r"content\icons\sand.png")),
        "water":  Image.open(os.path.join(CONVERSION_FOLDER, r"content\icons\icon_water.png")),
        "rocks1": Image.open(os.path.join(CONVERSION_FOLDER, r"content\map\tile\new_rocks\rocks1.png")),
        "rocks2": Image.open(os.path.join(CONVERSION_FOLDER, r"content\map\tile\new_rocks\rocks2.png")),
        "rocks3": Image.open(os.path.join(CONVERSION_FOLDER, r"content\map\tile\new_rocks\rocks3.png")),
        "rocks4": Image.open(os.path.join(CONVERSION_FOLDER, r"content\map\tile\new_rocks\rocks4.png")),
        "rocks5": Image.open(os.path.join(CONVERSION_FOLDER, r"content\map\tile\new_rocks\rocks5.png")),
        "rocks6": Image.open(os.path.join(CONVERSION_FOLDER, r"content\map\tile\new_rocks\rocks6.png")),
        "gadget": Image.open(os.path.join(CONVERSION_FOLDER, r"content\drop\gadget\gadget.png")),
        "relic":  Image.open(os.path.join(CONVERSION_FOLDER, r"content\drop\relic\relic.png")),
    }
    for image in images:
        images[image] = images[image].convert("RGBA")

class seed():

    def __init__(self, json_file_path, map_file_path) -> None:
        self.generate_data_base(json_file_path, map_file_path)
    
    def generate_data_base(self, json_file_path, map_file_path):

        # JSON Data
        self.json = json.load(open(json_file_path))

        def PoolIntArray_to_data_dict(data: str):
            data = data.replace("tile_data = PoolIntArray(", "")
            data = data.replace(")", "")
            data = data.split(",")
            data = [int(date) for date in data]
            data = numpy.array_split(data, len(data)/3)
            new_data = {}
            for tile in data:
                val = tile[0]/2**16
                y = round(val)
                x = tile[0] - y*2**16
                if x < 0: # way faster than flooring y
                    y -= 1
                new_data[(x, y)] = tile[1]
            return new_data

        with open(map_file_path, "r") as file:
            self.biomes, self.hardness, self.resources = list(filter(lambda line:line.startswith("tile_data"), file.readlines()))
            
        self.biomes = PoolIntArray_to_data_dict(self.biomes)
        self.hardness = PoolIntArray_to_data_dict(self.hardness)
        self.resources = PoolIntArray_to_data_dict(self.resources)

    # Helper Functions
    def tile_hits(self, x, y, drillstrenght):
        '''
        Returns the needed hits for destroying a block
        0 => No Block
        9999 => Indestructable
        '''
        INDESTRUCTABLE = 9999

        hardness_multiplier = {
            13: 0,
            14: 1,
            15: 2,
            16: 3,
            17: 4
        }

        resource_bonus_health = {
            0: 2,  # Iron
            1: 3,  # Water
            2: 1,  # Cobalt
            3: 6,  # Gadget
            4: 8,  # Relic
            10: 0, # Normal stone
            11: 0, # TODO: FIND OUT! VERY RARE AND COULDN'T FIND DIFFERENCE TO NORMAL STONE
        }
        # 9  -> (Mushroom) Cave
        # 10 -> stone
        # 21 -> indestructable
 
        tilebasehealth = self.json["Data"]["map.tilebasehealth"]
        tilehealthbasemultiplier = self.json["Data"]["map.tilehealthbasemultiplier"]
        tilehealthmultiplierperlayer = self.json["Data"]["map.tilehealthmultiplierperlayer"]
        
        tile_hp = tilebasehealth
        tile_hp *= tilehealthbasemultiplier
        if self.hardness[(x, y)] == 18:
            return INDESTRUCTABLE
        tile_hp *= hardness_multiplier[self.hardness[(x, y)]]
        tile_hp *= tilehealthmultiplierperlayer**(self.biomes[(x, y)]-10)
        if self.resources.get((x, y), None) == None: # No Block
            return 0
        if self.resources[(x, y)] == 9: # cave
            return 0
        if self.resources[(x, y)] == 21:
            return INDESTRUCTABLE
        tile_hp += resource_bonus_health[self.resources[(x, y)]]
        tile_hp = round(tile_hp)
        
        return round(tile_hp/drillstrenght)

    def tile_dist(self, x, y, x2=0, y2=0):
        return abs(x-x2) + abs(y-y2)

    def neighbour_tiles(self, map_data: dict, x, y):# TODO: REDO
        neighbours = [
            map_data.get((x+1, y), None),
            map_data.get((x-1, y), None),
            map_data.get((x, y+1), None),
            map_data.get((x, y-1), None)
        ]
        return filter(lambda value:value!=None, neighbours)
            

    # to be used outside
    def summary(self, seed_folder, current_folder):
        seed_data = json.load(open(os.path.join(seed_folder, str(current_folder), "savegame_0_decrypted.json")))
        seed_summary = [
            f'LevelTechs: {", ".join(seed_data["LevelTechs"])}',
            f'Loadout: {", ".join([str(item) for item in seed_data["Loadout"].items()])}',
            f'',
            f'Biome Colors: {", ".join(seed_data["Map"]["Biomes"][:len(seed_data["Map"]["CurrentIronCountByLayer"])])}',
            f'Iron per Biome {"-".join([str(number) for number in seed_data["Map"]["CurrentIronCountByLayer"].values()])}',
            f'',
            f'Run time: {seed_data["RunTime"]}',
            f''
        ]
        for map_object in seed_data["Objects"]["100"]:
            if "RelicChamber"  in map_object["meta.name"]:
                seed_summary.append(f'{map_object["meta.name"]}: {map_object["coord"]}')
            if "RelicSwitchChamber"  in map_object["meta.name"]:
                seed_summary.append(f'{map_object["meta.name"]}: {map_object["coord"]}')
            if map_object["meta.kind"] == "cave":
                seed_summary.append(f'{map_object["meta.name"]}: {map_object["coord"]}')

        with open(os.path.join(seed_folder, str(current_folder), "summary.txt"), "w") as file:
            for line in seed_summary:
                file.write(f'{line}\n')

        pass 
        # All Blocks infos
        hits = [self.tile_hits(*vector, 34) for vector in self.hardness]
        hits = sum(list(filter(lambda hit:hit!=9999, hits)))
        print(f'Seed needs {hits} hits for all blocks with Tier 3 Drill')
        return hits


    def visualize(self, seed_folder, current_folder):
        x_coords = [abs(tile[0]) for tile in self.biomes]
        y_coords = [tile[1] for tile in self.biomes]
        size = max(max(x_coords)*2, max(y_coords)) + 10
        size = size*24

        image = Image.new("RGBA", (size*2, size*2), 0x000000)
        pixels = image.load()

        biome_colors = {
            "grey": (25, 25, 25, 100),
            "green": (0, 100, 0, 100),
            "red": (100, 0, 0, 100),
            "yellow": (100, 100, 0, 100),
            "blue": (0, 0, 100, 100),
        }

        biom_list = self.json["Map"]["Biomes"]

        for vector, value in self.biomes.items():
            start = (vector[0]*24+size//2, vector[1]*24+size//10)
            end = (start[0]+24, start[1]+24)
            image.paste(biome_colors[biom_list[value-10]], (*start, *end))
            image.paste(biome_colors[biom_list[value-10]], (start[0], start[1]+size, end[0], end[1]+size))

        for vector, value in self.hardness.items():
            offset = (vector[0]*24+size//2, vector[1]*24+size//10)
            image.paste(ImageOps.grayscale(images[f"rocks{value-12}"]), offset, images[f"rocks{value-12}"])
            image.paste(ImageOps.grayscale(images[f"rocks{value-12}"]), (offset[0]+size, offset[1]), images[f"rocks{value-12}"])

        for vector, value in self.resources.items():
            offset = (vector[0]*24+size//2, vector[1]*24+size//10)
            match value:
                case 0:
                    image.paste(images[f"iron"], offset, images[f"iron"])
                    image.paste(images[f"iron"], (offset[0]+size, offset[1]+size), images[f"iron"])
                case 1:
                    image.paste(images[f"water"], offset, images[f"water"])
                    image.paste(images[f"water"], (offset[0]+size, offset[1]+size), images[f"water"])
                case 2:
                    image.paste(images[f"cobalt"], offset, images[f"cobalt"])
                    image.paste(images[f"cobalt"], (offset[0]+size, offset[1]+size), images[f"cobalt"])
                case 3:
                    image.paste(images[f"gadget"], offset, images[f"gadget"])
                    image.paste(images[f"gadget"], (offset[0]+size, offset[1]+size), images[f"gadget"])
                case 4:
                    image.paste(images[f"relic"], offset, images[f"relic"])
                    image.paste(images[f"relic"], (offset[0]+size, offset[1]+size), images[f"relic"])

        image.save(os.path.join(seed_folder, str(current_folder), "map.png"))
    

def main():

    # Initial Setup of the game
    dome_game = Game()
    while not dome_game.is_running():
        if dome_game.start():
            print(f'Started the Game!')
        else:
            print(f'Couldnt start Game within {GAME_OPEN_TIMER} seconds!')
            if input(f'Did something went wrong? Type exit to quit or enter to retry window finding').lower() == "exit":
                exit()

    # Game started! Checking for the Mod
    if os.path.exists(os.path.join(GAME_DATA_PATH, "Mods")):
        input(f'Potential modding detected! Please select desired mods and launch into the main menu. Press enter to continue...')
    else:
        time.sleep(5*PC_SPEED_MODIFIER)



    # starting generation loop:
    while True:
        dome_game.new_game(dome_game.save_file_exists())
        time.sleep(1.5*PC_SPEED_MODIFIER)
        dome_game.press_key(KEY_CONFIRM)
        time.sleep(6.5*PC_SPEED_MODIFIER)
        dome_game.quit_to_title()
        dome_game.store_save()
        if CONVERT_SAVEGAME:
            dome_game.convert_savefiles()
            cseed = seed(dome_game.current_decoded_save_json, dome_game.current_decoded_save_map)
            cseed.summary(dome_game.seed_folder, dome_game.current_folder)
            cseed.visualize(dome_game.seed_folder, dome_game.current_folder)

        print(f'Seed generated and saved as {dome_game.current_folder}')
        dome_game.next_seed()
        pass







if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Seed generation interrupted! Exiting programm...")
