import datetime
import time
import string
import json
from Display import PyLcd as lcd_screen
import pygame
import logging
import requests

class PygameWeather(object):
    """This class uses pygame and show on console Weatherinformation graphicaly"""

    def __init__(self):
        #TODO: add config file, to configure outside, if confifile present read data... set values
        self.updateRate = 3600     # seconds, for server call # update interval
        self.betweenTime = 20      # accumulated seconds screens/program are running, if matching or greate updateRate ... update #FIXME: prevent Bufferoverflow
        self.screenTimeOffset = 20 # the time the screens are shown
        # more vars
        self.states = ["start", "initial", "screen1", "screen2", "screen3", "network"]
        self.state = "start"
        self.weather_data = {}
        self.h = 0
        self.w = 0

        # today weather variables
        self.icon_name = ""
        self.icon_filename = ""
        self.currTempFeeling = ""
        self.currDayTempMax = ""
        self.currDayTempMin = ""
        self.current_summary = ""
        self.daily_summary = ""
        self.apparentTemperatureHigh = ""
        self.apparentTemperatureLow = ""
        self.apparentTemperatureHighTime = ""
        self.apparentTemperatureLowTime = ""
        # optional vars
        self.windSpeed = ""
        self.currWind = ""
        self.currPress = ""
        self.uv = ""
        self.todayDesc = ""
        self.humid = ""

        # icons to show weather
        self.list_of_icons = ['clear-day', 'clear-night', 'rain', 'snow', 'sleet', 'wind', 'fog', 'cloudy', 'partly-cloudy-day', 'partly-cloudy-night', 'hail', 'thunderstorm', 'tornado']

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
        # Constants
        pygame.mouse.set_visible(False)
        self.fontpath = pygame.font.match_font('dejavusansmono')
        self.font = pygame.font.Font(self.fontpath, 36)
        self.fontS2 = pygame.font.Font(self.fontpath, 28)
        self.fontSm = pygame.font.Font(self.fontpath, 18)
        self.colourWhite = (255, 255, 255)
        self.colourBlack = (0, 0, 0)
        #TODO: add auto installer, auto config, with python setup tools, and read config ...
        # installPath is like "/home/username/installfolder/img/big" ... ".../small"
        self.installPathImgBig = "/home/pi/weatherstation/img/big/"
        self.installPathImgSmall = "/home/pi/weatherstation/img/small/"
        # Constants

    # see a clock with secounds, just call it in loop or as many times as you need it, after it clear the screen !
    def showClock(self):
        #TODO:show in random position, activate if motion sensor register motion
        # clear screen and update
        self.lcd.screen.fill(self.colourBlack)
        pygame.display.update()
        # show the clock @ (10,260), uodate the screen and wait 1 second
        updated = time.strftime("%H:%M:%S")
        text_surface = self.fontS2.render(updated, True, self.colourWhite)
        self.lcd.screen.blit(text_surface, (10, 260))
        pygame.display.update()
        time.sleep(1)

    def parseDataFromServer(self, data):
        JsonKeyError = False
        if 'alerts' in data:
            self.alerts = data['alerts']
        if 'currently' in data:
            if 'apparentTemperature' in data['currently']:
                self.currTempFeeling = data['currently']['apparentTemperature']
            else:
                JsonKeyError = True
                logging.debug("Trace: data['currently']['apparentTemperature'] not found")
            if 'icon' in data['currently']:
                self.icon_name = data['currently']['icon']:
                if self.icon_name not in self.list_of_icons:
                    JsonKeyError = True
                    logging.debug("Trace: data['currently']['icon'] not found or not in list, was: {}".format(self.icon_name))
            if 'summary' in data['currently']:
                self.current_summary = data['currently']['summary']
            else:
                JsonKeyError = True
                logging.debug("Trace: data['currently']['summary'] not found or not in list")
        else:
            JsonKeyError = True
            logging.debug("Trace: data['currently'] all data not found")
        if 'daily' in data:
            if 'summary' in data['daily']:
                self.daily_summary = data['daily']['summary']
            else:
                JsonKeyError = True
                logging.debug("Trace: data['daily']['summary'] not found or not in list")
            if 'apparentTemperatureHigh' in data['daily']:
                self.currDayTempMax = data['daily']['apparentTemperatureHigh']
            else:
                JsonKeyError = True
                logging.debug("Trace: data['daily']['apparentTemperatureHigh'] not found or not in list")
            if 'apparentTemperatureLow' in data['daily']:
                self.currDayTempLow = data['daily']['apparentTemperatureLow']
            else:
                JsonKeyError = True
                logging.debug("Trace: data['daily']['apparentTemperatureLow'] not found or not in list")
            if 'apparentTemperatureHighTime' in data['daily']:
                self.currDayTempMaxTime = datetime.datetime.fromtimestamp( data['daily']['apparentTemperatureHighTime'] ) + datetime.timedelta(hours=2) ) # Zeit wann am waermsten
            else:
                JsonKeyError = True
                logging.debug("Trace: data['daily']['apparentTemperatureHighTime'] not found or not in list")
            if 'apparentTemperatureLowTime' in data['daily']:
                self.currDayTempLowTime = datetime.datetime.fromtimestamp( data['daily']['apparentTemperatureLowTime'] ) + datetime.timedelta(hours=2) ) # Zeit wann am kaeltesten am TAG
            else:
                JsonKeyError = True
                logging.debug("Trace: data['daily']['apparentTemperatureLowTime'] not found or not in list")
        else:
            JsonKeyError = True
            logging.debug("Trace: data['daily'] all data not found")
        return JsonKeyError

    def callServer(self):
        # TODO: test connection to internet, simple call server
        def getDataFromServer():
            data = {}
            response = requests.get('https://api.forecast.io/forecast/500e8abf656226b5076cd1886f87f8b2/51.7781718,14.2472211?units=si')
            if response.status_code == 200:
                data = response.json()
                if data != {}:
                    ret = self.parseDataFromServer(data)
                    if ret == False:
                        logging.info("Calling server successful")
                    else:
                        logging.info("While server calling broking data")
                else:
                    logging.warn("No Server Data!")
                    #TODO: Handle backup Server
            else:
                # server connection broken, or no internet, or ...
                logging.info("Calling server failure: {}".format(response.status_code)) #TODO: Handle backup Server
                # call backup server ... or keep old data ... or measure from local
            self.state = "screen1"
            return data

        if self.state == "start":
            self.progressScreen()
        if self.state == "initial":
            self.weather_data = getDataFromServer()
        if self.betweenTime >= self.updateRate:
            self.betweenTime = 0
            self.state = "network"
            logging.info(format(self.updateRate) + " seconds is over, Calling server...")
            self.weather_data = getDataFromServer()

    def iconMapping(self, icon_name):
        self.icon_filename = 'na.png'
        if icon_name == 'clear-day':
            self.icon_filename = '32.png'
        elif icon_name == 'clear-night':
            self.icon_filename = '31.png'
        elif icon_name == 'rain':
            self.icon_filename = '02.png'
        elif icon_name == 'snow':
            self.icon_filename = '16.png'
        elif icon_name == 'sleet':
            self.icon_filename = '08.png'
        elif icon_name == 'wind':
            self.icon_filename = '23.png'
        elif icon_name == 'fog':
            self.icon_filename = '20.png'
        elif icon_name == 'cloudy':
            self.icon_filename = '28.png'
        elif icon_name == 'partly-cloudy-day':
            self.icon_filename = '30.png'
        elif icon_name == 'partly-cloudy-night':
            self.icon_filename = '29.png'
        elif icon_name == 'hail':
            self.icon_filename = 'hail_icon.png'
        elif icon_name == 'thunderstorm':
            self.icon_filename = '04.png'
        elif icon_name == 'tornado':
            self.icon_filename = 'tornado_icon.png'
        elif icon_name == '':
            self.icon_filename = ''
        else:
            logging.warn("The icon was not found.")

    def updateScreen(self, action):
        self.lcd.screen.fill(self.colourBlack)
        pygame.display.update()
        ############ screen specifica begin #############
        try:
           action()
        except Exception as e:
           logging.error(e)
        ############ screen specifica end ###############
        # update screen
        pygame.display.update()
        # wait
        time.sleep(self.screenTimeOffset)
        self.betweenTime += self.screenTimeOffset
        # blank the screen after screenTimeOffset
        self.lcd.screen.fill(self.colourBlack)

    def progressScreen(self):
       # subroutine
       # timeout = 5
       # sleep(1)
       # update progressbar with + 20%
       # update screen and blit progress
       # pygame.draw.rect(...)
       self.lcd.screen.fill(self.colourBlack)
       pygame.display.update()
       # load picture and show ...
       self.state = "initial"
       try:
           icon = self.installPathImgBig + "easteregg_2.png"
           logo = pygame.image.load(icon).convert()
           self.w = logo.get_width() - 176
           self.h = logo.get_height() - 49
           logo = pygame.transform.scale(logo, (self.w,self.h))
           self.lcd.screen.blit(logo, (0, 0))
           textAnchorX = 310
           textAnchorY = 5
           text_surface = self.font.render("Loading ...", True, self.colourWhite)
           self.lcd.screen.blit(text_surface, (textAnchorX, textAnchorY))
           pygame.display.update()
           time.sleep(self.screenTimeOffset)
       except Exception as e:
           logging.warn(e)
       # wait
       #time.sleep(timeout)

    def screen1(self):
       self.state = "screen3"
       self.iconMapping(self.icon_name)
       icon = self.installPathImgBig + self.icon_filename
       logo = pygame.image.load(icon).convert()
       self.w = logo.get_width() - 50
       self.h = logo.get_height() - 50
       logo = pygame.transform.scale(logo, (self.w,self.h))
       lcd.screen.blit(logo, (0, 0))
       # set the anchor for the current weather data text
       textAnchorX = 260 # 310 war ok bei 328 Bild
       textAnchorY = 5
       textYoffset = 40
       # add current weather data text artifacts to the screen
       text_surface = self.font.render(self.currTempFeeling, True, self.colourWhite)
       lcd.screen.blit(text_surface, (textAnchorX, textAnchorY))
       textAnchorY+=textYoffset
       text_surface = self.font.render(self.currDayTempMax, True, self.colourWhite)
       lcd.screen.blit(text_surface, (textAnchorX, textAnchorY))
       textAnchorY+=textYoffset
       text_surface = self.font.render(self.currDayTempMin, True, self.colourWhite)
       lcd.screen.blit(text_surface, (textAnchorX, textAnchorY))
       textAnchorY+=textYoffset
       text_surface = self.font.render(self.current_summary, True, self.colourWhite)
       lcd.screen.blit(text_surface, (textAnchorX, textAnchorY))
       textAnchorY+=textYoffset
       if self.alerts:
           if 'description' in self.alerts:
               text_surface = self.font.render(self.alerts['description'], True, self.colourWhite)
               lcd.screen.blit(text_surface, (textAnchorX, textAnchorY))

    def screen2(self):
       self.state = "screen3"
       # set X axis text anchor for the forecast text
       textAnchorX = 0
       textXoffset = 75 #100
       textAnchorY = 10
       #pygame.draw.line(lcd.screen.get_surface(), self.colourWhite, (50,10), (450,10),4)

       # add summy of the values in one row
       for i in range(0,5):
         text_surface = self.fontS2.render(self.forecastDesc[i], True, self.colourWhite)
         lcd.screen.blit(text_surface, (textAnchorX, textAnchorY))
         textAnchorY+=textYoffset

       textAnchorX+=80
       textXoffset = 100

       # add each days forecast text + icon
       for i in range(1, 5):
           textAnchorY = 10
           text_surface = self.fontS2.render(self.forecastDays[i], True, self.colourWhite)
           lcd.screen.blit(text_surface, (textAnchorX, textAnchorY))
           textAnchorY+=textYoffset
           text_surface = self.fontS2.render(self.forecaseHighs[i], True, self.colourWhite)
           lcd.screen.blit(text_surface, (textAnchorX, textAnchorY))
           textAnchorY+=textYoffset
           text_surface = self.fontS2.render(self.forecaseLows[i], True, self.colourWhite)
           lcd.screen.blit(text_surface, (textAnchorX, textAnchorY))
           textAnchorY+=textYoffset
           #text_surface = self.fontS2.render(self.forecastPrecips[i], True, self.colourWhite)
           #lcd.screen.blit(text_surface, (textAnchorX, textAnchorY))
           #textAnchorY+=textYoffset
           #text_surface = self.fontS2.render(self.forecastWinds[i], True, self.colourWhite)
           #lcd.screen.blit(text_surface, (textAnchorX, textAnchorY))
           #textAnchorX+=textXoffset
           try:
             logo = pygame.image.load(self.forecastIcons[i]).convert()
             self.w = logo.get_width()
             self.h = logo.get_height()
             logo = pygame.transform.scale(logo, (self.w,self.h))
             lcd.screen.blit(logo, (textAnchorX, textAnchorY))
             textAnchorX+=textXoffset
           except pygame.error as message:
             #logging.warn(self.forecastIcons) # to see which icons are missing or is empty json
             #str = "err width: {}" .format(self.w)
             #str = str + " height: {}" .format(h)
             #logging.warn(str)
             logging.warn(message)
             textAnchorX+=textXoffset

       # today desc under the table
       textAnchorY = 220
       textAnchorX = 10
       text_surface = self.fontS2.render(self.todayDesc, True, self.colourWhite)
       lcd.screen.blit(text_surface, (textAnchorX, textAnchorY))
       # update when information
       textAnchorY+=textYoffset
       updated = time.strftime("%H:%M") #time.strftime("%H:%M:%S")
       text_surface = self.fontS2.render(updated, True, self.colourWhite)
       lcd.screen.blit(text_surface, (textAnchorX, textAnchorY))

    def screen3(self):
       self.state = "screen1"
       icon = self.installPathImgBig + "easteregg.png"
       logo = pygame.image.load(icon).convert()
       self.w = logo.get_width() - 30
       self.h = logo.get_height() - 30
       logo = pygame.transform.scale(logo, (self.w,self.h))
       self.lcd.screen.blit(logo, (0, 0))
       textAnchorX = 310
       textAnchorY = 5
       textYoffset = 40
       text_surface = self.font.render("Pause ...", True, self.colourWhite)
       self.lcd.screen.blit(text_surface, (textAnchorX, textAnchorY))

    def run(self):
        #self.updateScreen(self.screen3, "screen3")
        quit = False
        while not quit:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                   sys.exit()
                   quit = True
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                   quit = True
                   logging.info("ESC Key was pressed")

                if quit is True:
                   print("Escape Button was pressed.")
                   return
            # show screen
            self.progressScreen()
            self.showClock()
            if self.betweenTime >= self.updateRate:
              self.betweenTime = 0
              self.state = "network"
            # todo: make depending from state ... TODO: asynchronous download + blit screen if network
            self.updateScreen(self.screen1())


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG, filename="logfile", filemode="a+", format="%(asctime)s %(message)s")
    try:
       PygameWeather().run()
    except Exception as e:
       logging.error(e)
