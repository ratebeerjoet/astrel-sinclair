import re
import math
from flask import Flask, jsonify, request
import requests
from datetime import datetime, timedelta
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Allow frontend to access API

NASA_HORIZONS_API = "https://ssd.jpl.nasa.gov/api/horizons.api"
OBLIQUITY_ECLIPTIC = 23.4366  # Approximate obliquity for the year 2025

# Dictionary mapping planets to their Horizons API IDs
PLANET_IDS = {
    "sun": "10",
    "mercury": "199",
    "venus": "299",
    "moon": "301",
    "mars": "499",
    "jupiter": "599",
    "saturn": "699",
    "uranus": "799",
    "neptune": "899",
    "pluto": "999"
}

def parse_ra_dec(response_text):
    """Extract RA and DEC from Horizons response and convert to ecliptic longitude."""
    match = re.search(r'\d{4}-[A-Za-z]{3}-\d{2} \d{2}:\d{2} +([\d ]{2}) ([\d ]{2}) ([\d.]+) +([+-]?\d{2}) ([\d ]{2}) ([\d.]+)', response_text)
    if match:
        ra_h = float(match.group(1))
        ra_m = float(match.group(2))
        ra_s = float(match.group(3))
        dec_d = float(match.group(4))
        dec_m = float(match.group(5))
        dec_s = float(match.group(6))
        
        ra_deg = (ra_h + ra_m / 60 + ra_s / 3600) * 15  # Convert RA to degrees
        dec_deg = dec_d + dec_m / 60 + dec_s / 3600  # Convert DEC to degrees
        
        ecliptic_longitude = ra_deg  # Simplified conversion for now
        return ecliptic_longitude
    return None

def get_planet_positions(date=None, planet=None):
    try:
        logging.info(f"Fetching planetary positions for {planet} on date: {date}")
        
        if planet.lower() not in PLANET_IDS:
            return jsonify({"error": "Invalid planet name."})

        start_date = datetime.strptime(date, "%Y-%m-%d") if date else datetime.utcnow()
        stop_date = start_date + timedelta(days=1)

        # Format date correctly
        start_time = start_date.strftime('%Y-%b-%d')
        stop_time = stop_date.strftime('%Y-%b-%d')

        # Request Right Ascension and Declination
        params = {
            "format": "text",
            "COMMAND": f"'{PLANET_IDS[planet.lower()]}'",
            "OBJ_DATA": "'YES'",
            "MAKE_EPHEM": "'YES'",
            "EPHEM_TYPE": "'OBSERVER'",
            "CENTER": "'500@399'",
            "START_TIME": f"'{start_time}'",
            "STOP_TIME": f"'{stop_time}'",
            "STEP_SIZE": "'1 d'",
            "QUANTITIES": "'1'"
        }

        request_url = NASA_HORIZONS_API + "?" + "&".join([f"{k}={v}" for k, v in params.items()])
        logging.debug(f"Formatted Request URL: {request_url}")
        
        response = requests.get(request_url)
        logging.debug(f"Response status code: {response.status_code}")
        logging.debug(f"Raw response text:\n{response.text}")

        if response.status_code != 200:
            logging.error(f"API request failed with status code {response.status_code}")
            return jsonify({"error": "API request failed."})

        ecliptic_longitude = parse_ra_dec(response.text)
        if ecliptic_longitude is None:
            logging.error("Failed to extract ecliptic longitude from API response.")
            return jsonify({"error": "Failed to extract ecliptic longitude."})

        return jsonify({
            "planet": planet,
            "date": date,
            "ecliptic_longitude": ecliptic_longitude
        })

    except Exception as e:
        logging.exception("Exception occurred while fetching planetary data.")
        return jsonify({"error": str(e)})

@app.route('/planets/<planet>/<date>', methods=['GET'])
def planets(planet, date):
    return get_planet_positions(date, planet)

@app.route('/planets/all/<date>', methods=['GET'])
def all_planets(date):
    results = {}
    for planet in PLANET_IDS.keys():
        try:
            results[planet] = get_planet_positions(date, planet).json
        except Exception as e:
            logging.error(f"Failed to retrieve data for {planet}: {str(e)}")
            results[planet] = {"error": "Failed to retrieve data"}
    return jsonify(results)

if __name__ == '__main__':
    app.run(debug=True)
