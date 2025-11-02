# gui_app.py

import tkinter as tk
from tkinter import messagebox
import requests
import time
import folium
import webbrowser

# ----------------- Node coordinates (longitude, latitude) -----------------
NODES = {
    "Staff Quarter": [90.4266, 23.7805],
    "Banaseer": [90.4215, 23.7820],
    "Rampura": [90.4220, 23.7850],
    "Middle Badda": [90.4235, 23.7890],
    "North Badda": [90.4250, 23.7910],
    "Banani": [90.4195, 23.7960],
    "UIU": [90.4214, 23.7972],
    "Gulshan 1": [90.4145, 23.7807],
    "Gulshan 2": [90.4260, 23.7915],
    "Notun Bazar": [90.4298, 23.8010],
    "Bashundhara": [90.4319, 23.8153]
}

# ----------------- Neighbor connections -----------------
NEIGHBORS = {
    "Staff Quarter": ["Banaseer", "Gulshan 1"],
    "Banaseer": ["Staff Quarter", "Rampura", "Middle Badda"],
    "Rampura": ["Banaseer", "Middle Badda", "Banani"],
    "Middle Badda": ["Rampura", "Banaseer", "North Badda"],
    "North Badda": ["Middle Badda", "Gulshan 2", "Banani"],
    "Banani": ["Rampura", "UIU", "North Badda"],
    "UIU": ["Banani", "Notun Bazar"],
    "Gulshan 1": ["Staff Quarter", "Gulshan 2"],
    "Gulshan 2": ["Gulshan 1", "North Badda", "Bashundhara"],
    "Notun Bazar": ["UIU", "Bashundhara"],
    "Bashundhara": ["Gulshan 2", "Notun Bazar"]
}

# ----------------- OSRM server URL -----------------
OSRM_HOST = "http://localhost:5001"

# ----------------- Function to get OSRM distance for two nodes -----------------
def get_osrm_distance(a, b):
    lon1, lat1 = NODES[a]
    lon2, lat2 = NODES[b]
    url = f"{OSRM_HOST}/route/v1/driving/{lon1},{lat1};{lon2},{lat2}?overview=false"
    try:
        r = requests.get(url, timeout=5).json()
        if r["code"] == "Ok":
            return r["routes"][0]["distance"]
        return float("inf")
    except Exception as e:
        print(f"OSRM request failed for {a} -> {b}: {e}")
        return float("inf")

# ----------------- Build EDGES -----------------
EDGES = {}
for node, neighbors in NEIGHBORS.items():
    EDGES[node] = {}
    for neighbor in neighbors:
        EDGES[node][neighbor] = get_osrm_distance(node, neighbor)
        time.sleep(0.05)

# ----------------- Find all simple paths -----------------
def all_paths(start, goal, path=[]):
    path = path + [start]
    if start == goal:
        return [path]
    paths = []
    for neighbor in EDGES.get(start, {}):
        if neighbor not in path:
            newpaths = all_paths(neighbor, goal, path)
            for p in newpaths:
                paths.append(p)
    return paths

def path_distance(path):
    distance = 0
    for i in range(len(path)-1):
        distance += EDGES[path[i]][path[i+1]]
    return distance

# ----------------- Get OSRM route coordinates for a segment -----------------
def get_osrm_route_coords(start, goal):
    lon1, lat1 = NODES[start]
    lon2, lat2 = NODES[goal]
    url = f"{OSRM_HOST}/route/v1/driving/{lon1},{lat1};{lon2},{lat2}?overview=full&geometries=geojson"# path take details a dekhte pari and osrm route coor ke geo formate a dibe
    try:
        r = requests.get(url, timeout=5).json()
        if r["code"] == "Ok":
            route = r["routes"][0]["geometry"]["coordinates"]
            return [(lat, lon) for lon, lat in route]
    except Exception as e:
        print(f"OSRM route error {start} -> {goal}: {e}")
    return [(NODES[start][1], NODES[start][0]), (NODES[goal][1], NODES[goal][0])]

# ----------------- Draw all paths -----------------
def draw_all_paths(paths, optimal_path):
    fmap = folium.Map(location=[NODES[optimal_path[0]][1], NODES[optimal_path[0]][0]], zoom_start=14)#  crteate a interactive map

    # Draw all paths in gray
    for path in paths:
        if path == optimal_path:
            continue
        for i in range(len(path)-1):
            segment = get_osrm_route_coords(path[i], path[i+1])
            folium.PolyLine(segment, color="lightgray", weight=3, opacity=0.5).add_to(fmap)

    # Draw optimal path in blue
    for i in range(len(optimal_path)-1):
        segment = get_osrm_route_coords(optimal_path[i], optimal_path[i+1])
        folium.PolyLine(segment, color="blue", weight=5, opacity=0.8).add_to(fmap)

    # Add markers
    for node in optimal_path:
        folium.Marker(location=[NODES[node][1], NODES[node][0]], popup=node).add_to(fmap)

    # Save and open
    fmap.save("path_map.html")
    webbrowser.open("path_map.html")

# ----------------- Run pathfinding ----------------- “Find Path” button
def run_astar():
    start = start_var.get() # get user input 
    goal = goal_var.get()
    #If the user didn’t select both places, it shows a warning message.
    if not start or not goal:
        messagebox.showwarning("Input Error", "Select both start and goal.")
        return
    if start == goal:
        messagebox.showinfo("Same Node", "Start and goal cannot be same.")
        return

    paths = all_paths(start, goal) #→ Calls the function all_paths() (from astar.py) to find all possible routes between the two points.
    if not paths:
        output_label.config(text="⚠️ No path found.")  #If there’s no connection between start and goal, it shows a warning in the output label.
        return

    optimal_path = min(paths, key=path_distance)#→ Among all found paths, it picks the one with the smallest total distance using path_distance().
    draw_all_paths(paths, optimal_path)#Sends the paths to a map-drawing function to show routes visually (with Folium).

    msg = f"✅ Optimal Path: {' → '.join(optimal_path)}\nTotal distance: {path_distance(optimal_path):.1f} m"
    output_label.config(text=msg) #Displays the best path and its total distance in meters on the GUI screen.

# ----------------- GUI -----------------
root = tk.Tk()# Creates the main application window.
root.title("Campus Navigation")
root.geometry("400x300")

tk.Label(root, text="Select Start:").pack()
start_var = tk.StringVar()
tk.OptionMenu(root, start_var, *NODES.keys()).pack()

tk.Label(root, text="Select Goal:").pack()
goal_var = tk.StringVar() # value thke hold kore 
tk.OptionMenu(root, goal_var, *NODES.keys()).pack()

tk.Button(root, text="Find Optimal Path", command=run_astar).pack(pady=10)
output_label = tk.Label(root, text="", justify="left", wraplength=380)
output_label.pack()

root.mainloop()
