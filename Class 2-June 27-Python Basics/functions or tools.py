

import time

def get_current_time() -> str:
    """Return the current time as a human-readable string."""
    return time.strftime("%Y-%m-%d %H:%M:%S")


print(get_current_time())











fake_weather_data = {
        "tokyo": "22°C, partly cloudy",
        "delhi": "34°C, clear skies",
        "london": "15°C, light rain",
    }


def get_weather(city: str) -> str:
    """Return the current weather for `city`. (Mock data for teaching.)"""
    return fake_weather_data.get(city.lower(), f"No weather data for {city!r}")



