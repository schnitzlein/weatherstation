import datetime
import time
import json
from Display import PyLcd as lcd_screen
import pygame
import logging

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
        self.weather_com_result = {}
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

    def callServer(self):
        pass
