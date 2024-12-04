# GTFS Trip Planner Demo with Web Interface using Streamlit

## Step 1: Prepare Environment
# Make sure you have installed necessary Python packages:
# pip install pandas networkx streamlit openai

import pandas as pd
import networkx as nx
import streamlit as st
import openai

stops = pd.read_csv('stops.txt')
routes = pd.read_csv('routes.txt')
trips = pd.read_csv('trips.txt')
stop_times = pd.read_csv('stop_times.txt')
shapes = pd.read_csv('shapes.txt')

# Build Graph for Route Planning
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

# Define function to find the shortest path between two stops
def find_shortest_route(graph, start_stop_id, end_stop_id):
    try:
        path = nx.shortest_path(graph, source=str(start_stop_id), target=str(end_stop_id))
        return path
    except nx.NetworkXNoPath:
        return None
    except nx.NodeNotFound:
        return None

# Define function to provide detailed route information
def get_route_details(route_path):
    details = []
    for i in range(len(route_path) - 1):
        start_stop = stops.loc[stops['stop_id'] == int(route_path[i])]
        end_stop = stops.loc[stops['stop_id'] == int(route_path[i + 1])]
        trip_id = graph.get_edge_data(route_path[i], route_path[i + 1])['trip_id']
        details.append(f"From {start_stop['stop_name'].values[0]} to {end_stop['stop_name'].values[0]} via Trip {trip_id}")
    return details

# Streamlit UI
st.title("GTFS Trip Planner Demo")

# Preferences Buttons
st.sidebar.header("Travel Preferences")
preferences = []
if st.sidebar.button("Shortest Route"):
    preferences.append("shortest_route")
if st.sidebar.button("Least Transfers"):
    preferences.append("least_transfers")
if st.sidebar.button("Scenic Route"):
    preferences.append("scenic_route")

# User Inputs
start_stop_id = st.text_input("Enter Start Stop ID:")
end_stop_id = st.text_input("Enter End Stop ID:")

# Voice/Text Input for ChatGPT
user_message = st.text_area("Enter your question or additional preferences:")
if st.button("Submit Request"):
    # Route Planning
    if start_stop_id and end_stop_id:
        if start_stop_id not in stops['stop_id'].astype(str).values:
            st.error("Invalid Start Stop ID. Please enter a valid stop ID.")
        elif end_stop_id not in stops['stop_id'].astype(str).values:
            st.error("Invalid End Stop ID. Please enter a valid stop ID.")
        else:
            route = find_shortest_route(graph, start_stop_id, end_stop_id)
            if route:
                route_details = get_route_details(route)
                st.subheader("Suggested Route:")
                for detail in route_details:
                    st.write(detail)
            else:
                st.error("No route available between the selected stops.")

    # Prepare input for OpenAI API
    openai_message = f"User preferences: {preferences}. User message: {user_message}. Start Stop ID: {start_stop_id}, End Stop ID: {end_stop_id}."
    # Placeholder for OpenAI API response (since we do not have the API key yet)
    st.subheader("ChatGPT Response:")
    st.write("[Response from ChatGPT would be displayed here]")

# Instructions for running the Streamlit app
st.markdown("""
### Instructions
- Save this script as `trip_planner_app.py`.
- Run the app using the command: `streamlit run trip_planner_app.py`
- Use the sidebar to select preferences, input stop IDs, and add extra information for ChatGPT.
""")
