import pandas as pd
import folium
from folium import plugins
import json

def generate_map(csv_file):
    """Generate the main interactive map"""
    try:
        df = pd.read_csv(csv_file)
        
        # Center the map on Andhra Pradesh
        center_lat = 15.9129
        center_lng = 79.7400
        
        # Create the map
        m = folium.Map(
            location=[center_lat, center_lng],
            zoom_start=7,
            tiles='OpenStreetMap'
        )
        
        # Add different tile layers
        folium.TileLayer('CartoDB positron').add_to(m)
        folium.TileLayer('CartoDB dark_matter').add_to(m)
        
        # Create marker clusters for better performance
        marker_cluster = plugins.MarkerCluster().add_to(m)
        
        # Define colors for different severity levels
        colors = {
            'low': 'green',
            'medium': 'orange', 
            'high': 'red'
        }
        
        # Add markers for each crime location
        for index, row in df.iterrows():
            # Get coordinates (adjust column names as per your CSV)
            lat = row.get('latitude', None)
            lng = row.get('longitude', None)
            
            # If no coordinates, skip or use geocoding service
            if pd.isna(lat) or pd.isna(lng):
                continue
                
            location_name = row.get('location_description', 'Unknown Location')
            crime_type = row.get('crime_type', 'Unknown Crime')
            severity = row.get('severity', 'medium').lower()
            date = row.get('date', 'Unknown Date')
            
            # Create popup content with navigation button
            popup_content = f"""
            <div style="width: 250px;">
                <h5>{location_name}</h5>
                <p><strong>Crime Type:</strong> {crime_type}</p>
                <p><strong>Severity:</strong> {severity.title()}</p>
                <p><strong>Date:</strong> {date}</p>
                <button onclick="parent.onMarkerClick('{location_name}', '{location_name}, Andhra Pradesh, India')" 
                        class="btn btn-sm btn-primary">
                    📍 Select for Navigation
                </button>
            </div>
            """
            
            # Add marker to cluster
            folium.Marker(
                [lat, lng],
                popup=folium.Popup(popup_content, max_width=300),
                tooltip=f"{location_name} - {crime_type}",
                icon=folium.Icon(
                    color=colors.get(severity, 'blue'),
                    icon='exclamation-triangle',
                    prefix='fa'
                )
            ).add_to(marker_cluster)
        
        # Add heat map layer
        if 'latitude' in df.columns and 'longitude' in df.columns:
            heat_data = [[row['latitude'], row['longitude']] for idx, row in df.iterrows() 
                        if pd.notna(row['latitude']) and pd.notna(row['longitude'])]
            
            if heat_data:
                plugins.HeatMap(heat_data, name='Crime Heat Map').add_to(m)
        
        # Add layer control
        folium.LayerControl().add_to(m)
        
        # Add fullscreen button
        plugins.Fullscreen().add_to(m)
        
        # Add measure control
        plugins.MeasureControl().add_to(m)
        
        return m._repr_html_()
        
    except Exception as e:
        print(f"Error generating map: {e}")
        return f"<div class='alert alert-danger'>Error loading map: {str(e)}</div>"

def generate_filtered_map(csv_file, location_filter='', crime_type_filter='', severity_filter=''):
    """Generate filtered map based on user inputs"""
    try:
        df = pd.read_csv(csv_file)
        
        # Apply filters
        if location_filter and location_filter.lower() != 'all':
            df = df[df['location_description'].str.contains(location_filter, case=False, na=False)]
        
        if crime_type_filter and crime_type_filter != 'All':
            df = df[df['crime_type'] == crime_type_filter]
            
        if severity_filter and severity_filter != 'All':
            df = df[df['severity'].str.lower() == severity_filter.lower()]
        
        # If filtered data is empty, return message
        if df.empty:
            return "<div class='alert alert-warning'>No crimes found matching the selected filters.</div>"
        
        # Center map on first result or default location
        if not df.empty and 'latitude' in df.columns and 'longitude' in df.columns:
            center_lat = df['latitude'].mean()
            center_lng = df['longitude'].mean()
        else:
            center_lat = 15.9129
            center_lng = 79.7400
        
        # Create the map
        m = folium.Map(
            location=[center_lat, center_lng],
            zoom_start=9,
            tiles='OpenStreetMap'
        )
        
        # Add different tile layers
        folium.TileLayer('CartoDB positron').add_to(m)
        folium.TileLayer('CartoDB dark_matter').add_to(m)
        
        # Create marker clusters
        marker_cluster = plugins.MarkerCluster().add_to(m)
        
        # Define colors for different severity levels
        colors = {
            'low': 'green',
            'medium': 'orange',
            'high': 'red'
        }
        
        # Add markers for filtered results
        for index, row in df.iterrows():
            lat = row.get('latitude', None)
            lng = row.get('longitude', None)
            
            if pd.isna(lat) or pd.isna(lng):
                continue
                
            location_name = row.get('location_description', 'Unknown Location')
            crime_type = row.get('crime_type', 'Unknown Crime')
            severity = row.get('severity', 'medium').lower()
            date = row.get('date', 'Unknown Date')
            
            # Create popup content with navigation button
            popup_content = f"""
            <div style="width: 250px;">
                <h5>{location_name}</h5>
                <p><strong>Crime Type:</strong> {crime_type}</p>
                <p><strong>Severity:</strong> {severity.title()}</p>
                <p><strong>Date:</strong> {date}</p>
                <button onclick="parent.onMarkerClick('{location_name}', '{location_name}, Andhra Pradesh, India')" 
                        class="btn btn-sm btn-primary">
                    📍 Select for Navigation
                </button>
            </div>
            """
            
            folium.Marker(
                [lat, lng],
                popup=folium.Popup(popup_content, max_width=300),
                tooltip=f"{location_name} - {crime_type}",
                icon=folium.Icon(
                    color=colors.get(severity, 'blue'),
                    icon='exclamation-triangle',
                    prefix='fa'
                )
            ).add_to(marker_cluster)
        
        # Add heat map for filtered data
        if len(df) > 0 and 'latitude' in df.columns and 'longitude' in df.columns:
            heat_data = [[row['latitude'], row['longitude']] for idx, row in df.iterrows() 
                        if pd.notna(row['latitude']) and pd.notna(row['longitude'])]
            
            if heat_data:
                plugins.HeatMap(heat_data, name='Filtered Crime Heat Map').add_to(m)
        
        # Add layer control
        folium.LayerControl().add_to(m)
        
        # Add fullscreen button
        plugins.Fullscreen().add_to(m)
        
        return m._repr_html_()
        
    except Exception as e:
        print(f"Error generating filtered map: {e}")
        return f"<div class='alert alert-danger'>Error loading filtered map: {str(e)}</div>"

