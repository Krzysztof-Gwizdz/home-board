import logging
import os
import io
import arrow
from PIL import Image, ImageDraw, ImageFont
from homeboard.modules import calendar

logger = logging.getLogger(__name__)

FONTS_PATH = os.path.abspath(os.path.join(__file__, os.pardir, os.pardir, 'fonts'))
IMAGES_PATH = os.path.abspath(os.path.join(__file__, os.pardir, os.pardir, 'images'))
FONT_LATO = ImageFont.truetype(os.path.join(FONTS_PATH, 'Lato-Regular.ttf'), 16)
FONT_LATO_BOLD = ImageFont.truetype(os.path.join(FONTS_PATH, 'Lato-Bold.ttf'), 22)
FONT_ROBOTO_SERIF = ImageFont.truetype(os.path.join(FONTS_PATH, 'RobotoSerif-Var.ttf'), 32)

def openPngSize(name, width, height):
    image = Image.open(os.path.join(IMAGES_PATH, name))
    useWidth = image.size[0] > image.size[1]
    if useWidth:
        ratio = (width/float(image.size[0]))
        output_height = int((float(image.size[1])*float(ratio)))
        image = image.resize((width, output_height))
    else:
        ratio = (height/float(image.size[1]))
        output_width = int((float(image.size[0])*float(ratio)))
        image = image.resize((output_width,height))
    return image

#Icons
# temperatureIconPng = cairo.ImageSurface(cairo.FORMAT_A1, 25, 25)
# temperatureIconPng = cairo.svg2png(url=os.path.join(svgsPath, 'temperature-three-quarters.svg'), output_width=25, output_height=25)
# temperatureIcon = Image.frombytes('1', (25,25), temperatureIconPng)
temperatureIcon = openPngSize('temperature-three-quarters.png', 25, 25)
dropletIcon = openPngSize('droplet.png', 25, 25)
pressureIcon = openPngSize('arrows-down-to-line.png', 25, 25)
windIcon = openPngSize('wind.png', 25, 25)
arrowIcon = openPngSize('arrow-up.png', 50, 50)

statusImageNameDict = {
    "01d": "sun.png",
    "01n": "moon.png",
    "02d": "cloud-sun.png",
    "02n": "cloud-moon.png",
    "03d": "cloud.png",
    "03n": "cloud.png",
    "04d": "cloud.png",
    "04n": "cloud.png",
    "09d": "cloud-showers-heavy.png",
    "09n": "cloud-showers-heavy.png",
    "10d": "cloud-sun-rain.png",
    "10n": "cloud-moon-rain.png",
    "11d": "cloud-bolt.png",
    "11n": "cloud-bolt.png",
    "13d": "snowflake.png",
    "13n": "snowflake.png",
    "50d": "smog.png",
    "50n": "smog.png"
}


testFile = os.path.abspath(os.path.join(__file__, os.pardir, 'test.bmp'))
DEGREE_SIGN = u'\N{DEGREE SIGN}'

