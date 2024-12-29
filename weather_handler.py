import requests
from datetime import datetime
from utilities import log_output

def get_weather(arguments, _, text_area, __, self):
    """
    Fetch and display weather information for a given city
    """
    if not arguments:
        log_output(text_area, "Usage: weather <city_name>")
        return
        
    # Join city name parts if city name contains spaces
    city = ' '.join(arguments)
    
    # Replace with your OpenWeatherMap API key
    API_KEY = "3a9391c892cb78fe0da06f3be7ce3567"
    BASE_URL = "http://api.openweathermap.org/data/2.5/weather"
    
    try:
        # Make API request
        params = {
            'q': city,
            'appid': API_KEY,
            'units': 'metric'  # For Celsius
        }
        
        response = requests.get(BASE_URL, params=params)
        
        if response.status_code == 200:
            data = response.json()
            
            # Extract relevant information
            temp = data['main']['temp']
            feels_like = data['main']['feels_like']
            humidity = data['main']['humidity']
            wind_speed = data['wind']['speed']
            description = data['weather'][0]['description']
            pressure = data['main']['pressure']
            
            # Format sunrise and sunset times
            sunrise = datetime.fromtimestamp(data['sys']['sunrise']).strftime('%H:%M')
            sunset = datetime.fromtimestamp(data['sys']['sunset']).strftime('%H:%M')
            
            # Create formatted output
            weather_info = f"""
Weather in {city.title()}:
------------------------
Temperature: {temp}°C
Feels like: {feels_like}°C
Weather: {description.title()}
Humidity: {humidity}%
Wind Speed: {wind_speed} m/s
Pressure: {pressure} hPa
Sunrise: {sunrise}
Sunset: {sunset}
"""
            log_output(text_area, weather_info)
            
        elif response.status_code == 404:
            log_output(text_area, f"Error: City '{city}' not found.")
        else:
            log_output(text_area, f"Error: Unable to fetch weather data. Status code: {response.status_code}")
            
    except requests.RequestException as e:
        log_output(text_area, f"Network error: {e}")
    except Exception as e:
        log_output(text_area, f"Error: {e}")