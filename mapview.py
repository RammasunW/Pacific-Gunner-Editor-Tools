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
positions = []
names = []
colors = []

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
def load_entities(level_var):
    global positions
    global names
    global colors
    # -----------------------------
    # READ ENTITY DATA
    # -----------------------------
    with open('move.dat', 'r') as file:
        data_lines = file.readlines()

    pos_regex = r'vec3 pos = \((-?\d+\.?\d*), (-?\d+\.?\d*), (-?\d+\.?\d*)\)'
    ang_regex = r'vec3 ang = \((-?\d+\.?\d*), (-?\d+\.?\d*), (-?\d+\.?\d*)\)'
    name_regex = r'string name = "(\w+)"'

    positions = []
    names = []
    colors = []

    for i in range(len(data_lines)):
        line = data_lines[i]
        if level_var in line:
            pos_match = re.search(pos_regex, data_lines[i+2])
            ang_match = re.search(ang_regex, data_lines[i+3])
            name_match = re.search(name_regex, data_lines[i])

            if pos_match and name_match and ang_match:
                x = float(pos_match.group(1))
                y = float(pos_match.group(2))
                z = float(pos_match.group(3))
                
                angle_y = float(ang_match.group(2))
                positions.append((x, y, z, angle_y))
                names.append(name_match.group(1))

    # ---- Extract coords ----
    x_coords = [p[0] for p in positions]
    y_coords = [p[1] for p in positions]
    z_coords = [p[2] for p in positions]
    angles = [p[3] for p in positions]

    # ---- Assign colors ----

    for name in names:
        if "_j_" in name:
            if "_P_" in name:
                colors.append('yellow')
            else:
                colors.append('orange')
        elif "_E_" in name or "_e_" in name:
            colors.append('green')
        elif "_P_" in name:
            if "isle" in name or "bush" in name or "palm" in name or "brbwr" in name:
                colors.append('green')
            else:
                colors.append('lightblue')
        else:
            colors.append('navy')

    return x_coords, y_coords, z_coords, angles, names, colors

# -----------------------------
# UPDATE PLOT (KEY FUNCTION)
# -----------------------------
def update_plot(clear=True):
    global cb_drawn
    global cb
    global cursor
    
    ax.clear()

    if current_map is None:
        return

    x_coords, y_coords, z_coords, angles, names, colors = load_entities(current_level)

    # ---- contour ----
    norm = TwoSlopeNorm(
        vmin=current_map.min(),
        vcenter=0,
        vmax=current_map.max()
    )

    # ---- Levels (no duplicate 0) ----
    levels = np.concatenate([
        np.linspace(current_map.min(), 0, 10, endpoint=False),
        np.linspace(0, current_map.max(), 10)
    ])

    cmap = LinearSegmentedColormap.from_list(
        "blue_green",
        [
            (0.0, "darkblue"),
            (0.49, "blue"),
            (0.5, "lightgreen"),
            (1.0, "darkgreen")
        ]
    )
    
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
    if not cb_drawn:
        cb = plt.colorbar(contour, ax=ax)
        cb_drawn = True
    else:
        cb.update_normal(contour)
        cb.norm = contour.norm
        cb.update_ticks()
        
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
    current_level = "L" if val == "0" else f"L{int(val):02d}"
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

    '''positions.append((x, y, z, 0))
    names.append("NEW_ENTITY")

    update_plot(clear=False)'''
    print(f'The point on terrain is {x:.2f}, {y:.2f}, {z:.2f}')





# -----------------------------
# MAIN UI
# -----------------------------
root = tk.Tk()
root.title("Map Viewer")

# Load map button
btn = tk.Button(root, text="Load Map", command=load_map_file)
btn.pack()

# Level dropdown
level_var = tk.StringVar(root)
level_var.set("0")

dropdown = tk.OptionMenu(root, level_var, *[str(i) for i in range(0, 29)], command=change_level)
dropdown.pack()

# -----------------------------
# MATPLOTLIB FIGURE
# -----------------------------
fig, ax = plt.subplots()

# Show plot in separate window
plt.ion()  # interactive mode ON
plt.show()
fig.canvas.mpl_connect("button_press_event", on_click)

# Run UI
root.mainloop()