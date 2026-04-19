import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import TwoSlopeNorm, LinearSegmentedColormap
import tkinter as tk
from tkinter import filedialog
import re
import mplcursors
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import sys

def on_close():
    root.quit()       # stop Tkinter loop
    root.destroy()    # destroy window
    sys.exit()        # kill Python process

# -----------------------------
# GLOBAL VARS
# -----------------------------
current_map = None
current_level = "L"
cb = None
cb_drawn = False
cursor = None
level_val = 0


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

level_names = [
"All",
"aleutian",
"alpha",
"bonin",
"xmas",
"coralsea",
"corregidor",
"santo",
"fiji",
"formosa",
"guadalcanal",
"guam",
"iwojima",
"johnston",
"kwajalein",
"leytegulf",
"marcus",
"midway",
"newguinea",
"npacific",
"noumea",
"okinawa",
"pearl",
"philippinesea",
"sansapor",
"whiskey",
"tahiti",
"tarawa",
"wake",
]


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

# For editing
selected_entity = None
mode = "select"   # "select", "add", "delete"
coord_label = None
dragging = False
dragged_entity = None

targets = {}
paths = []
show_paths = True
selected_path_index = -1

def load_paths_file(filename):
    global targets, paths
    targets.clear()
    paths.clear()
    targets = {}
    paths = []

    with open(filename, 'r') as f:
        lines = f.readlines()

    mode = None

    for line in lines:
        line = line.strip()

        if line.startswith("targets:"):
            mode = "targets"
            continue
        elif line.startswith("paths:"):
            mode = "paths"
            continue

        # ---- TARGETS ----
        if mode == "targets" and line.startswith("target:"):
            parts = line.split()
            tid = int(parts[1])
            x = float(parts[2])
            y = float(parts[3])
            z = float(parts[4])

            targets[tid] = (x, y, z)

        # ---- PATHS ----
        elif mode == "paths" and line.startswith("path:"):
            parts = line.split("list:")[1].strip().split()
            ids = list(map(int, parts))

            current = []
            '''for i in ids:
                if i == -1:
                    if current:
                        paths.append(current)
                        current = []
                else:
                    current.append(i)'''
            current = ids[:3]

            if current:
                paths.append(current)


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
        
    num = r'[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?'
    pos_regex = rf'vec3 pos = \(\s*({num})\s*,\s*({num})\s*,\s*({num})\s*\)'
    ang_regex = rf'vec3 ang = \(\s*({num})\s*,\s*({num})\s*,\s*({num})\s*\)'
    name_regex = r'string name = "(\w+)"'
    type_regex = r'string type = "(\w+)"'
    level_regex = r'(L\d{2})'

    for i in range(len(data_lines)-4):
        name_match = re.search(name_regex, data_lines[i])
        level_match = re.search(level_regex, data_lines[i])
        type_match = re.search(type_regex, data_lines[i+1])
        pos_match = re.search(pos_regex, data_lines[i+2])
        ang_match = re.search(ang_regex, data_lines[i+3])
        
        if type_match:
            if type_match.group(1) == "path":
                continue

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
    print('Entities loaded:', len(entities))

def edit_selected():
    global selected_entity

    if selected_entity is None:
        print("No entity selected")
        return

    win = tk.Toplevel(root)
    win.title("Edit Entity")

    tk.Label(win, text="Name").grid(row=0, column=0)
    name_entry = tk.Entry(win)
    name_entry.insert(0, selected_entity["name"])
    name_entry.grid(row=0, column=1)

    tk.Label(win, text="Angle Y").grid(row=1, column=0)
    angle_entry = tk.Entry(win)
    angle_entry.insert(0, str(selected_entity["angle_y"]))
    angle_entry.grid(row=1, column=1)

    def save():
        selected_entity["name"] = name_entry.get()
        selected_entity["angle_y"] = float(angle_entry.get())
        win.destroy()
        update_plot()

    tk.Button(win, text="Save", command=save).grid(row=2, columnspan=2)


def get_entities_for_level(level):
    global entities
    return [e for e in entities if e["level"] == level]

# -----------------------------
# UPDATE PLOT (KEY FUNCTION)
# -----------------------------
def update_plot(clear=True, filter_by=None):
    global cb_drawn
    global cb
    global cursor
    global entities
    global current_level
    global selected_entity
    global targets, paths, show_paths
    
    ax.clear()

    if current_map is None:
        return
    
    if filter_by is None:
        current_entities = entities if current_level == "L" else get_entities_for_level(current_level)
    else:
        current_entities = [e for e in entities if filter_by in e["name"]]
    
    x_coords = [e["x"] for e in current_entities]
    y_coords = [e["y"] for e in current_entities]
    z_coords = [e["z"] for e in current_entities]
    names    = [e["name"] for e in current_entities]
    types    = [e["type"] for e in current_entities]
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
    
    # Paths
