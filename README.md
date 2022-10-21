**This is a python project to generate or save seeds for Dome Keeper made by https://bippinbits.com/**

Settings/Things to do:
- Save python file and settings.json to any location you want
- Set desired seed in settings.json
  - Difficulties:
    - "normal"
    - "hard" 
    - "brutal"
    - "YAFI"
  - Map Sizes:
    - "small"
    - "medium" 
    - "large"
    - "huge"
  - Modifiers: True/False

DOs:
- You can resize the window at any time. It is recommended to resize it before starting generation
- You can quit the generation by pressing CTRL + C at any time in the script window. Or just close/end the script
- You can have the window in the background or on another virtual desktop. If it is minimized the script will automatially activate it.

DONTs:
- Rightclick the window bar, it will pause the game and mess up timing
- Do any inputs into the window as they might mess up the expected state
- Start in the main menu with any other than the most left button selected

It is untested if other languages than english have a map screen with different dimensions that might mess up modifier detection. Tested in english, if you find problems with other languages let me know!

If you only want to get the scn and encrypted json file you are ready to go. Just run the file, and follow instructions!

If you want to have the tscn, decrypted json, seed summary and a png of the map:
1) Use GDRE Tools https://github.com/kimstars/godotRE to recover the domekeeper.exe to any folder you like
2) Move both .gd files and a Godot.exe https://godotengine.org/download into the recovery folder
3) Set full path of the recovered projet as "conversion_folder" (use \\\\ as separator)
4) Set "convert_savegame" to true
 
You are now ready to go! Just ingore all the Godot Errors.
Seeds will be stored next to the Dome Keeper savegame folder as "Dome Keeper Seeds". Each setting has its own subfolder with naming:
- First letter of difficulty
- First letter of map size
- First letter of modifier if modifier is active



Modules to install:
pywin32
PILLOW
All other should be included in python by default

Created for Dome Keeper version 41.5

Use at own risk, suggestions are welcome!
