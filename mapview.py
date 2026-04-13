import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import TwoSlopeNorm, LinearSegmentedColormap
import tkinter as tk
from tkinter import filedialog
import re
import mplcursors

# -----------------------------
# GLOBAL STATE
# -----------------------------
current_map = None
current_level = "L"
cb = None
cb_drawn = False
cursor = None

entities = []
'''
Structure:
        "level": "L69",
        "name": "L69_xxx",
        "type": "float" | "point",
        "x": 2092.02,
        "y": 0,
        "z": -2474.88,
        "angle_x": 0,
        "angle_y": 22.5,
        "angle_z": 0
'''

# -----------------------------
# LOAD MAP
# -----------------------------
def load_map_file():
    global current_map

    filename = filedialog.askopenfilename(
        title="Select heightmap",
        filetypes=[("Map files", "*.map")]
    )

    if not filename:
        return

    current_map = np.loadtxt(filename, comments="end:")
    update_plot()

# -----------------------------
# LOAD ENTITIES
# -----------------------------
def load_entities():
    global entities
    # -----------------------------
    # READ ENTITY DATA
    # -----------------------------
    with open('move.dat', 'r') as file:
        data_lines = file.readlines()

    pos_regex = r'vec3 pos = \((-?\d+\.?\d*), (-?\d+\.?\d*), (-?\d+\.?\d*)\)'
    ang_regex = r'vec3 ang = \((-?\d+\.?\d*), (-?\d+\.?\d*), (-?\d+\.?\d*)\)'
    name_regex = r'string name = "(\w+)"'
    type_regex = r'string type = "(\w+)"'
    level_regex = r'(L\d{2})'

    for i in range(len(data_lines)-4):
        name_match = re.search(name_regex, data_lines[i])
        level_match = re.search(level_regex, data_lines[i])
        type_match = re.search(type_regex, data_lines[i+1])
        pos_match = re.search(pos_regex, data_lines[i+2])
        ang_match = re.search(ang_regex, data_lines[i+3])

        if pos_match and name_match and ang_match:
            
            name = name_match.group(1)
            if "_j_" in name: # Enemy
                if "_P_" in name: # Enemy buildings
                    color = 'yellow'
                else: #Enemy ships
                    color = 'orange'
            # Friendly
            elif "_E_" in name or "_e_" in name: # Terrain
                color = 'green'
            elif "_P_" in name: # Terrain
                if "isle" in name or "bush" in name or "palm" in name or "brbwr" in name:
                    color = 'green'
                else: # Friendly buildings
                    color = 'lightblue'
            else: # Friendly ships
                color = 'navy'
            
            entities.append({
            "level": level_match.group(1) if level_match else "L00",
            "name": name,
            "type": type_match.group(1),
            "x": float(pos_match.group(1)),
            "y": float(pos_match.group(2)),
            "z": float(pos_match.group(3)),
            "angle_x": float(ang_match.group(1)),
            "angle_y": float(ang_match.group(2)),
            "angle_z": float(ang_match.group(3)),
            "color": color
            })


def get_entities_for_level(level):
    global entities
    return [e for e in entities if e["level"] == level]

# -----------------------------
# UPDATE PLOT (KEY FUNCTION)
# -----------------------------
def update_plot(clear=True):
    global cb_drawn
    global cb
    global cursor
    global entities
    global current_level
    
    ax.clear()

    if current_map is None:
        return
    
    current_entities = get_entities_for_level(current_level)
    
    x_coords = [e["x"] for e in current_entities]
    y_coords = [e["y"] for e in current_entities]
    z_coords = [e["z"] for e in current_entities]
    names    = [e["name"] for e in current_entities]
    angles   = [e["angle_y"] for e in current_entities]
    colors   = [e["color"] for e in current_entities]


    # ---- contour ----
    if current_map.min() == current_map.max():
        norm = None
        cmap = "Blues"
        
    else:
        norm = TwoSlopeNorm(
            vmin=current_map.min(),
            vcenter=0,
            vmax=current_map.max()
        )
        
        cmap = LinearSegmentedColormap.from_list(
        "blue_green",
        [
            (0.0, "darkblue"),
            (0.49, "blue"),
            (0.5, "lightgreen"),
            (1.0, "darkgreen")
        ]
    )

    # ---- Levels (no duplicate 0) ----
    levels = np.concatenate([
        np.linspace(current_map.min(), 0, 10, endpoint=False),
        np.linspace(0, current_map.max(), 10)
    ])
    levels = np.unique(levels)
    
    extent = [-5000, 5000, -5000, 5000]

    # ---- HEIGHTMAP (scaled to world coords) ----
    contour = ax.contourf(
        current_map,
        levels=levels,
        cmap=cmap,
        norm=norm,
        extent=extent  # IMPORTANT
    )

    # ---- Coastline ----
    ax.contour(
        current_map,
        levels=[0],
        colors='black',
        linewidths=2,
        extent=extent
    )

    # ---- Entities ----
    scatter = ax.scatter(x_coords, z_coords, c=colors, s=80, edgecolors='black', linewidths=2)
    
    # ---- Entity Angles ----
    dx = [np.cos(np.radians(a)) for a in angles]
    dz = [np.sin(np.radians(a)) for a in angles]

    ax.quiver(
        x_coords,
        z_coords,
        dx,
        dz,
        color='red',
        scale=30,        # adjust arrow size
        width=0.003
    )

    # ---- Labels ----
    ax.set_xlabel('X')
    ax.set_ylabel('Z')
    ax.set_title(f'Entities + Heightmap ({current_level})')

    # ---- Colorbar ----
    cax.clear()
    cb = plt.colorbar(contour, cax=cax)
        
    # ---- Hover tool ----
    if cursor is not None:
        cursor.remove()
    
    cursor = mplcursors.cursor(scatter, hover=True)

    @cursor.connect("add")
    def on_add(sel):
        i = sel.index
        sel.annotation.set_text(
            f'{names[i]}\n({x_coords[i]}, {y_coords[i]}, {z_coords[i]})'
        )


    fig.canvas.draw()

