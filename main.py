import sys
import time
import requests
import json
import argparse

argparser = argparse.ArgumentParser(description="quickly get train times from Elron.ee")
argparser.add_argument("origin", help="the origin station to specify")
argparser.add_argument("destination", help="the destination station to specify")
argparser.add_argument("-d", "--date", default="today", help="the destination station to specify")
args = argparser.parse_args()

def timestamp_from_minutes(x: int) -> str:
	hours = str(x//60).rjust(2, "0")
	minutes = str(x%60).rjust(2, "0")
	return f"{hours}:{minutes}"

def current_time_minutes() -> int:
	return int(time.strftime("%H")) * 60 + int(time.strftime("%M"))

def build_payload(date: str, origin: str, destination: str) -> str:
    # date ought to be formatted as year-month-day, ex: 2019-12-31
    payload = '{"date":"' + date + '","origin_stop_area_id":"'
    payload += origin + '","destination_stop_area_id":"'
    payload += destination + '","channel":"web"}'
    return payload

with open("stops.json", "r") as fptr:
    ID_TABLE = {
        e["stop_name"].lower() : e["stop_area_id"] for e in json.loads(fptr.read())
    }

ARGS = [x.strip().lower() for x in sys.argv[1:]]
BODY = '{"date":"' + time.strftime("%Y-%m-%d") + '","origin_stop_area_id":"' + ID_TABLE[ARGS[0]] + '","destination_stop_area_id":"' + ID_TABLE[ARGS[1]] + '","channel":"web"}'
HEADERS = {
    'Host': 'api.ridango.com',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:72.0) Gecko/20100101 Firefox/72.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate, br',
    'Content-Type': 'application/json',
    'Content-Length': '112',
    'DNT': '1',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Cache-Control': 'max-age=0, no-cache',
    'Origin': 'https://api.ridango.com',
    'Pragma': 'no-cache'
    }
URL = 'https://api.ridango.com/v2/64/intercity/stopareas/trips/direct'

response = requests.put(URL, data=BODY, headers=HEADERS)

for j in response.json()["journeys"]:
    c = current_time_minutes()
    if j["trips"][0]["departure_time_min"] >= c:
        departure = timestamp_from_minutes(j["trips"][0]["departure_time_min"])
        arrival = timestamp_from_minutes(j["trips"][0]["arrival_time_min"])
        print(j["journey_name"])
        print(f"{departure} -> {arrival}\n")