def get_unique_values(csv_file):
    """Get unique values for filter dropdowns"""
    try:
        df = pd.read_csv(csv_file)
        
        locations = sorted(df['location_description'].dropna().unique().tolist())
        crime_types = sorted(df['crime_type'].dropna().unique().tolist())
        severities = sorted(df['severity'].dropna().unique().tolist())
        
        return {
            'locations': locations,
            'crime_types': crime_types,
            'severities': severities
        }
    except Exception as e:
        print(f"Error getting unique values: {e}")
        return {
            'locations': [],
            'crime_types': [],
            'severities': []
        }

def generate_statistics(csv_file):
    """Generate crime statistics"""
    try:
        df = pd.read_csv(csv_file)
        
        # Basic statistics
        total_crimes = len(df)
        
        # Crime type distribution
        crime_by_type = df['crime_type'].value_counts().to_dict()
        
        # Severity distribution
        severity_counts = df['severity'].value_counts().to_dict()
        
        # Location with most crimes
        location_counts = df['location_description'].value_counts()
        top_location = location_counts.index[0] if not location_counts.empty else "N/A"
        top_location_count = location_counts.iloc[0] if not location_counts.empty else 0
        
        # Recent crimes (assuming date column exists)
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'], errors='coerce')
            recent_crimes = df.sort_values('date', ascending=False).head(5)
            recent_crimes_list = recent_crimes[['location_description', 'crime_type', 'severity', 'date']].to_dict('records')
        else:
            recent_crimes_list = []
        
        return {
            'total_crimes': total_crimes,
            'crime_by_type': crime_by_type,
            'severity_counts': severity_counts,
            'top_location': top_location,
            'top_location_count': top_location_count,
            'recent_crimes': recent_crimes_list
        }
        
    except Exception as e:
        print(f"Error generating statistics: {e}")
        return {
            'total_crimes': 0,
            'crime_by_type': {},
            'severity_counts': {},
            'top_location': "N/A",
            'top_location_count': 0,
            'recent_crimes': []
        }

def generate_route_map(start_location, end_location):
    """Generate a route map between two locations"""
    try:
        # Create base map centered between locations
        m = folium.Map(
            location=[15.9129, 79.7400],  # Default to AP center
            zoom_start=10,
            tiles='OpenStreetMap'
        )
        
        # Add start marker
        folium.Marker(
            [15.9129, 79.7400],  # You would need to geocode the actual coordinates
            popup=f"Start: {start_location}",
            tooltip="Starting Point",
            icon=folium.Icon(color='green', icon='play', prefix='fa')
        ).add_to(m)
        
        # Add end marker
        folium.Marker(
            [15.9129, 79.7400],  # You would need to geocode the actual coordinates
            popup=f"Destination: {end_location}",
            tooltip="Destination",
            icon=folium.Icon(color='red', icon='stop', prefix='fa')
        ).add_to(m)
        
        # Note: For actual routing, you would need to integrate with a routing service
        # like OpenRouteService, GraphHopper, or Google Directions API
        
        return m._repr_html_()
        
    except Exception as e:
        print(f"Error generating route map: {e}")
        return f"<div class='alert alert-danger'>Error generating route: {str(e)}</div>"

