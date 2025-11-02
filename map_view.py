import folium
import requests
import json
from graph_data import NODES

# Load OSRM config
with open("osrm_config.json") as f:
    OSRM = json.load(f)
BASE_URL = OSRM["base_url"]  # storing  url

def get_osrm_route_coords(start, goal):
    """Fetch real road geometry from OSRM."""
    lon1, lat1 = NODES[start]
    lon2, lat2 = NODES[goal]
    url = f"{BASE_URL}/route/v1/driving/{lon1},{lat1};{lon2},{lat2}?overview=full&geometries=geojson" # path ke detail a dekhar jonno  route ke geojson formate a deyar jonno
    try:
        r = requests.get(url)
        data = r.json()
        if data["code"] == "Ok":
            route = data["routes"][0]["geometry"]["coordinates"]
            distance = data["routes"][0]["distance"]
            duration = data["routes"][0]["duration"]
            route_latlon = [(coord[1], coord[0]) for coord in route]
            return route_latlon, distance, duration
    except Exception as e:
        print("OSRM route error:", e)
    return None, None, None

def show_route_on_map(path, use_osrm=True):
    """Display Folium map and return HTML file path."""
    if not path:
        print("No path to show.")
        return None

    start, goal = path[0], path[-1]
    start_coords = (NODES[start][1], NODES[start][0])# log and lat order 
    goal_coords = (NODES[goal][1], NODES[goal][0])
    m = folium.Map(location=start_coords, zoom_start=14)

    folium.Marker(start_coords, popup=f"Start: {start}", icon=folium.Icon(color='green')).add_to(m)
    folium.Marker(goal_coords, popup=f"Goal: {goal}", icon=folium.Icon(color='red')).add_to(m)

    if use_osrm:
        route_coords, distance, duration = get_osrm_route_coords(start, goal)
        if route_coords:
            folium.PolyLine(route_coords, color="blue", weight=6, opacity=0.8, tooltip="OSRM Route").add_to(m)
            folium.Popup(f"Distance: {distance/1000:.2f} km | Duration: {duration/60:.1f} min").add_to(m) #This line creates a clickable popup on the map showing the distance and time for the route.
        else:
            route_coords = [(NODES[node][1], NODES[node][0]) for node in path]
            folium.PolyLine(route_coords, color="orange", weight=4, tooltip="A* Path").add_to(m) #If OSRM fails or is not used, this draws the A* path as an orange line connecting all nodes
    else:
        route_coords = [(NODES[node][1], NODES[node][0]) for node in path]
        folium.PolyLine(route_coords, color="orange", weight=4, tooltip="A* Path").add_to(m)
#This draws each node as a circle, saves the map as HTML, and gives you the file to view in a browser.
    for node in path:
        folium.CircleMarker(
            location=(NODES[node][1], NODES[node][0]),
            radius=5,
            color="purple",
            fill=True,
            fill_opacity=0.7,
            popup=node
        ).add_to(m)

    map_file = "route_map.html"
    m.save(map_file)
    print(f"✅ Map saved as {map_file}")
    return map_file
