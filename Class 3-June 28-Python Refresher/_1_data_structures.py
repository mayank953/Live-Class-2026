"""
_1_data_structures.py

Lists, dictionaries, tuples, and the combination that matters most
later: a list of dictionaries. Still zero mention of AI or agents.

Run with: uv run _1_data_structures.py
"""

# --- Lists: an ordered, changeable collection ---
cities = ["Tokyo", "Delhi", "London"]
print(cities[0])          # indexing -- first item
print(cities[-1])         # negative indexing -- last item
print(cities[0:2])        # slicing -- a sub-list
cities.append("Paris")    # adding to the end
print(cities)

for city in cities:
    print(f"Visiting {city}")

# --- Tuples: like a list, but cannot be changed after creation ---
coordinates = (35.68, 139.69)   # latitude, longitude -- a fixed pair
latitude, longitude = coordinates   # unpacking -- splitting a tuple into separate variables
print(f"Lat: {latitude}, Lon: {longitude}")

# --- Dictionaries: labeled data, accessed by key instead of position ---
weather_reading = {
    "city": "Tokyo",
    "temperature_c": 22.5,
    "condition": "partly cloudy",
}
print(weather_reading["city"])          # access by key
print(weather_reading.get("humidity"))  # .get() -- returns None instead of crashing if missing
weather_reading["humidity"] = 60        # adding a new key
print(weather_reading)

for key, value in weather_reading.items():   # looping over BOTH keys and values
    print(f"{key}: {value}")

# --- The combination that matters most: a list of dictionaries ---
readings = [
    {"city": "Tokyo", "temperature_c": 22.5},
    {"city": "Delhi", "temperature_c": 34.0},
    {"city": "London", "temperature_c": 15.0},
]
for reading in readings:
    print(f"{reading['city']}: {reading['temperature_c']}°C")

warm_cities = [r["city"] for r in readings if r["temperature_c"] > 20]   # a list comprehension
print(f"Warm cities: {warm_cities}")


if __name__ == "__main__":
    print("\nData structures done. Still nothing AI-related -- next up, OOP.")
