from flask import Flask, request, jsonify, render_template
import requests
import os
from dotenv import load_dotenv
import datetime

# Load environment variables from a `.env` file for security (API key)
load_dotenv()

# Initialize Flask application
app = Flask(__name__)

# API key for OpenWeatherMap (replace with your own key)
API_KEY = os.getenv("OPENWEATHER_API_KEY")

# Base URL for OpenWeatherMap API
BASE_URL = "http://api.openweathermap.org/data/2.5/weather"


# -------------------- Routes and View Functions --------------------

@app.route("/")
def index():
    """
    Renders the main HTML template for the weather application.

    Returns:
        The rendered HTML template (`index.html`).
    """
    return render_template("index.html")


@app.route("/weather", methods=["GET"])
def get_weather():
    """
    Retrieves weather data for a specified city or coordinates.

    Expects either a `city` parameter or both `lat` and `lon` parameters in the query string.

    Returns:
        JSON-formatted weather data for the given city/coordinates on success (200 OK).
        JSON-formatted error message with appropriate status code (400 Bad Request, 500 Internal Server Error) on failure.
    """

    city = request.args.get("city")
    lat = request.args.get("lat")
    lon = request.args.get("lon")

    # Validate input: Require either city or both lat/lon
    if not city and not (lat and lon):
        return jsonify({"error": "Please provide either 'city' or 'lat' and 'lon' parameters"}), 400

    # Construct the API request URL based on provided parameters
    if city:
        url = f"{BASE_URL}?q={city}&appid={API_KEY}&units=metric"
    else:
        url = f"{BASE_URL}?lat={lat}&lon={lon}&appid={API_KEY}&units=metric"

    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for non-200 status codes

        data = response.json()

        # Extract relevant weather data from the response
        weather = {
            "city": city if city else f"({lat}, {lon})",  # Indicate coordinates if no city
            "temperature": data["main"]["temp"],
            "description": data["weather"][0]["description"],
            "humidity": data["main"]["humidity"],
            "wind_speed": data["wind"]["speed"],
            "wind_deg": data["wind"]["deg"],  # Wind direction in degrees
            "cloudiness": data["clouds"]["all"],  # Percentage cloud cover
            "pressure": data["main"]["pressure"],
            "sunrise": convert_timestamp_to_datetime(data["sys"]["sunrise"]),
            "sunset": convert_timestamp_to_datetime(data["sys"]["sunset"]),
        }
        return jsonify(weather)

    except requests.exceptions.RequestException as e:
        # Handle API request errors gracefully (e.g., network issues)
        return jsonify({"error": "Failed to fetch weather data"}), 500

    except Exception as e:  # Catch any unexpected errors
        # Log the error for debugging and return a generic error message
        print(f"Unexpected error: {e}")
        return jsonify({"error": "Internal server error"}), 500


# Function to convert timestamp to human-readable datetime
def convert_timestamp_to_datetime(timestamp):
    """
    Converts a Unix timestamp to a human-readable datetime string.

    Args:
        timestamp (int): Unix timestamp in seconds.

    Returns:
        str: Human-readable datetime string in the format "%Y-%m-%d %H:%M:%S".
    """

    # Convert timestamp to datetime object
    dt_object = datetime.datetime.fromtimestamp(timestamp)

    # Format the datetime object as a string in the desired format
    formatted_datetime = dt_object.strftime("%Y-%m-%d %H:%M:%S")

    return formatted_datetime


# -------------------- MAIN --------------------

if __name__ == "__main__":
    # Disable debug mode for production environments (replace with a production-safe configuration)
    app.run(debug=False)