# ---- PATHS ----
    if show_paths and paths:
        for idx, path in enumerate(paths):

            if selected_path_index != -1 and idx != selected_path_index:
                continue

            xs, zs, dxs, dzs = [], [], [], []

            for i in range(len(path) - 1):
                t1 = path[i]
                t2 = path[i + 1]

                if t1 in targets and t2 in targets:
                    x1, _, z1 = targets[t1]
                    x2, _, z2 = targets[t2]

                    xs.append(x1)
                    zs.append(z1)
                    dxs.append(x2 - x1)
                    dzs.append(z2 - z1)

            if xs:
                ax.quiver(
                    xs, zs,
                    dxs, dzs,
                    angles='xy',
                    scale_units='xy',
                    scale=1,
                    color='yellow',
                    width=0.002
                )
    
    if selected_entity and selected_entity["level"] == current_level:
        ax.scatter(
            selected_entity["x"],
            selected_entity["z"],
            s=200,
            facecolors='none',
            edgecolors='red',
            linewidths=3
        )
    
    # ---- Entity Angles ----
    dx = [np.sin(np.radians(a)) for a in angles]
    dz = [np.cos(np.radians(a)) for a in angles]

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
    ax.set_title(f'Entities + Heightmap ({current_level} {level_names[level_val]})')

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
        f'{names[i]}\nType: {types[i]}\n({x_coords[i]},{y_coords[i]},{z_coords[i]})')


    canvas.draw()

# -----------------------------
# LEVEL CHANGE
# -----------------------------
def change_level(val):
    global level_val, level_name, current_map, current_level
    val = val[:2]
    level_val = int(val)
    current_level = "L" if val == "00" else f"L{int(val):02d}"
    
    if current_level != "L":
        # experimental: change everything in one button
        level_name = level_names[level_val]
        current_map = np.loadtxt("m\\area_" + level_name + ".map", comments="end:")
        
        load_paths_file("m\\pth_area_" + level_name + ".dat")
    
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


def toggle_paths():
    global show_paths
    show_paths = not show_paths
    update_plot()


# Click to add

def on_press(event):
    global selected_entity, dragging, dragged_entity

    if event.inaxes != ax or current_map is None:
        return

    x, z = event.xdata, event.ydata
    y = get_entity_y(x, z, current_map)

    # ---- Always show coordinates ----
    coord_label.config(text=f"X={x:.2f}, Y={y:.2f}, Z={z:.2f}")

    current_entities = get_entities_for_level(current_level)

    # ---- ADD MODE ----
    if mode == "add":
        info = prompt_new_entity()
        
        if not info["name"]:
            return
            
        if info["type"] == "float":
            y = 0
        else:
            y = get_entity_y(x, z, current_map)
        
        new_entity = {
            "level": current_level,
            "name": info["name"],
            "type": info["type"],
            "x": x,
            "y": y,
            "z": z,
            "angle_x": 0,
            "angle_y": info["angle"],
            "angle_z": 0,
            "color": "red"
        }
        entities.append(new_entity)
        selected_entity = new_entity
        update_plot()
        return

    if not current_entities:
        return

    # find closest entity
    closest = min(
        current_entities,
        key=lambda e: (e["x"] - x)**2 + (e["z"] - z)**2
    )

    dist = (closest["x"] - x)**2 + (closest["z"] - z)**2

    # ---- DELETE MODE ----
    if mode == "delete" and dist < 200**2:
        entities.remove(closest)
        update_plot()
        return

    # ---- SELECT + DRAG ----
    if dist < 200**2:
        selected_entity = closest
        dragged_entity = closest
        dragging = True
        update_plot()
    

def on_motion(event):
    global dragging, dragged_entity

    if not dragging or dragged_entity is None:
        return

    if event.inaxes != ax:
        return

    x, z = event.xdata, event.ydata

    # update position
    dragged_entity["x"] = x
    dragged_entity["z"] = z

    # LIVE HEIGHT UPDATE
    if dragged_entity["type"] == "float":
        dragged_entity["y"] = 0
    else:
        dragged_entity["y"] = get_entity_y(x, z, current_map)

    # update coordinate display
    coord_label.config(
        text=f"X={x:.2f}, Y={dragged_entity['y']:.2f}, Z={z:.2f}"
    )

    update_plot()


def on_release(event):
    global dragging, dragged_entity

    dragging = False
    dragged_entity = None
  
  
def on_scroll(event):
    global selected_entity

    if selected_entity is None:
        return
    if mode != "select":
        return

    # adjust rotation speed here
    step = 5  # degrees per scroll

    if event.button == 'up':
        selected_entity["angle_y"] += step
    elif event.button == 'down':
        selected_entity["angle_y"] -= step

    # keep angle in [-180, 180] (optional but clean)
    if selected_entity["angle_y"] > 180:
        selected_entity["angle_y"] -= 360
    elif selected_entity["angle_y"] < -180:
        selected_entity["angle_y"] += 360

    update_plot()


def set_mode(m):
    global mode, mode_var, selected_entity
    mode = m
    if mode == "add":
        selected_entity = None
    mode_var.set(m)
    update_plot()


