import logging
from waveshare_epd import epd7in5_V2

logger = logging.getLogger(__name__)

class DisplayModule:

    def __init__(self, config):
        self.config = config

    @staticmethod
    def displayImage(image):
        logger.info("Displaying image on 7,5\" e-paper display.")
        try:
            display = epd7in5_V2.EPD()
            display.init()
            logger.info("Display initialized.")
            display.Clear()
            display.display(display.getbuffer(image))
            display.sleep()

        except IOError as e:
            logger.error(e)
