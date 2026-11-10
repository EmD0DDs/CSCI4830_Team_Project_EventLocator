import requests
from dotenv import load_dotenv
from pathlib import Path
import os
from geopy.geocoders import Nominatim

class Events:
    def __init__(self):
        self.curr_dir = Path(__file__).resolve().parent if "__file__" in locals() else Path.cwd()
        load_dotenv(self.curr_dir/".env")
        self.api_predict= os.getenv("API_PREDICT")
        self.api_token= os.getenv("PREDICT_TOKEN")
        self.geolocator = Nominatim(user_agent="EventLocator", timeout=10)
    


    def get_event(self, category : str, radius : float, unit : str, location : str , offset : int) -> list[dict]:
        events_data =[]
        locationData = self.geolocator.geocode(location)
        limit = 50 #I think free plan caps at 50 
        if locationData == None:
            return list({"Error": "Could not find location"})

        params = {
            "within": f"{radius}{unit}@{locationData.latitude},{locationData.longitude}",
            "country": "US",
            "limit": limit,
            "offset": offset,
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
            e_data = {
                'Title': f"{event.get('title', 'Not Available')}",
                'Description': f"{event.get('description', 'Not Available')}",
                'Attendance': f"{event.get('phq_attendance', 'Not Available')}",
                'Start_Time': f"{event.get('start_local', 'Not Available')}",
                'End_Time': f"{event.get('end_local', 'Not Available')}",
                'Location': event.get('geo', {}).get('address', {}).get('formatted_address', 'Location unavailable'),
            }
            events_data.append(e_data)
        
        return events_data


#add this back if you wanna test the api. Make sure you call it like python .\HomePage\APIcalls.py and from the directory the env is in
# if __name__ == "__main__":
#     print(Events().get_event("concerts", 100, "mi", "Omaha", 0))
#     print(Events().get_event("concerts", 100, "mi", "Omaha", 50))





