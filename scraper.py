import os
import requests
import json
import re
import sys
from shapely.geometry import shape, mapping

### Configuration

output_filepath = "./Canyon County parcels.geojson"  # Filepath to save the merged GeoJSON
min_features = int(sys.argv[1]) # Try to grab at least this many features, if enough are available

### Mappings

CITY_MAPPINGS = {
    'CA': 'Caldwell',
    'MI': 'Middleton',
    'NA': 'Nampa',
    'PA': 'Payette',
    'NO': 'Notus',
    'WI': 'Wilder',
    'ST': 'Star',
    'GR': 'Greenleaf',
    'KU': 'Kuna',
    'ME': 'Melba'
}

SUFFIX_MAPPINGS = {
    "BLVD": "Boulevard",
    "ST": "Street",
    "DR": "Drive",
    "PL": "Place",
    "LN": "Lane",
    "CT": "Court",
    "AVE": "Avenue",
    "CIR": "Circle",
    "RD": "Road",
    "WAY": "Way",
    "PKWY": "Parkway",
    "TRL": "Trail",
    "LOOP": "Loop",
    "HWY": "Highway",
    "PT": "Point"
}

DIRECTIONAL_MAPPINGS = {
    'N': 'North',
    'S': 'South',
    'E': 'East',
    'W': 'West',
    'NE': 'Northeast',
    'NW': 'Northwest',
    'SE': 'Southeast',
    'SW': 'Southwest'
}

def fetch_page(result_offset):
    """
    Sends a GET request for parcels in GeoJSON format. Requests fields SiteAddress and SiteCity, comprising all address information available for the parcels.
    """
    url = f"https://maps.canyonco.org/arcgisserver/rest/services/Assessor/CCPublicTaxparcels/MapServer/0/query"
    params = {
        "f": "geojson",
        "where": "1=1",
        "returnGeometry": "true",
        "outFields": "SiteAddress,SiteCity",
        "outSR": 3857, # WGS 84
        "resultOffset": f"{result_offset}"
    }

    response = requests.get(url,params=params)
    
    if response.status_code == 200:
        data = response.json()
        
        if len(data["features"]) == 0: # End point returns an empty list if no more features are available
            print(f"No features found with offset {result_offset}")
        print(f"Scraped {len(data['features'])}")
        return data["features"]

    else:
        print(f"Failed to retrieve data for resultOffset {result_offset}, status code: {response.status_code}")
        return []  # Return empty list if the request fails

### Program logic

all_features = []
result_offset = 0

# Fetch pages until we receive an empty page or have fetched the desired number of features.
while (features := fetch_page(result_offset)) and result_offset < min_features and len(features) != 0:
    result_offset += len(features)
    # Process the features and apply the necessary parsing
    for feature in features:
        properties = feature["properties"]
    
        if CITY_MAPPINGS.get(properties["SiteCity"]):
            properties["addr:city"] = CITY_MAPPINGS[properties["SiteCity"]]
            del properties["SiteCity"]
        
        # Parse SiteAddress into house number and street name
        address = properties["SiteAddress"]
        if address is None:
            continue
        properties["addr:housenumber"], properties["addr:street"] = (None, None) if len(parts:=(address.split(' ', 1))) < 2 else (parts[0], parts[1]) #None if invalid
        del properties["SiteAddress"] # Not used in the output
        
        # Only keep features with a valid housenumber
        if properties["addr:housenumber"] == "0" or properties["addr:housenumber"] is None:
            continue

        # Remove probable unit numbers/letters from street name and flag them. Trailing numbers, except on highways, and trailing single letters are probably units.
        if "addr:street" in properties and properties["addr:street"].find("HWY") == -1:
            match = re.search(r"\s([A-D]|\d+)$", properties["addr:street"])
            if match:
                properties["addr:unit"] = match.group(1)
                properties["addr:street"] = properties["addr:street"][:match.start()].strip()
        
        # Generate capture groups for suffixes and directionals
        directionals = '|'.join(re.escape(direction) for direction in DIRECTIONAL_MAPPINGS.keys())
        suffixes = '|'.join(re.escape(abbr) for abbr in SUFFIX_MAPPINGS.keys())

        # Expand suffixes followed by a postdirectional, e.g., "17th Ave S" -> "17th Avenue South"
        properties["addr:street"] = re.sub(rf' ({suffixes}) ({directionals})', lambda m: ' ' + SUFFIX_MAPPINGS[m.group(1)] + ' ' + DIRECTIONAL_MAPPINGS[m.group(2)], properties["addr:street"])

        # Expand predirectionals
        properties["addr:street"] = re.sub(rf'^({directionals}) ', lambda m: DIRECTIONAL_MAPPINGS[m.group(1)] + ' ', properties["addr:street"])

        # Expand postdirectionals
        properties["addr:street"] = re.sub(rf' ({directionals})$', lambda m: ' ' + DIRECTIONAL_MAPPINGS[m.group(1)], properties["addr:street"])
        
        # Expand all other suffixes
        properties["addr:street"] = re.sub(rf'\b({suffixes})\b$', lambda m: SUFFIX_MAPPINGS.get(m.group(0), m.group(0)), properties["addr:street"])

        # Expand "highway" infix, e.g., "OLD HWY 30" -> "OLD Highway 30"
        properties["addr:street"] = re.sub('HWY', 'Highway', properties["addr:street"])

        # Convert to title case
        properties["addr:street"] = properties["addr:street"].title()

        # Capitalize "Mc" correctly, e.g., "East Mcmillan Road" -> "East McMillan Road"
        properties["addr:street"] = re.sub(r'\bMc(\w+)', lambda match: 'Mc' + match.group(1).title(), properties["addr:street"])

        # Remove errant space after Mc (common error in address datasets)
        properties["addr:street"] = re.sub(r'Mc ', 'Mc', properties["addr:street"])
        
        # Capitalize ordinal numbers correctly, e.g., "South 1St Street" -> "South 1st Street"
        properties["addr:street"] = re.sub(r'(\d+)(St|Nd|Rd|Th)', lambda m: m.group(1) + m.group(2).lower(), properties["addr:street"])

        # Replace the original geometry with the centroid (as a point)
        feature["geometry"] = mapping(shape(feature["geometry"]).centroid)

        all_features.append(feature)

# Create a GeoJSON structure with CRS information
geojson_data = {
    "type": "FeatureCollection",
    "crs": {
        "type": "name",
        "properties": {
            "name": "EPSG:3857"
        }
    },
    "features": all_features
}

with open(output_filepath, 'w') as f:
    json.dump(geojson_data, f)

print(f"Recorded {len(all_features)} valid features")
print(f"Saved merged GeoJSON data to {output_filepath}")
