import datetime
import time
import json
from Display import PyLcd as lcd_screen
import pygame
import logging
import requests

# Constants
pygame.mouse.set_visible(False)
fontpath = pygame.font.match_font('dejavusansmono')
font = pygame.font.Font(fontpath, 36)
fontS2 = pygame.font.Font(fontpath, 28)
fontSm = pygame.font.Font(fontpath, 18)
colourWhite = (255, 255, 255)
colourBlack = (0, 0, 0)

#TODO: add auto installer, auto config, with python setup tools, and read config ...
# installPath is like "/home/username/installfolder/img/big" ... ".../small"
installPathImgBig = "/home/pi/weatherstation/img/big/"
installPathImgSmall = "/home/pi/weatherstation/img/small/"
# Constants

class PygameWeather(object):
    """This class uses pygame and show on console Weatherinformation graphicaly"""

    def __init__(self):
        #TODO: add config file, to configure outside, if confifile present read data... set values
        self.updateRate = 7200     # seconds, for server call # update interval
        self.betweenTime = 20      # accumulated seconds screens/program are running, if matching or greate updateRate ... update #FIXME: prevent Bufferoverflow
        self.screenTimeOffset = 20 # the time the screens are shown
        # more vars
        self.states = ["initial", "screen1", "screen2", "screen3", "network"]
        self.state = "initial"
        self.weather_data = {}
        self.h = 0
        self.w = 0

        # today variables
        self.today = ""
        self.windSpeed = ""
        self.currWind = ""
        self.currTemp = ""
        self.currTempFeeling = ""
        self.currPress = ""
        self.uv = ""
        self.todayDesc = ""
        self.humid = ""

        # forecast variables
        self.forecastDesc = ""
        self.forecastDays = {}
        self.forecaseHighs = {}
        self.forecaseLows = {}
        self.forecastPrecips = {}
        self.forecastWinds = {}
        self.forecastIcons = {}
        # Create an instance of the PyLcd class
        self.lcd = lcd_screen()

    # see a clock with secounds, just call it in loop or as many times as you need it, after it clear the screen !
    def showClock(self):
        # clear screen and update
        lcd.screen.fill(colourBlack)
        pygame.display.update()
        # show the clock @ (10,260), uodate the screen and wait 1 second
        updated = time.strftime("%H:%M:%S")
        text_surface = fontS2.render(updated, True, colourWhite)
        lcd.screen.blit(text_surface, (10, 260))
        pygame.display.update()
        time.sleep(1)

    def callServer(self):
        def getDataFromServer():
            data = {}
            response = requests.get('https://api.forecast.io/forecast/500e8abf656226b5076cd1886f87f8b2/51.7781718,14.2472211?units=si')
            if response.status_code == 200:
                # allet schick -> los gehts
                data = response.json() #r.text
                if data != {}:
                    #TODO check if all keys are present ...
                    logging.info("Calling server successful")
                else:
                    pass # if failure calling ... get data from backup server , mapping icons ...
            else:
                # server connection broken, or no internet, or ...
                logging.info("Calling server failure")
            self.state = "screen1"
            return data

        if self.state == "initial":
            self.weather_data = getDataFromServer()
        if self.betweenTime >= self.updateRate:
            self.betweenTime = 0
            self.state = "network"
            logging.info(format(self.updateRate) + " seconds is over, Calling server...")
            self.weather_data = getDataFromServer()

    def updateScreen(self, action):
        self.lcd.screen.fill(colourBlack)
        pygame.display.update()
        ############ screen specifica begin #############
        action()
        ############ screen specifica end ###############
        # update screen
        pygame.display.update()
        # wait
        time.sleep(self.screenTimeOffset)
        self.betweenTime += self.screenTimeOffset
        # blank the screen after screenTimeOffset
        self.lcd.screen.fill(colourBlack)

   def progressScreen(self):
       # subroutine
       # timeout = 5
       # sleep(1)
       # update progressbar with + 20%
       # update screen and blit progress
       # pygame.draw.rect(...)
       self.lcd.screen.fill(colourBlack)
       pygame.display.update()
       # load picture and show ...
       self.state = "initial"
       icon = installPathImgBig + "easteregg.png"
       logo = pygame.image.load(icon).convert()
       self.w = logo.get_width() - 30
       self.h = logo.get_height() - 30
       logo = pygame.transform.scale(logo, (self.w,self.h))
       self.lcd.screen.blit(logo, (0, 0))
       textAnchorX = 310
       textAnchorY = 5
       textYoffset = 40
       text_surface = font.render("Pause ...", True, colourWhite)
       self.lcd.screen.blit(text_surface, (textAnchorX, textAnchorY))
       pygame.display.update()
       # wait
       time.sleep(timeout)

   def screen1(self):
       pass

   def screen2(self):
       pass

   def screen3(self, state):
       self.state = state
       icon = installPathImgBig + "easteregg.png"
       logo = pygame.image.load(icon).convert()
       self.w = logo.get_width() - 30
       self.h = logo.get_height() - 30
       logo = pygame.transform.scale(logo, (self.w,self.h))
       self.lcd.screen.blit(logo, (0, 0))
       textAnchorX = 310
       textAnchorY = 5
       textYoffset = 40
       text_surface = font.render("Pause ...", True, colourWhite)
       self.lcd.screen.blit(text_surface, (textAnchorX, textAnchorY))

   def run(self):
       self.updateScreen(self.screen3, "screen3")

if __name__ == '__main__':
    p_obj = PygameWeather()
    # ...
