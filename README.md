**This is a python project to generate or save seeds for Dome Keeper made by https://bippinbits.com/**

Settings/Things to do:
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

If you only want to get the scn and encrypted json file you are ready to go.
1) Use GDRE Tools https://github.com/kimstars/godotRE to recover the domekeeper.exe to any folder you like
2) Move both .gd files and a Godot.exe https://godotengine.org/download into this folder
3) Set full path of the recovered projet as "conversion_folder" (use \\ as separator)
4) Set "convert_savegame" to true
 
You are now ready to go! Just ingore all the Godot Errors.
Seeds will be stored next to the Dome Keeper savegame folder as "Dome Keeper Seeds". Each setting has its own subfolder with naming:
First letter of difficulty
Frst letter of map size
first letter of modifier if modifier is active



Modules to install:
pywin32
PILLOW
All other should be included in python by default

Created for Dome Keeper version
Use at own risk, suggestions are welcome!
