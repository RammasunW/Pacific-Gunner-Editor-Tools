# Pacific-Gunner-Editor-Tools
Tools for modifying Pacific Gunner.

WIP, so far 2 tools are available.
Vibe coding turns out the be so effective! Big thanks to ChatGPT.

## Map mixing tool (mix_map.py):
Mixes the height files (.map format) of two maps to generate one map that includes highest points from both maps.

As we know, this game stores map objects and their "collisions" separately. Map objects can be easily accessed and copy-pasted throughout level files. But they don't technically have collisions. Instead, a height file of a level stores the highest points in order to fake map collisions. Heights are stored in a 200x200 grid. Negative numbers represent depth, 0 represents sea level, and positive ones represent ground height.

If you want to combine two maps, let's say Guam and Xmas Island, you need to compare one map file to another and generate a new one that contains the highest heights of both files so that you have map collisions from both levels. This tool makes it easy: we read a height file as a fat 2D grid and simply loop over each value. To use it, run the script, select height file 1 and height file 2 (must be .map formatted like original .map files), and finally select a folder and name the new file with mixed maps! In fact, you can run this several times to combine more than 2 maps together!


Demonstration: https://youtu.be/G4JtEPnEnz0


Here is an example of mixing 5 levels with small isles:
![mapped3](https://user-images.githubusercontent.com/70968294/227723333-317fc7da-5c20-4eba-93d2-3bce3a685f3b.jpg)


## Map visualization tool (mapview.py):
Categorizes and visualizes coordinates from move.dat, the file that stores all coordinates of in-game objects and entities. Coord colors correspond to in-game radar colors (green dots are for map objects).

First, copy and paste the move.dat tool in game's data directory to the tool's directory.

Then, to use the tool, run the script.

`cd` to the folder of the script

then run `python mapview.py`

The UI provides the following functionalities:
- Load .map file and draw its contour.
- Load move.dat and draw entities on the map, you can filter them by level. The red arrow indicates the orientation (y-rotation) of the entity.
- Load pth_area_xyz.dat and draw paths on the map as yellow arrows. Use index -1 for all paths, and any other index for a specific path.
- Add / edit / delete entries from move.dat and save it as a new file.
- In "select" mode, drag a dot to modify its location. The new height (y-value) is automatically calculated for you.
- In "select" mode, scroll up / down to adjust its orientation. Or use "edit" to modify its name and orientation manually.
- Hover you mouse over a dot to see its details.
- Click on the map to read its xyz-coordinates (height is automatically calculated).

Known bugs:
- If a map is completely flat (e.g. Leyte Gulf) there will be an error.
- After typing the index of a path, you need to manually click up / down in order to view it.

Screenshots:

- All entries in my customized move.dat plotted on the map
  ![git1](https://github.com/user-attachments/assets/756fb826-1662-4bd3-87d6-6a27b38563e2)

- All entities and all paths in level "Guam"
  ![git2](https://github.com/user-attachments/assets/047c8658-b6d1-47ee-ac48-1f067c0080a1)

- The path (FrPa01a in level script, or index 96 in pth_area_pearl.dat) of the first aircraft in level "Pearl Harbor" in yellow
  <img width="1745" height="965" alt="pearl96" src="https://github.com/user-attachments/assets/1da65627-f112-417a-8814-f13bc43df95b" />


