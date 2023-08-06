import logging
import requests
import json
import time
from requests.exceptions import HTTPError

logger = logging.getLogger(__name__)

class WeatherModule:

    def __init__(self, config):
        self.url = config["url"]
        self.apiKey = config["api-key"]
        self.lang = config["lang"]
        self.units = config["units"]
        self.cityName = config["city-name"]

    def getWeatherData(self):
        finalUrl = f'{self.url}?appid={self.apiKey}&q={self.cityName}'
        if self.lang:
            finalUrl = f'{finalUrl}&lang={self.lang}'
        if self.units:
            finalUrl = f'{finalUrl}&units={self.units}'
        try:
            logger.info(f'Executing weather API call.')
            startTime = time.time()
            response = requests.get(finalUrl)
            response.raise_for_status()
            endTime = time.time()
            logger.info(f'Weather API call executed. Took {(endTime - startTime):.2f}s.')
            jsonResponse = response.json()
        except HTTPError as httpError:
            logger.error(f'HTTP error occurred: {httpError}')
        except Exception as ex:
            logger.error(f'Exception occurred: {ex}')
        if jsonResponse:
            return {
                'cityName': jsonResponse["name"],
                'temperature': jsonResponse["main"]["temp"],
                'pressure': jsonResponse["main"]["pressure"],
                'humidity': jsonResponse["main"]["humidity"],
                'windSpeed': jsonResponse["wind"]["speed"],
                'windDirection': jsonResponse["wind"]["deg"],
                'weatherStatus': jsonResponse["weather"][0]["main"]
            }
