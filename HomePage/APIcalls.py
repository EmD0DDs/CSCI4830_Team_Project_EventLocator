import requests
from dotenv import load_dotenv
from pathlib import Path
import os

class Events:
    def __init__(self):
        self.curr_dir = Path(__file__).resolve().parent if "__file__" in locals() else Path.cwd()
        load_dotenv(self.curr_dir/".env")
        self.api_predict= os.getenv("API_PREDICT")
        self.api_token= os.getenv("PREDICT_TOKEN")
    


    def get_event(self, category : str, radius : float, unit : str, latitude : float, longitude : float) -> list[dict]:
        events_data =[]
        response = requests.get(
            url=self.api_predict,
            headers={
            "Authorization": f"Bearer {self.api_token}",
            "Accept": "application/json"
            },
            params={
                "within" : f"{radius}{unit}@{latitude},{longitude}",
                "category": f"{category}",
                "country": "US",
                

            },
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
                'Location': event.get('geo', {}).get('address', {}),
            }
            events_data.append(e_data)
        
        return events_data





