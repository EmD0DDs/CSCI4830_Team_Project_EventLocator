import requests
from dotenv import load_dotenv
from pathlib import Path
import os
from datetime import date
from geopy.geocoders import Nominatim

class Events:
    def __init__(self):
        self.curr_dir = Path(__file__).resolve().parent if "__file__" in locals() else Path.cwd()
        load_dotenv(self.curr_dir/".env")
        self.api_predict= os.getenv("API_PREDICT")
        self.api_token= os.getenv("PREDICT_TOKEN")
        self.geolocator = Nominatim(user_agent="EventLocator", timeout=10)
    


    def get_event(self, category : str, radius : float, unit : str, location : str , offset : int, lat : float = None, lon : float = None) -> list[dict]:
        events_data =[]
        limit = 50 #I think free plan caps at 50 
        # Skip geocoding when the caller already has coordinates (e.g. from the browser)
        if lat is None or lon is None:
            locationData = self.geolocator.geocode(location)
            if locationData == None:
                return []
            lat, lon = locationData.latitude, locationData.longitude

        params = {
            "within": f"{radius}{unit}@{lat},{lon}",
            "country": "US",
            "limit": limit,
            "offset": offset,
            # Only events starting today or later (not long-running ones that began earlier), soonest first
            "start.gte": date.today().isoformat(),
            "sort": "start",
        }

        if category != "None":
            params["category"] = category

        response = requests.get(
            url=self.api_predict,
            headers={
            "Authorization": f"Bearer {self.api_token}",
            "Accept": "application/json"
            },
            params=params,
            timeout=10
        )
        response.raise_for_status()
        data = response.json()
        
        for event in data.get('results', []):
            venue = next((e.get('name') for e in event.get('entities', []) if e.get('type') == 'venue'), None)
            e_data = {
                'Title': f"{event.get('title', 'Not Available')}",
                'Category': event.get('category', ''),
                'Venue': venue,
                'Description': f"{event.get('description', 'Not Available')}",
                'Attendance': f"{event.get('phq_attendance', 'Not Available')}",
                'Start_Time': f"{event.get('start_local', 'Not Available')}",
                'End_Time': f"{event.get('end_local', 'Not Available')}",
                'Location': event.get('geo', {}).get('address', {}),
            }
            events_data.append(e_data)
        
        return events_data


#add this back if you wanna test the api. Make sure you call it like python .\HomePage\APIcalls.py and from the directory the env is in
# if __name__ == "__main__":
#     print(Events().get_event("concerts", 100, "mi", "Omaha", 0))
#     print(Events().get_event("concerts", 100, "mi", "Omaha", 50))





