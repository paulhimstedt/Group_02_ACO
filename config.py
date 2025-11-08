# config.py
import os
from dotenv import load_dotenv

# Load variables from the .env file
load_dotenv()

# Get the API key from the environment
GOOGLE_MAPS_API_KEY = os.environ.get("GOOGLE_MAPS_API_KEY")

# Check if the key was loaded
if not GOOGLE_MAPS_API_KEY:
    print("Warning: GOOGLE_MAPS_API_KEY not found. Did you create a .env file?")
    # You could also raise an error:
    # raise ValueError("No GOOGLE_MAPS_API_KEY set. Check your .env file.")

# Your other configuration settings
TRAVEL_MODE = "transit"
DEFAULT_STAY_TIME = 30