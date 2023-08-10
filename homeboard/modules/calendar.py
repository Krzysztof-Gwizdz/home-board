#!/usr/bin/python3
import arrow
import logging
import requests
import time
import recurring_ical_events
from icalendar import Calendar
from requests.exceptions import HTTPError

logger = logging.getLogger(__name__)

fmt = lambda date: (date.year, date.month, date.day, date.hour, date.minute, date.second)

class CalendarModule:
    def __init__(self, config):
        self.calendars = config["icalendars"]
        self.timezone = config["timezone"]
        self.icalendars = [iCalendar(calendar[0], calendar[1]) for calendar in self.calendars]
        if len(self.calendars) > len(self.icalendars):
            logger.warning(f'Some of calendars not loaded properly!')

    def getTodaysEvents(self, count=5):
        startTimeline = arrow.utcnow()
        startTimeline = arrow.get(startTimeline.date())
        endTimeline = startTimeline.shift(days = 1)
        tStart = fmt(startTimeline)
        tEnd = fmt(endTimeline)
        recurringEvents = ((calendar.name, recurring_ical_events.of(calendar.calendar).between(tStart, tEnd)) for calendar in self.icalendars)
        events = self.__convertToEventList(recurringEvents)
        sortedEvents = CalendarModule.sortEvents(events)
        # print(f'Today\'s events:\n{str(sortedEvents[0:count])}')
        if sortedEvents:
            return sortedEvents[0:count]
        else:
            return None

    def getTomorrowsEvents(self, count=5):
        startTimeline = arrow.utcnow().shift(days = 1)
        startTimeline = arrow.get(startTimeline.date())
        endTimeline = startTimeline.shift(days = 1)
        tStart = fmt(startTimeline)
        tEnd = fmt(endTimeline)
        recurringEvents = ((calendar.name, recurring_ical_events.of(calendar.calendar).between(tStart, tEnd)) for calendar in self.icalendars)
        events = self.__convertToEventList(recurringEvents)
        sortedEvents = CalendarModule.sortEvents(events)
        # print(f'Tomorrow\'s events:\n{str(sortedEvents[0:count])}')
        if sortedEvents:
            return sortedEvents[0:count]
        else:
            return None

    def getEventsForFiveDays(self, count=5):
        startTimeline = arrow.utcnow().shift(days = 2)
        startTimeline = arrow.get(startTimeline.date())
        endTimeline = startTimeline.shift(days = 6)
        tStart = fmt(startTimeline)
        tEnd = fmt(endTimeline)
        recurringEvents = ((calendar.name, recurring_ical_events.of(calendar.calendar).between(tStart, tEnd)) for calendar in self.icalendars)
        events = self.__convertToEventList(recurringEvents)
        sortedEvents = CalendarModule.sortEvents(events)
        # print(f'Next five day\'s events:\n{str(sortedEvents[0:count])}')
        if sortedEvents:
            return sortedEvents[0:count]
        else:
            return None

    def __convertToEventList(self, recurringEvents):
        return list(
            {
                'title': event.get('SUMMARY').lstrip(),

                'begin': arrow.get(event.get('DTSTART').dt).to(self.timezone) if (
                        arrow.get(event.get('DTSTART').dt).format('HH:mm') != '00:00')
                else arrow.get(event.get('DTSTART').dt).replace(tzinfo=self.timezone),

                'end': arrow.get(event.get('DTEND').dt).to(self.timezone) if (
                        arrow.get(event.get('dtstart').dt).format('HH:mm') != '00:00')
                else arrow.get(event.get('DTEND').dt).replace(tzinfo=self.timezone),

                'owner': calendar[0]
            } for calendar in recurringEvents for event in calendar[1]
        )

    @staticmethod
    def sortEvents(events):
        if not events:
            logger.debug(f'Cannot sort empty event list.')
        else:
            byDate = lambda event: event['begin']
            events.sort(key=byDate)
            return events

    @staticmethod
    def isEventAllDay(event):
        if not ('end' and 'begin') in event:
            logger.debug(f'Not a valid event. Must have start and end date.')
            raise Exception('Not valid event!')
        begin, end = event['begin'], event['end']
        duration = end - begin
        return (begin.format('HH:mm') == '00:00' and end.format('HH:mm') == '00:00' and duration.days >=1)

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