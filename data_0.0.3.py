# GTFS Trip Planner Demo using Python

## Step 1: Prepare Environment
# Make sure you have installed necessary Python packages:
# pip install pandas networkx

import pandas as pd
import networkx as nx

# Load the GTFS data
stops = pd.read_csv('stops.txt')
routes = pd.read_csv('routes.txt')
trips = pd.read_csv('trips.txt')
stop_times = pd.read_csv('stop_times.txt')
shapes = pd.read_csv('shapes.txt')

# Display a preview of the stops data to ensure the files are being read correctly
print(stops.head())

## Step 2: Build Graph for Route Planning
# Build a directed graph using NetworkX to represent stops and routes
graph = nx.DiGraph()

# Add nodes for each stop, using stop_id as the unique identifier
for _, stop in stops.iterrows():
    graph.add_node(str(stop['stop_id']), name=stop['stop_name'])

# Add edges for connections between stops based on stop_times
previous_stop = None
previous_trip_id = None
for _, stop_time in stop_times.iterrows():
    current_trip_id = stop_time['trip_id']
    if previous_stop is not None and current_trip_id == previous_trip_id:
        graph.add_edge(str(previous_stop['stop_id']), str(stop_time['stop_id']), trip_id=current_trip_id, departure_time=previous_stop['departure_time'], arrival_time=stop_time['arrival_time'])
    previous_stop = stop_time
    previous_trip_id = current_trip_id

print(f"Graph has {len(graph.nodes)} nodes and {len(graph.edges)} edges")

## Step 3: Create Route Planner
# Define a function that finds the shortest path between two stops
def find_shortest_route(graph, start_stop_id, end_stop_id):
    try:
        path = nx.shortest_path(graph, source=str(start_stop_id), target=str(end_stop_id))
        return path
    except nx.NetworkXNoPath:
        return None
    except nx.NodeNotFound:
        return None

# Define a function to provide detailed route information
def get_route_details(route_path):
    details = []
    for i in range(len(route_path) - 1):
        start_stop = stops.loc[stops['stop_id'] == int(route_path[i])]
        end_stop = stops.loc[stops['stop_id'] == int(route_path[i + 1])]
        trip_id = graph.get_edge_data(route_path[i], route_path[i + 1])['trip_id']
        details.append(f"From {start_stop['stop_name'].values[0]} to {end_stop['stop_name'].values[0]} via Trip {trip_id}")
    return details

## Step 4: Run Demo
# Select two stops to find a route between
while True:
    start_stop_id = input("Enter Start Stop ID (or type 'exit' to quit): ")
    if start_stop_id.lower() == 'exit':
        break
    if start_stop_id not in stops['stop_id'].astype(str).values:
        print("Invalid Start Stop ID. Please enter a valid stop ID.")
        continue
    
    end_stop_id = input("Enter End Stop ID (or type 'exit' to quit): ")
    if end_stop_id.lower() == 'exit':
        break
    if end_stop_id not in stops['stop_id'].astype(str).values:
        print("Invalid End Stop ID. Please enter a valid stop ID.")
        continue

    route = find_shortest_route(graph, start_stop_id, end_stop_id)
    if route:
        print("\nSuggested Route:")
        route_details = get_route_details(route)
        for detail in route_details:
            print(detail)
    else:
        print("No route available between the selected stops.")
