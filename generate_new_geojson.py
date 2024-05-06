import json

def offset_coordinates(geometry, offset_lon, offset_lat):
    if geometry['type'] == 'Point':
        lon, lat = geometry['coordinates']
        geometry['coordinates'] = [lon + offset_lon, lat - offset_lat]
    elif geometry['type'] == 'LineString' or geometry['type'] == 'MultiPoint':
        for i, coords in enumerate(geometry['coordinates']):
            lon, lat = coords
            geometry['coordinates'][i] = [lon + offset_lon, lat - offset_lat]
    elif geometry['type'] == 'Polygon' or geometry['type'] == 'MultiLineString':
        for i, part in enumerate(geometry['coordinates']):
            for j, coords in enumerate(part):
                lon, lat = coords
                geometry['coordinates'][i][j] = [lon + offset_lon, lat - offset_lat]
    elif geometry['type'] == 'MultiPolygon':
        for i, polygon in enumerate(geometry['coordinates']):
            for j, part in enumerate(polygon):
                for k, coords in enumerate(part):
                    lon, lat = coords
                    geometry['coordinates'][i][j][k] = [lon + offset_lon, lat - offset_lat]
    return geometry

def offset_geojson(input_file, output_file, offset_lon, offset_lat):
    with open(input_file, 'r') as f:
        data = json.load(f)

    if 'features' in data:
        for feature in data['features']:
            feature['geometry'] = offset_coordinates(feature['geometry'], offset_lon, offset_lat)
    elif 'geometry' in data:
        data['geometry'] = offset_coordinates(data['geometry'], offset_lon, offset_lat)

    with open(output_file, 'w') as f:
        json.dump(data, f)

# Example usage:
input_file = 'data/Geojsons/singapore-boundary.geojson'  #Source
output_file = 'data/Geojsons/output.geojson' #Destination
offset_lon = 120
offset_lat = -5
offset_geojson(input_file, output_file, offset_lon, offset_lat)
