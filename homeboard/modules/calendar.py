#!/usr/bin/python3
import logging
import requests
import time
import recurring_ical_events
from icalendar import Calendar
from requests.exceptions import HTTPError

logger = logging.getLogger(__name__)

class CalendarModule:
    def __init__(self, config):
        self.calendars = config["icalendars"]
        self.timezone = config["timezone"]
        self.icalendars = [iCalendar(calendar[0], calendar[1]) for calendar in self.calendars]
        if len(self.calendars) > len(self.icalendars):
            logger.warning(f'Some of calendars not loaded properly!')

    def getTodaysEvents(self):
        return

    def getTomorrowsEvents(self):
        return

    def getEventsForFiveDays(self):
        return

class iCalendar:
    def __init__(self, name, url):
        self.name = name
        self.url = url
        if self.url:
            self.calendar = self.getCalendarData()

    def getCalendarData(self):
        logger.info(f'Executing API call for calendar {self.name}.')
        try:
            startTime = time.time()
            response = requests.get(self.url)
            response.raise_for_status()
            endTime = time.time()
            logger.info(f'API call for calendar {self.name} executed. Took {(endTime - startTime):.2f}s.')
            calendar = Calendar.from_ical(response.text)
            return calendar
        except HTTPError as httpError:
            logger.error(f'HTTP error occurred: {httpError}')
        except Exception as ex:
            logger.error(f'Exception occurred: {ex}')

    def __str__(self):
        return f'iCalendar<{self.name}>'