def export_filtered_data(csv_file, location_filter='', crime_type_filter='', severity_filter=''):
    """Export filtered crime data to CSV"""
    try:
        df = pd.read_csv(csv_file)
        
        # Apply filters
        if location_filter and location_filter.lower() != 'all':
            df = df[df['location_description'].str.contains(location_filter, case=False, na=False)]
        
        if crime_type_filter and crime_type_filter != 'All':
            df = df[df['crime_type'] == crime_type_filter]
            
        if severity_filter and severity_filter != 'All':
            df = df[df['severity'].str.lower() == severity_filter.lower()]
        
        # Export to CSV
        output_filename = f"filtered_crimes_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv"
        df.to_csv(output_filename, index=False)
        
        return {
            'success': True,
            'filename': output_filename,
            'count': len(df)
        }
        
    except Exception as e:
        print(f"Error exporting data: {e}")
        return {
            'success': False,
            'error': str(e),
            'count': 0
        }

def search_crimes_near_location(csv_file, location, radius_km=5):
    """Search for crimes near a specific location within a given radius"""
    try:
        df = pd.read_csv(csv_file)
        
        # For demonstration, using simple text matching
        # In production, you would use geospatial queries with proper coordinates
        nearby_crimes = df[df['location_description'].str.contains(location, case=False, na=False)]
        
        if nearby_crimes.empty:
            return {
                'success': False,
                'message': f"No crimes found near {location}",
                'crimes': []
            }
        
        crimes_list = nearby_crimes[['location_description', 'crime_type', 'severity', 'date']].to_dict('records')
        
        return {
            'success': True,
            'message': f"Found {len(crimes_list)} crimes near {location}",
            'crimes': crimes_list
        }
        
    except Exception as e:
        print(f"Error searching crimes near location: {e}")
        return {
            'success': False,
            'message': f"Error searching: {str(e)}",
            'crimes': []
        }

def generate_crime_trend_data(csv_file):
    """Generate data for crime trend analysis"""
    try:
        df = pd.read_csv(csv_file)
        
        if 'date' not in df.columns:
            return {'error': 'Date column not found in data'}
        
        # Convert date column
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        df = df.dropna(subset=['date'])
        
        # Group by month and crime type
        df['month_year'] = df['date'].dt.to_period('M')
        trend_data = df.groupby(['month_year', 'crime_type']).size().unstack(fill_value=0)
        
        # Convert to format suitable for visualization
        trend_dict = {}
        for crime_type in trend_data.columns:
            trend_dict[crime_type] = [
                {'month': str(month), 'count': count} 
                for month, count in trend_data[crime_type].items()
            ]
        
        return {
            'success': True,
            'trend_data': trend_dict,
            'total_months': len(trend_data.index)
        }
        
    except Exception as e:
        print(f"Error generating trend data: {e}")
        return {'error': str(e)}
    
    
    
def generate_route_map(start_location, end_location, user_lat=None, user_lng=None):
    """Generate a route map from user's current location to destination"""
    try:
        # Use user's current location if provided, otherwise use default
        if user_lat and user_lng:
            start_coords = [user_lat, user_lng]
            start_label = "Your Location"
        else:
            # Fallback to default location if user location not available
            start_coords = [15.9129, 79.7400]
            start_label = start_location
        
        # Create base map centered on start location
        m = folium.Map(
            location=start_coords,
            zoom_start=10,
            tiles='OpenStreetMap'
        )
        
        # Add current location marker
        folium.Marker(
            start_coords,
            popup=f"Start: {start_label}",
            tooltip="Starting Point (Your Location)",
            icon=folium.Icon(color='green', icon='play', prefix='fa')
        ).add_to(m)
        
        # Add destination marker (you'll need to geocode the end_location)
        # For now using default coords - replace with actual geocoded coordinates
        folium.Marker(
            [15.9129, 79.7400],  # Replace with geocoded coordinates of end_location
            popup=f"Destination: {end_location}",
            tooltip="Destination",
            icon=folium.Icon(color='red', icon='stop', prefix='fa')
        ).add_to(m)
        
        return m._repr_html_()
        
    except Exception as e:
        print(f"Error generating route map: {e}")
        return f"<div class='alert alert-danger'>Error generating route: {str(e)}</div>"

# Main execution functions
if __name__ == "__main__":
    # Example usage
    csv_file = "crime_data.csv"  # Replace with your actual CSV file path
    
    # Generate main map
    main_map = generate_map(csv_file)
    print("Main map generated")
    
    # Get filter options
    filter_options = get_unique_values(csv_file)
    print("Filter options:", filter_options)
    
    # Generate statistics
    stats = generate_statistics(csv_file)
    print("Statistics:", stats)
    
    # Example filtered map
    filtered_map = generate_filtered_map(csv_file, location_filter="", crime_type_filter="Theft", severity_filter="high")
    print("Filtered map generated")
    
    # Search crimes near location
    nearby_crimes = search_crimes_near_location(csv_file, "Vijayawada", radius_km=10)
    print("Nearby crimes:", nearby_crimes)
    
    # Generate trend data
    trend_data = generate_crime_trend_data(csv_file)
    print("Trend data:", trend_data)
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    