# Pacific-Gunner-Editor-Tools
Tools for modifying Pacific Gunner.

WIP, so far 2 tools are available.

Map mixing tool:
Mixes the height files (.map format) of two maps to generate one map that includes highest points from both maps.
As we know, this game stores map objects and their "collisions" separately. Map objects can be easily accessed and copy-pasted throughout level files. But they don't technically have collisions. Instead, a height file of a level stores the highest points in order to fake map collisions. Heights are stored in a 200x200 grid. Negative numbers represent depth, 0 represents sea level, and positive ones represent height. If you want to combine two maps, let's say Guam and Xmas Island, you need to compare one map file to another and generate a new one that contains the highest heights of both files so that you have map collisions from both levels. This tool makes it easy since we read a height file as a fat 2D list and loop over each value. To use it, run the script, select height file 1 and height file 2 (must be .map formatted like original .map files), and finally select a folder and name the new file with mixed maps! In fact, you can run this several times to combine more than 2 maps together! Here is an example of mixing 5 levels all with small isles:
![mapped3](https://user-images.githubusercontent.com/70968294/227723333-317fc7da-5c20-4eba-93d2-3bce3a685f3b.jpg)


Coordinates tool:
Categorizes and visualizes coordinates from move.dat, the file that stores all coordinates of in-game objects and entities. Coord colors correspond to in-game radar colors (green dots are for map objects). First, copy and paste the move.dat tool in game's data directory to the tool's directory. Then, to use the tool, run the script, enter level IDs (which can be found in each level's file, for example, if you want to look at all coordinates used in level Fiji, open area_fiji.dat and you will notice all coordinate names start with L08, therefore enter 8), leave blank if you want to look at ALL COORDINATES FROM ALL LEVELS (the whole move.dat file)! A window will be created and contains an X-Z plane that allows your mouse to hover over and read coordinate names and XYZ values. (DON'T CLICK THE MOUSE, IT WILL PRODUCE ERRORS)

Example of entering 16 as ID (Marcus Island):

![pacificmove2](https://user-images.githubusercontent.com/70968294/227724539-27023479-f729-4c36-9f00-e1acda54c7ef.png)


Here is EVERYTHING in the original game!
![pacificmove](https://user-images.githubusercontent.com/70968294/226758129-8c2cfd20-175e-4edf-9036-ed7b213f1123.png)
