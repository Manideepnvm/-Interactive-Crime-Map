import pandas as pd
import folium
from folium.plugins import MarkerCluster, HeatMap
import json

def generate_map(csv_path):
    df = pd.read_csv(csv_path)
    
    # Center map on Andhra Pradesh
    center_lat = df['latitude'].mean()
    center_lon = df['longitude'].mean()
    
    fmap = folium.Map(
        location=[center_lat, center_lon], 
        zoom_start=8,
        tiles='OpenStreetMap'
    )
    
    # Add marker clustering
    marker_cluster = MarkerCluster().add_to(fmap)
    
    # Color mapping for severity
    color_map = {
        'Low': 'green',
        'Medium': 'orange', 
        'High': 'red'
    }
    
    for _, row in df.iterrows():
        color = color_map.get(row['severity'], 'blue')
        
        popup_info = f"""
        <div style="width: 200px;">
            <h5><b>{row['crime_type']}</b></h5>
            <p><b>Date:</b> {row['date']}</p>
            <p><b>Severity:</b> {row['severity']}</p>
            <p><b>Location:</b> {row['location_description']}</p>
            <p><b>ID:</b> {row['id']}</p>
        </div>
        """
        
        folium.Marker(
            location=[row['latitude'], row['longitude']],
            popup=folium.Popup(popup_info, max_width=250),
            tooltip=f"{row['crime_type']} - {row['location_description']}",
            icon=folium.Icon(color=color, icon='exclamation-sign')
        ).add_to(marker_cluster)
    
    # Add heatmap layer
    heat_data = [[row['latitude'], row['longitude']] for idx, row in df.iterrows()]
    HeatMap(heat_data, name='Crime Density').add_to(fmap)
    
    # Add layer control
    folium.LayerControl().add_to(fmap)
    
    return fmap._repr_html_()

def generate_filtered_map(csv_path, location_search='', crime_type='', severity=''):
    df = pd.read_csv(csv_path)
    
    # Apply filters
    if location_search:
        df = df[df['location_description'].str.contains(location_search, case=False, na=False)]
    
    if crime_type and crime_type != 'All':
        df = df[df['crime_type'] == crime_type]
    
    if severity and severity != 'All':
        df = df[df['severity'] == severity]
    
    if df.empty:
        # Return empty map if no results
        fmap = folium.Map(location=[15.9129, 79.7400], zoom_start=8)
        folium.Marker(
            location=[15.9129, 79.7400],
            popup="No crimes found with the selected filters",
            icon=folium.Icon(color='gray')
        ).add_to(fmap)
        return fmap._repr_html_()
    
    # Center map on filtered results
    center_lat = df['latitude'].mean()
    center_lon = df['longitude'].mean()
    
    fmap = folium.Map(
        location=[center_lat, center_lon], 
        zoom_start=10,
        tiles='OpenStreetMap'
    )
    
    # Color mapping for severity
    color_map = {
        'Low': 'green',
        'Medium': 'orange', 
        'High': 'red'
    }
    
    for _, row in df.iterrows():
        color = color_map.get(row['severity'], 'blue')
        
        popup_info = f"""
        <div style="width: 200px;">
            <h5><b>{row['crime_type']}</b></h5>
            <p><b>Date:</b> {row['date']}</p>
            <p><b>Severity:</b> {row['severity']}</p>
            <p><b>Location:</b> {row['location_description']}</p>
            <p><b>ID:</b> {row['id']}</p>
        </div>
        """
        
        folium.Marker(
            location=[row['latitude'], row['longitude']],
            popup=folium.Popup(popup_info, max_width=250),
            tooltip=f"{row['crime_type']} - {row['location_description']}",
            icon=folium.Icon(color=color, icon='exclamation-sign')
        ).add_to(fmap)
    
    return fmap._repr_html_()