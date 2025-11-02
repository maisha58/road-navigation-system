import json
import math
import requests
import time

# ---------------- Nodes ----------------
# Node coordinates (Dhaka campus example)
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

# ---------------- Base URL of OSRM ----------------
BASE_URL = "http://localhost:5001"  # your running OSRM server

# ---------------- Neighbor Connections ----------------
# Define which nodes are directly connected (edges)
NEIGHBORS = {
    "Staff Quarter": ["Banaseer", "Rampura"],
    "Banaseer": ["Staff Quarter", "Rampura", "Middle Badda"],
    "Rampura": ["Staff Quarter", "Banaseer", "Middle Badda"],
    "Middle Badda": ["Banaseer", "Rampura", "North Badda", "Banani"],
    "North Badda": ["Middle Badda", "Banani"],
    "Banani": ["Middle Badda", "North Badda", "UIU"],
    "UIU": ["Banani"],
    "Gulshan 1": ["Gulshan 2", "Staff Quarter"],
    "Gulshan 2": ["Gulshan 1", "North Badda"],
    "Notun Bazar": ["Bashundhara", "North Badda"],
    "Bashundhara": ["Notun Bazar"]
}

# ---------------- Function to get distance from OSRM ----------------
def get_osrm_distance(a, b):
    lon1, lat1 = NODES[a]
    lon2, lat2 = NODES[b]
    url = f"{BASE_URL}/route/v1/driving/{lon1},{lat1};{lon2},{lat2}?overview=false"
    try:
        r = requests.get(url, timeout=5).json()
        if r["code"] == "Ok":
            return r["routes"][0]["distance"]  # meters
        else:
            return float("inf")
    except Exception as e:
        print(f"OSRM request failed for {a} -> {b}: {e}")
        return float("inf")

# ---------------- Build EDGES with real distances ---------------- akta node theke kothay kothay jao jay and resl distance means graph cfeate hoitese 
EDGES = {}
for node, neighbors in NEIGHBORS.items():
    EDGES[node] = {}
    for neighbor in neighbors:
        distance = get_osrm_distance(node, neighbor)
        EDGES[node][neighbor] = distance
        time.sleep(0.1)  # slight delay to avoid overwhelming OSRM

# ---------------- Heuristic function (straight-line distance) ----------------
def heuristic(a, b):
    lon1, lat1 = NODES[a]
    lon2, lat2 = NODES[b]
    # Approx straight-line distance in meters (Euclidean)
    return math.sqrt((lon1 - lon2)**2 + (lat1 - lat2)**2) * 111000
