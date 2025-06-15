from flask import Flask, render_template, request, jsonify
from utils.map_generators import generate_map, generate_filtered_map
import pandas as pd

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
    df = pd.read_csv('data/crime_data.csv')
    locations = df['location_description'].unique().tolist()
    return jsonify(locations)

@app.route('/api/crime_types')
def get_crime_types():
    df = pd.read_csv('data/crime_data.csv')
    crime_types = df['crime_type'].unique().tolist()
    return jsonify(crime_types)

if __name__ == '__main__':
    app.run(debug=True)