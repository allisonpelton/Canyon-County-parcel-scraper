import os
import requests
import json
import re
import sys
from shapely.geometry import shape, mapping

### Configuration

output_filepath = "./Elmore County parcels.geojson"  # Filepath to save the merged GeoJSON
min_features = int(sys.argv[1]) # Try to grab at least this many features, if enough are available

### Mappings

ABBR_MAPPINGS = {
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
    "PT": "Point",
    "WY": "Way",
    "RNCH": "Ranch",
    "CRK": "Creek",
    "MTN": "Mountain",
    "RES": "Reservoir",
    "AM": "American",
    "GV": "Grandview",
    "FV": "Featherville",
    "KH": "King Hill"
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
    service = "Elmore_County_Parcels"
    url = f"https://services.arcgis.com/91hXl6NfvLGEi8x5/arcgis/rest/services/{service}/FeatureServer/0/query"
    params = {
        "f": "geojson",
        "where": "1=1",
        "returnGeometry": "true",
        "outFields": "PM_PROP_AD,PM_PROP_ZP",
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
while result_offset < min_features and (features := fetch_page(result_offset)) and len(features) != 0:
    result_offset += len(features)
    # Process the features and apply the necessary parsing
    for feature in features:
        properties = feature["properties"]
    
        # Parse PM_PROP_AD into house number and street name
        address = properties["PM_PROP_AD"]
        
        #Remove extra spaces
        address = re.sub("\s+"," ",address)
        address = re.sub("\s$","",address)

        ### Data validation
        if address is None:
            continue
        properties["addr:housenumber"], properties["addr:street"] = (None, None) if len(parts:=(address.split(' ', 1))) < 2 else (parts[0], parts[1]) #None if invalid
        
        
        # Only keep features with a valid housenumber
        if properties["addr:housenumber"] == "0" or properties["addr:housenumber"] is None or properties["addr:housenumber"] == "" or properties["addr:housenumber"][0] not in "123456789":
            continue

        properties["addr:postcode"] = properties["PM_PROP_ZP"]

        ### Column Cleanup
        del properties["PM_PROP_AD"] # Not used in the output
        del properties["PM_PROP_ZP"]

        ### Address parsing

        # A leading number in addr:street is likely a unit number
        start = properties["addr:street"].split()
        if start[0].isnumeric() or len(start[0]) == 1 and start[0] in "ABCDFGHIJKLMOPQRTUVXYZ":
            properties["addr:street"] = ' '.join(start[1:])
            properties["addr:unit"] = start[0]

        # Remove probable unit numbers/letters from street name and flag them. Trailing numbers, except on highways, and trailing single letters are probably units.
        if "addr:street" in properties and properties["addr:street"].find("HWY") == -1:
            match = re.search(r"\s([A-D]|\d+)$", properties["addr:street"]) # Ideally we would match all trailing letters, but E cannot be disambiguated as a unit or postdirectional
            if match:
                properties["addr:unit"] = match.group(1)
                properties["addr:street"] = properties["addr:street"][:match.start()].strip()
            
            ### Add missing "Street" suffix present in Elmore County dataset
            if properties["addr:street"].split()[-1] not in ABBR_MAPPINGS and properties["addr:street"].split()[-1] not in DIRECTIONAL_MAPPINGS.values() and properties["addr:street"].split()[-1] not in DIRECTIONAL_MAPPINGS.keys():
                properties["addr:street"] = properties["addr:street"] + " Street"

        # Remove extraneous plus signs
        properties["addr:street"] = re.sub(" \+ "," ",properties["addr:street"])
        properties["addr:street"] = re.sub(" \+","",properties["addr:street"])

        # Generate capture groups for suffixes and directionals
        directionals = '|'.join(re.escape(direction) for direction in DIRECTIONAL_MAPPINGS.keys())
        suffixes = '|'.join(re.escape(abbr) for abbr in ABBR_MAPPINGS.keys())

        # Expand suffixes followed by a postdirectional, e.g., "17th Ave S" -> "17th Avenue South"
        properties["addr:street"] = re.sub(rf' ({suffixes}) ({directionals})', lambda m: ' ' + ABBR_MAPPINGS[m.group(1)] + ' ' + DIRECTIONAL_MAPPINGS[m.group(2)], properties["addr:street"])

        # Expand predirectionals
        properties["addr:street"] = re.sub(rf'^({directionals}) ', lambda m: DIRECTIONAL_MAPPINGS[m.group(1)] + ' ', properties["addr:street"])

        # Expand postdirectionals
        properties["addr:street"] = re.sub(rf' ({directionals})$', lambda m: ' ' + DIRECTIONAL_MAPPINGS[m.group(1)], properties["addr:street"])
        
        # Expand all other suffixes (may appear as infixes as well)
        # May incorrectly expand Saint to Street
        properties["addr:street"] = re.sub(rf'\b({suffixes})\b', lambda m: ABBR_MAPPINGS.get(m.group(0), m.group(0)), properties["addr:street"])

        # Convert to title case
        properties["addr:street"] = properties["addr:street"].title()

        # Capitalize "Mc" correctly, e.g., "East Mcmillan Road" -> "East McMillan Road"
        properties["addr:street"] = re.sub(r'\bMc(\w+)', lambda match: 'Mc' + match.group(1).title(), properties["addr:street"])

        # Remove errant space after Mc (common error in address datasets)
        properties["addr:street"] = re.sub(r'Mc ', 'Mc', properties["addr:street"])
        
        # Capitalize ordinal numbers correctly, e.g., "South 1St Street" -> "South 1st Street"
        properties["addr:street"] = re.sub(r'(\d+)(St|Nd|Rd|Th)', lambda m: m.group(1) + m.group(2).lower(), properties["addr:street"])

        ### Geometry handling

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