def prompt_new_entity():
    dialog = tk.Toplevel(root)
    dialog.title("New Entity")

    result = {"name": None, "angle": 0, "type": "float"}

    tk.Label(dialog, text="Name:").grid(row=0, column=0)
    name_entry = tk.Entry(dialog)
    name_entry.grid(row=0, column=1)

    tk.Label(dialog, text="Angle Y:").grid(row=1, column=0)
    angle_entry = tk.Entry(dialog)
    angle_entry.insert(0, "0")
    angle_entry.grid(row=1, column=1)
    
    tk.Label(dialog, text="Type:").grid(row=2, column=0)
    type_var = tk.StringVar(value="float")
    tk.OptionMenu(dialog, type_var, "float", "point").grid(row=2, column=1)

    def submit():
        result["name"] = name_entry.get()
        try:
            result["angle"] = float(angle_entry.get())
        except:
            result["angle"] = 0
        result["type"] = type_var.get()
        dialog.destroy()

    tk.Button(dialog, text="OK", command=submit).grid(row=3, columnspan=2)

    dialog.grab_set()
    root.wait_window(dialog)

    return result


def save_entities():
    global entities
    
    filename = filedialog.asksaveasfilename(
        title="Save move.dat",
        defaultextension=".dat",
        filetypes=[("DAT files", "*.dat")]
    )

    if not filename:
        return

    entities = sorted(entities, key=lambda e: e["level"])
    
    with open(filename, "w") as f:
        for e in entities:
            block = f"""struct move =
{{
\tstring name = "{e['name']}";
\tstring type = "{e['type']}";
\tvec3 pos = ({e['x']:.3f}, {e['y']:.3f}, {e['z']:.3f});
\tvec3 ang = ({e['angle_x']:.1f}, {e['angle_y']:.1f}, {e['angle_z']:.1f});
}};

"""
            f.write(block)

    print(f"Saved to {filename}")
    print('Entities saved:', len(entities))


def on_path_select(selection):
    global selected_path_index

    selected_path_index = selection

    update_plot()


def load_paths_file_dialog():
    filename = filedialog.askopenfilename(
        title="Select paths file",
        filetypes=[("Path files", "*.dat")]
    )

    if not filename:
        return

    load_paths_file(filename)  # your parser
    
    update_plot()


def filter_move():
    update_plot(filter_by=filter_entry.get())


# -----------------------------
# MAIN UI
# -----------------------------
root = tk.Tk()
root.title("Map Viewer")

control_frame = tk.Frame(root)
control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

# Load map button
btn = tk.Button(control_frame, text="Load Terrain (.map)", command=load_map_file)
btn.pack()

# Level dropdown
level_var = tk.StringVar(control_frame)
level_var.set("Choose Level")
dropdown = tk.OptionMenu(control_frame, level_var, *menu_entries, command=change_level)
dropdown.pack()

# Filter move
tk.Label(control_frame, text="Filter move by name").pack()
filter_entry = tk.Entry(control_frame)
filter_entry.pack()
filter_btn = tk.Button(control_frame, text="Filter", command=filter_move)
filter_btn.pack()

menubar = tk.Menu(control_frame)
mode_var = tk.StringVar(value="select")

btn_paths = tk.Button(control_frame, text="Load Paths", command=load_paths_file_dialog)
btn_paths.pack()

toggle_btn = tk.Button(control_frame, text="Toggle Paths", command=toggle_paths)
toggle_btn.pack()

path_spin = tk.Spinbox(control_frame, from_=-1, to=287,
                       command=lambda: on_path_select(int(path_spin.get())))
path_spin.pack()

tk.Label(control_frame, text="Editor Mode:").pack()

tk.Radiobutton(control_frame, text="Select", variable=mode_var, value="select",
               command=lambda: set_mode("select")).pack()
tk.Radiobutton(control_frame, text="Add", variable=mode_var, value="add",
               command=lambda: set_mode("add")).pack()
tk.Radiobutton(control_frame, text="Delete", variable=mode_var, value="delete",
               command=lambda: set_mode("delete")).pack()
tk.Button(control_frame, text="Edit Point", command=edit_selected).pack()

coord_label = tk.Label(control_frame, text="X=0 Y=0 Z=0")
coord_label.pack()

tk.Button(control_frame, text="Save move.dat As...", command=save_entities).pack()

root.config(menu=menubar)

load_entities()

# -----------------------------
# MATPLOTLIB FIGURE
# -----------------------------
fig, ax = plt.subplots()
cax = fig.add_axes([0.91, 0.1, 0.03, 0.8])

# Show plot in separate window
canvas = FigureCanvasTkAgg(fig, master=root)
canvas_widget = canvas.get_tk_widget()
canvas_widget.pack(fill=tk.BOTH, expand=True)
canvas.mpl_connect("button_press_event", on_press)
canvas.mpl_connect("motion_notify_event", on_motion)
canvas.mpl_connect("button_release_event", on_release)
canvas.mpl_connect("scroll_event", on_scroll)

toolbar = NavigationToolbar2Tk(canvas, root)
toolbar.update()
toolbar.pack()

# Run UI
root.protocol("WM_DELETE_WINDOW", on_close)
root.mainloop()
