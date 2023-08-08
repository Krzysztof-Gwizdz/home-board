import os
import json
import logging
from logging.handlers import RotatingFileHandler

from homeboard.modules import weather
from homeboard.modules import calendar
from homeboard.modules import dashboard_image
# from homeboard.modules import display

streamHandler = logging.StreamHandler()
streamHandler.setLevel(logging.ERROR)

projectPath = os.path.dirname(os.path.realpath(__file__))

if not os.path.exists(f'{projectPath}/logs'):
    os.mkdir(f'{projectPath}/logs')

logging.basicConfig(
    level = logging.INFO,
    format = '%(asctime)s | %(levelname)s | %(name)s | %(message)s',
    datefmt = '%Y-%m-%d %H:%M:%S',
    handlers = [
        streamHandler,
        RotatingFileHandler(
            f'{projectPath}/logs/home-board.log',
            maxBytes = 2097152,
            backupCount = 5
        )
    ]
)

logger = logging.getLogger(__name__)

class HomeBoard:
    """
    HomeBoard main class
    """

    def __init__(self):
        self.loadSettings()
        self.weatherModule = weather.WeatherModule(self.settings["configuration"]["weather"])
        self.calendarModule = calendar.CalendarModule(self.settings["configuration"]["calendar"])
        self.imageModule = dashboard_image.ImageModule(self.settings["configuration"]["image"])
        # self.displayModule = display.DisplayModule(self.settings["configuration"]["display"])

    def run(self):
        weatherData = self.weatherModule.getWeatherData()
        # print(f'Weather data for {weatherData["cityName"]} - {weatherData["weatherStatus"]} Temp: {weatherData["temperature"]}, Humidity: {weatherData["humidity"]}%')
        todayEvents = self.calendarModule.getTodaysEvents()
        tomorrowEvents = self.calendarModule.getTomorrowsEvents()
        nextDaysEvents = self.calendarModule.getEventsForFiveDays()
        self.imageModule.testImage(todayEvents, tomorrowEvents, nextDaysEvents, weatherData)
        # self.displayModule.displayImage(self.imageModule.renderDashboardImage(todayEvents, tomorrowEvents, nextDaysEvents, weatherData))

        return

    def loadSettings(self):
        settingsPath = os.path.abspath(os.path.join(__file__, os.pardir, os.pardir, 'config.json'))
        try:
            with open(settingsPath) as settingsFile:
                self.settings = json.load(settingsFile)
                logger.info('Settings file loaded.')
        except FileNotFoundError:
            logger.error(f'Settings file not found in {settingsPath}.')