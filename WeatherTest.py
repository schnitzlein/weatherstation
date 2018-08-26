import datetime
import time
import json
import string
#import urllib2
from Display import PyLcd as lcd_screen
import pygame
import logging
import pprint
pp = pprint.PrettyPrinter(indent=4)

# https://darksky.net/dev/docs
# http://greanwhichmeantime.com/time-zone/europe/european-union/germany/

mydict = []
with open('mylog.json', 'r') as inf:
  mydict = eval(inf.read())

pp.pprint(mydict['currently'])
pp.pprint(mydict['hourly']['summary'])

germany_offset = mydict['offset'] # from server, can be hardcoded it is 2 hours, seen greanwhichmeantime

#pp.pprint(len(mydict['hourly']['data']))
#for i in mydict['hourly']['data']:
#    print(i['apparentTemperature'])

pp.pprint(mydict['daily']['summary'])
pp.pprint(mydict['daily']['icon'])
for i in mydict['daily']['data']:
    print(i['apparentTemperatureHigh'])
    print( datetime.datetime.fromtimestamp( i['apparentTemperatureHighTime'] ) + datetime.timedelta(hours=2) ) # Zeit wann am waermsten
    print( datetime.datetime.fromtimestamp( i['apparentTemperatureLowTime'] ) + datetime.timedelta(hours=2) ) # Zeit wann am kaeltesten am TAG, Rest ist deprecated
    print(i['apparentTemperatureLow'])

# TODO: cast forecastIcons and current Icons mapping
# possible mapping ... TODO
def iconMapping(icon_name):
    icon_filename = 'na.png'
    if icon_name == 'clear-day':
        icon_filename = '32.png'

# clear-day, clear-night, rain, snow, sleet, wind, fog, cloudy, partly-cloudy-day, partly-cloudy-night, hail, thunderstorm, tornado
# clear-day: 32.png
# clear-night: 31.png maybe a sky with stars ... TODO
# rain: 02.png
# snow: 16.png
# sleet: 08.png
# wind: 23.png
# fog: 20.png
# cloudy: 28.png
# partly-cloudy-day: 30.png
# partly-cloudy-night: 29.png
# hail: hail_icon.png
# thunderstorm: 04.png
# tornado: tornado_icon.png

# TODO: make a progress bar loading and checking data from server, init screen: easteregg_2.png show for at least 5 secs
