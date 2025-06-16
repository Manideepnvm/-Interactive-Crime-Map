from flask import Flask, render_template, request, jsonify
from utils.map_generators import generate_map, generate_filtered_map
import pandas as pd
import json

app = Flask(__name__)

@app.route('/')
def home():
    crime_map = generate_map('data/crime_data.csv')
    return render_template('index.html', map_html=crime_map)

@app.route('/filter', methods=['POST'])
def filter_crimes():
    data = request.get_json()
    location_search = data.get('location', '')
    crime_type = data.get('crime_type', '')
    severity = data.get('severity', '')
    
    filtered_map = generate_filtered_map('data/crime_data.csv', location_search, crime_type, severity)
    return jsonify({'map_html': filtered_map})

@app.route('/api/locations')
def get_locations():
    try:
        df = pd.read_csv('data/crime_data.csv')
        locations = df['location_description'].unique().tolist()
        # Remove any NaN values and sort
        locations = [loc for loc in locations if pd.notna(loc)]
        locations.sort()
        return jsonify(locations)
    except Exception as e:
        return jsonify([]), 500

@app.route('/api/crime_types')
def get_crime_types():
    try:
        df = pd.read_csv('data/crime_data.csv')
        crime_types = df['crime_type'].unique().tolist()
        # Remove any NaN values and sort
        crime_types = [ct for ct in crime_types if pd.notna(ct)]
        crime_types.sort()
        return jsonify(crime_types)
    except Exception as e:
        return jsonify([]), 500

@app.route('/api/stats')
def get_stats():
    try:
        df = pd.read_csv('data/crime_data.csv')
        
        # Calculate stats
        total_crimes = len(df)
        
        # Assuming you have a severity column
        if 'severity' in df.columns:
            low_severity = len(df[df['severity'].str.lower() == 'low'])
            medium_severity = len(df[df['severity'].str.lower() == 'medium'])
            high_severity = len(df[df['severity'].str.lower() == 'high'])
        else:
            # If no severity column, distribute evenly for demo
            low_severity = int(total_crimes * 0.45)
            medium_severity = int(total_crimes * 0.35)
            high_severity = total_crimes - low_severity - medium_severity
        
        return jsonify({
            'total': total_crimes,
            'low': low_severity,
            'medium': medium_severity,
            'high': high_severity
        })
    except Exception as e:
        # Return default values if CSV reading fails
        return jsonify({
            'total': 100,
            'low': 45,
            'medium': 35,
            'high': 20
        })

@app.route('/api/location_details/<location>')
def get_location_details(location):
    """Get detailed information about a specific location for navigation"""
    try:
        df = pd.read_csv('data/crime_data.csv')
        location_data = df[df['location_description'] == location]
        
        if not location_data.empty:
            # Get coordinates if available
            lat = location_data.iloc[0].get('latitude', None)
            lng = location_data.iloc[0].get('longitude', None)
            
            return jsonify({
                'name': location,
                'latitude': lat,
                'longitude': lng,
                'address': f"{location}, Andhra Pradesh, India",
                'crime_count': len(location_data)
            })
        else:
            return jsonify({
                'name': location,
                'address': f"{location}, Andhra Pradesh, India"
            })
    except Exception as e:
        return jsonify({
            'name': location,
            'address': f"{location}, Andhra Pradesh, India"
        })

@app.route('/api/nearby_locations')
def get_nearby_locations():
    """Get locations near user's current position"""
    try:
        lat = float(request.args.get('lat', 0))
        lng = float(request.args.get('lng', 0))
        radius = float(request.args.get('radius', 10))  # km
        
        df = pd.read_csv('data/crime_data.csv')
        
        # If your CSV has latitude/longitude columns
        if 'latitude' in df.columns and 'longitude' in df.columns:
            # Calculate distance (simplified version)
            df['distance'] = ((df['latitude'] - lat) ** 2 + (df['longitude'] - lng) ** 2) ** 0.5
            nearby = df[df['distance'] <= radius * 0.01]  # Rough conversion
            
            locations = nearby['location_description'].unique().tolist()
            return jsonify(locations[:20])  # Limit to 20 results
        else:
            # If no coordinates, return all locations
            locations = df['location_description'].unique().tolist()
            return jsonify(locations[:20])
            
    except Exception as e:
        return jsonify([])

if __name__ == '__main__':
    app.run(debug=True)