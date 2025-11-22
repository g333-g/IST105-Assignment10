import random
import requests
import os
from dotenv import load_dotenv
from datetime import datetime
from django.shortcuts import render
from .forms import ContinentForm
from pymongo import MongoClient

load_dotenv()

MONGO_URI = os.getenv('MONGO_URI', 'mongodb://98.92.156.75:27017')
client = MongoClient(MONGO_URI)
db = client.geodata

OPENWEATHERMAP_API_KEY = os.getenv('OPENWEATHERMAP_API_KEY', 'a3c4ee66a2992a074e39114df6b984d4')

def continent_view(request):
    if request.method == 'POST':
        form = ContinentForm(request.POST)
        if form.is_valid():
            continent = form.cleaned_data['continent']
            response = requests.get(f"https://restcountries.com/v3.1/region/{continent}")
            countries = random.sample(response.json(), 5)
            results = []
            for c in countries:
                capital = c.get("capital", [""])[0]
                name = c.get("name", {}).get("common", "")
                pop = c.get("population", 0)
                try:
                    weather = requests.get(
                        "https://api.openweathermap.org/data/2.5/weather",
                        params={
                            "q": capital,
                            "appid": OPENWEATHERMAP_API_KEY,
                            "units": "metric"
                        }
                    ).json()
                    temp = weather["main"]["temp"]
                    desc = weather["weather"][0]["description"]
                except Exception:
                    temp, desc = None, "Not found"
                
                results.append({
                    "country": name,
                    "capital": capital,
                    "population": pop,
                    "temperature_celsius": temp,
                    "weather_description": desc
                })

            record = {
                "continent": continent,
                "search_timestamp": datetime.utcnow().isoformat(),
                "results": results
            }
            db.searches.insert_one(record)

            return render(request, "search_results.html", {"results": results, "continent": continent})
    else:
        form = ContinentForm()
    return render(request, "continent_form.html", {"form": form})

def history_view(request):
    history = list(db.searches.find().sort("search_timestamp", -1))
    return render(request, "history.html", {"history": history})