# -----------------------------
# LEVEL CHANGE
# -----------------------------
def change_level(val):
    global current_level
    val = val[:2]
    current_level = "L" if val == "00" else f"L{int(val):02d}"
    update_plot()


# -----Get terrain height-----
def world_to_grid(x, z, data):
    xmin, xmax = -5000, 5000
    zmin, zmax = -5000, 5000

    nx, nz = data.shape

    # normalize to [0, 1]
    u = (x - xmin) / (xmax - xmin)
    v = (z - zmin) / (zmax - zmin)

    # convert to grid indices
    i = u * (nx - 1)
    j = v * (nz - 1)

    return i, j

def get_height(x, z, data):
    i, j = world_to_grid(x, z, data)

    i0, j0 = int(i), int(j)
    i1, j1 = min(i0 + 1, data.shape[0] - 1), min(j0 + 1, data.shape[1] - 1)

    # fractional part
    di = i - i0
    dj = j - j0

    # 4 surrounding heights
    h00 = data[j0][i0]
    h10 = data[j0][i1]
    h01 = data[j1][i0]
    h11 = data[j1][i1]

    # bilinear interpolation
    h = (
        h00 * (1 - di) * (1 - dj) +
        h10 * di * (1 - dj) +
        h01 * (1 - di) * dj +
        h11 * di * dj
    )

    return h

def get_entity_y(x, z, data):
    h = get_height(x, z, data)

    if h < 0:
        return 0   # sea
    else:
        return h   # land



# Click to add

def on_click(event):
    if event.inaxes != ax:
        return

    x = event.xdata
    z = event.ydata

    y = get_entity_y(x, z, current_map)
    print(f'The point on terrain is {x:.2f}, {y:.2f}, {z:.2f}')





# -----------------------------
# MAIN UI
# -----------------------------
root = tk.Tk()
root.title("Map Viewer")

load_entities()

# Load map button
btn = tk.Button(root, text="Load Map", command=load_map_file)
btn.pack()

# Level dropdown
level_var = tk.StringVar(root)
level_var.set("Choose Level")

menu_entries = [
"00 - All",
"01 - Aleutian",
"02 - Alpha",
"03 - Bonin",
"04 - Xmas",
"05 - Coral Sea",
"06 - Corregidor",
"07 - Espiritu Santo",
"08 - Fiji",
"09 - Formosa",
"10 - Guadalcanal",
"11 - Guam",
"12 - Iwo Jima",
"13 - Johnston",
"14 - Kwajalein",
"15 - Leyte Gulf",
"16 - Marcus",
"17 - Midway",
"18 - New Guinea",
"19 - North Pacific",
"20 - Noumea",
"21 - Okinawa",
"22 - Pearl Harbor",
"23 - Philippine Sea",
"24 - Sansapor",
"25 - Sierra Whiskey",
"26 - Tahiti",
"27 - Tarawa",
"28 - Wake",
]

dropdown = tk.OptionMenu(root, level_var, *menu_entries, command=change_level)
dropdown.pack()

# -----------------------------
# MATPLOTLIB FIGURE
# -----------------------------
fig, ax = plt.subplots()
cax = fig.add_axes([0.88, 0.1, 0.03, 0.8])

# Show plot in separate window
plt.ion()  # interactive mode ON
plt.show()
fig.canvas.mpl_connect("button_press_event", on_click)

# Run UI
root.mainloop()
