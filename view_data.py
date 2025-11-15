import requests
import json

# Get grading by ID
response = requests.get('http://localhost:8000/gradings/1')
grading = response.json()

# Pretty print the results
print(json.dumps(grading['results'], indent=2))