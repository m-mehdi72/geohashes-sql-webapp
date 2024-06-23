import csv
from django.http import HttpResponse
import json

def generate_coordinates_csv_response(coordinates):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="coordinates.csv"'
    
    writer = csv.writer(response)
    
    writer.writerow(['Location Name', 'Latitude', 'Longitude'])
    for location_name, lat, lon in coordinates:
        writer.writerow([location_name, lat, lon])

    return response

def extract_coordinates(geojson_file):
    with open(geojson_file, 'r') as f:
        data = json.load(f)
        
    coordinates = []
    messages = []
    for feature in data['features']:
        location_name = feature['properties'].get('name')
        if location_name is None:
            location_name = ''
        else:
            location_name = location_name.rstrip('\n')
        
        geometry_type = feature['geometry']['type']
        if geometry_type == 'MultiPolygon':
            coords = feature['geometry']['coordinates']
            for polygon in coords:
                for sub_polygon in polygon:
                    for point in sub_polygon:
                        coordinates.append((location_name, point[1], point[0]))
        else:
            messages.append(f"Unsupported geometry type: {geometry_type}")
    
    return coordinates, messages
