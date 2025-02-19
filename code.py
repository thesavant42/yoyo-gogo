import json
import os
import sys

# Path to the configuration file
CONFIG_FILE = "config.json"

try:
    # Try to open and read the configuration file
    with open(CONFIG_FILE, "r") as f:
        config = json.load(f)  # Load JSON data into a dictionary
        PROJECT = config.get("active_project", "default_project")  # Get project name, or use "default_project"
except Exception as e:
    # Handle cases where the config file is missing or invalid
    print(f"Error reading {CONFIG_FILE}: {e}")
    PROJECT = "default_project"  # Fallback project if an error occurs

# Ensure CircuitPython can find the projects folder
PROJECTS_DIR = "/projects"
sys.path.append(PROJECTS_DIR)

print(f"DEBUG: Available projects: {os.listdir(PROJECTS_DIR)}")
print(f"DEBUG: Attempting to run project '{PROJECT}'")

try:
    __import__(PROJECT)  # Use absolute import for CircuitPython compatibility
except ImportError as e:
    print(f"Error: Project '{PROJECT}' not found or could not be loaded: {e}")
    print("Running default error handler instead.")
    __import__("default_project")  # Use absolute import for the fallback
except Exception as e:
    print(f"Unexpected error running {PROJECT}: {e}")
    print("Running default error handler instead.")
    __import__("default_project")