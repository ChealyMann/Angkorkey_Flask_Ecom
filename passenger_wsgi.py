import sys
import os

# Insert the project directory into the path
project_home = os.path.dirname(os.path.abspath(__file__))
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Import the 'app' object from 'app.py' as 'application'
# 'application' is the default callable that Passenger looks for.
from app import app as application