class ImageModule:

    def __init__(self, config):
        self.locale = config["locale"]
        return

    def renderDashboardImage(self, todayEvents, tomorrowEvents, nextDaysEvents, weatherData):
        logger.info('Start of rendering dashboard image.')
        today = arrow.utcnow().format('dddd DD. MMMM YYYY', locale=self.locale)
        image = Image.new('1', (800,480), 255)
        draw = ImageDraw.Draw(image)

        # Lines
        draw.line([(200,0),(200,480)], fill="Black", width=2)
        draw.line([(200,60),(800,60)], fill="Black", width=2)
        draw.line([(200,200),(800,200)], fill="Black", width=1)
        draw.line([(200,340),(800,340)], fill="Black", width=1)

        # Weather
        statusIcon = openPngSize(statusImageNameDict[weatherData["weatherStatus"]], 150, 150)
        draw.bitmap((25,30), statusIcon)

        draw.text((100,200), f'{weatherData["cityName"]}', font=FONT_LATO_BOLD, anchor="ma")

        FONT_LATO_BOLD.size = 32

        draw.bitmap((40, 250), temperatureIcon)
        draw.text((65, 250), f'{weatherData["temperature"]} {DEGREE_SIGN}C', font=FONT_LATO_BOLD)

        draw.bitmap((40, 285), dropletIcon)
        draw.text((65, 285), f'{weatherData["humidity"]} %', font=FONT_LATO_BOLD)

        draw.bitmap((35, 320), pressureIcon)
        draw.text((65, 320), f'{weatherData["pressure"]} hPa', font=FONT_LATO_BOLD)

        draw.bitmap((35,355), windIcon)
        draw.text((65,355), f'{weatherData["windSpeed"]} m/s', font=FONT_LATO_BOLD)

        FONT_LATO_BOLD.size = 22

        arrowIcn = arrowIcon.rotate(angle=(180 - weatherData["windDirection"]))
        draw.bitmap((75, 385), arrowIcn)

        # Date
        draw.text((500,30), f'{today}', font=FONT_ROBOTO_SERIF, anchor="mm")

        #Today
        draw.text((205,65), "Dzisiaj", font=FONT_LATO_BOLD)
        if todayEvents:
            for idx, event in enumerate(todayEvents):
                draw.text((205,(97 + idx * 19)), event['title'], font=FONT_LATO)
                draw.text((650,(97 + idx * 19)), event['owner'], font=FONT_LATO, anchor="ma")
                if calendar.CalendarModule.isEventAllDay(event):
                    draw.text((750,(97 + idx * 19)), "cały dzień", font=FONT_LATO, anchor="ma")
                else:
                    draw.text((750,(97 + idx * 19)), f'{event["begin"].format("HH:mm")} - {event["end"].format("HH:mm")}', font=FONT_LATO, anchor="ma")

        #Tomorrow
        draw.text((205, 205), "Jutro", font=FONT_LATO_BOLD)
        if tomorrowEvents:
            for idx, event in enumerate(tomorrowEvents):
                draw.text((205,(236 + idx * 19)), event['title'], font=FONT_LATO)
                draw.text((650,(236 + idx * 19)), event['owner'], font=FONT_LATO, anchor="ma")
                if calendar.CalendarModule.isEventAllDay(event):
                    draw.text((750,(236 + idx * 19)), "cały dzień", font=FONT_LATO, anchor="ma")
                else:
                    draw.text((750,(236 + idx * 19)), f'{event["begin"].format("HH:mm")} - {event["end"].format("HH:mm")}', font=FONT_LATO, anchor="ma")

        #Next 5 days
        draw.text((205, 345), "Następne 5 dni", font=FONT_LATO_BOLD)
        if nextDaysEvents:
            for idx, event in enumerate(nextDaysEvents):
                draw.text((205,(379 + idx * 19)), event['title'], font=FONT_LATO)
                draw.text((600,(379 + idx * 19)), event['owner'], font=FONT_LATO, anchor="ma")
                draw.text((650,(379 + idx * 19)), event['begin'].format("DD.MM"), font=FONT_LATO)
                if calendar.CalendarModule.isEventAllDay(event):
                    draw.text((750,(379 + idx * 19)), "cały dzień", font=FONT_LATO, anchor="ma")
                else:
                    draw.text((750,(379 + idx * 19)), f'{event["begin"].format("HH:mm")} - {event["end"].format("HH:mm")}', font=FONT_LATO, anchor="ma")
        logger.info(f'Rendered image size: {image.size}')
        return image

    def testImage(self, todayEvents, tomorrowEvents, nextDaysEvents, weatherData):
        logger.info('Start of rendering test image.')
        today = arrow.utcnow().format('dddd DD. MMMM YYYY', locale=self.locale)
        image = Image.new('1', (800,480), 255)
        draw = ImageDraw.Draw(image)

        # Lines
        draw.line([(200,0),(200,480)], fill="Black", width=2)
        draw.line([(200,60),(800,60)], fill="Black", width=2)
        draw.line([(200,200),(800,200)], fill="Black", width=1)
        draw.line([(200,340),(800,340)], fill="Black", width=1)

        # Weather
        statusIcon = openPngSize(statusImageNameDict[weatherData["weatherStatus"]], 150, 150)
        draw.bitmap((25,30), statusIcon)

        draw.text((100,200), f'{weatherData["cityName"]}', font=FONT_LATO_BOLD, anchor="ma")

        FONT_LATO_BOLD.size = 32

        draw.bitmap((40, 250), temperatureIcon)
        draw.text((65, 250), f'{weatherData["temperature"]} {DEGREE_SIGN}C', font=FONT_LATO_BOLD)

        draw.bitmap((40, 285), dropletIcon)
        draw.text((65, 285), f'{weatherData["humidity"]} %', font=FONT_LATO_BOLD)

        draw.bitmap((35, 320), pressureIcon)
        draw.text((65, 320), f'{weatherData["pressure"]} hPa', font=FONT_LATO_BOLD)

        draw.bitmap((35,355), windIcon)
        draw.text((65,355), f'{weatherData["windSpeed"]} m/s', font=FONT_LATO_BOLD)

        FONT_LATO_BOLD.size = 22

        arrowIcn = arrowIcon.rotate(angle=(180 - weatherData["windDirection"]))
        draw.bitmap((75, 385), arrowIcn)

        # Date
        draw.text((500,30), f'{today}', font=FONT_ROBOTO_SERIF, anchor="mm")

        #Today
        draw.text((205,65), "Dzisiaj", font=FONT_LATO_BOLD)
        if todayEvents:
            for idx, event in enumerate(todayEvents):
                draw.text((205,(97 + idx * 19)), event['title'], font=FONT_LATO)
                draw.text((650,(97 + idx * 19)), event['owner'], font=FONT_LATO, anchor="ma")
                if calendar.CalendarModule.isEventAllDay(event):
                    draw.text((750,(97 + idx * 19)), "cały dzień", font=FONT_LATO, anchor="ma")
                else:
                    draw.text((750,(97 + idx * 19)), f'{event["begin"].format("HH:mm")} - {event["end"].format("HH:mm")}', font=FONT_LATO, anchor="ma")

        #Tomorrow
        draw.text((205, 205), "Jutro", font=FONT_LATO_BOLD)
        if tomorrowEvents:
            for idx, event in enumerate(tomorrowEvents):
                draw.text((205,(236 + idx * 19)), event['title'], font=FONT_LATO)
                draw.text((650,(236 + idx * 19)), event['owner'], font=FONT_LATO, anchor="ma")
                if calendar.CalendarModule.isEventAllDay(event):
                    draw.text((750,(236 + idx * 19)), "cały dzień", font=FONT_LATO, anchor="ma")
                else:
                    draw.text((750,(236 + idx * 19)), f'{event["begin"].format("HH:mm")} - {event["end"].format("HH:mm")}', font=FONT_LATO, anchor="ma")

        #Next 5 days
        draw.text((205, 345), "Następne 5 dni", font=FONT_LATO_BOLD)
        if nextDaysEvents:
            for idx, event in enumerate(nextDaysEvents):
                draw.text((205,(379 + idx * 19)), event['title'], font=FONT_LATO)
                draw.text((600,(379 + idx * 19)), event['owner'], font=FONT_LATO, anchor="ma")
                draw.text((650,(379 + idx * 19)), event['begin'].format("DD.MM"), font=FONT_LATO)
                if calendar.CalendarModule.isEventAllDay(event):
                    draw.text((750,(379 + idx * 19)), "cały dzień", font=FONT_LATO, anchor="ma")
                else:
                    draw.text((750,(379 + idx * 19)), f'{event["begin"].format("HH:mm")} - {event["end"].format("HH:mm")}', font=FONT_LATO, anchor="ma")
            logger.info(f'Rendered image size: {image.size}')
            image.save(testFile)
