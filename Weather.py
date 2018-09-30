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
        self.updateRate = 7200     # seconds, for server call # update interval
        self.betweenTime = 20      # accumulated seconds screens/program are running, if matching or greate updateRate ... update #FIXME: prevent Bufferoverflow
        self.screenTimeOffset = 20 # the time the screens are shown
        # more vars
        self.states = ["start", "initial", "screen1", "screen2", "screen3", "network"]
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

    def callServer(self):
        # TODO: test connection to internet, simple call server
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
                logging.info("Calling server failure") #TODO: Handle backup Server
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
        self.lcd.screen.fill(self.colourBlack)
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
           self.w = logo.get_width() - 256
           self.h = logo.get_height() - 69
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
       # Render the weather logo at 0,0
       icon = self.installPathImgBig + (self.weather_com_result['current_conditions']['icon']) + ".png"
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
       text_surface = self.font.render(self.today, True, self.colourWhite)
       lcd.screen.blit(text_surface, (textAnchorX, textAnchorY))
       textAnchorY+=textYoffset
       text_surface = self.font.render(self.currTemp, True, self.colourWhite)
       lcd.screen.blit(text_surface, (textAnchorX, textAnchorY))
       textAnchorY+=textYoffset
       text_surface = self.font.render(self.currTempFeeling, True, self.colourWhite)
       lcd.screen.blit(text_surface, (textAnchorX, textAnchorY))
       textAnchorY+=textYoffset
       text_surface = self.font.render(self.currWind, True, self.colourWhite)
       lcd.screen.blit(text_surface, (textAnchorX, textAnchorY))
       textAnchorY+=textYoffset
       text_surface = self.font.render(self.currPress, True, self.colourWhite)
       lcd.screen.blit(text_surface, (textAnchorX, textAnchorY))
       textAnchorY+=textYoffset
       text_surface = self.font.render(self.uv, True, self.colourWhite)
       lcd.screen.blit(text_surface, (textAnchorX, textAnchorY))
       textAnchorY+=textYoffset
       text_surface = self.font.render(self.humid, True, self.colourWhite)
       lcd.screen.blit(text_surface, (textAnchorX, textAnchorY))

    def screen2(self):
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

    def screen3(self, next_state):
       self.state = next_state
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
            #  self.updateScreen(self.screen1)
            self.updateScreen(self.screen3("state1"))


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG, filename="logfile", filemode="a+", format="%(asctime)s %(message)s")
    try:
       PygameWeather().run()
    except Exception as e:
       logging.error(e)
