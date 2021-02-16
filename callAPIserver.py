import sys
#import pygame
import time
#import string
#import logging
import json
#import urllib
import requests
import pprint
pp = pprint.PrettyPrinter(indent=4)

datadict = {}


def callServer( ):
    """
    returns dictionary with response from weather API Server
    if response HTTP Status != 200 returns None
    """

    url = 'https://api.forecast.io/forecast/<API-KEY>/50.0,13.0?units=si' # '?lang=de'
    params = {}
    # params = dict(foo='', foo2='')
    resp = requests.get(url=url, params=params)
    if (resp.status_code == 200):
        data = resp.json()
        pp.pprint(data)
        return data
    return None


def test():
#while True:
    retVal = callServer()
    #print(retVal)

    # extract current data for today
    today = ""
    windSpeed = retVal['currently']['windSpeed']
    currWind = "{} km/h ".format(windSpeed)
    currTemp = str( retVal['currently']['temperature'] ) + u' \N{DEGREE SIGN}' + "C"
    currPress = str( retVal['currently']['pressure'] ) + " mb"
    uv = "Ozone {}".format(retVal['currently']['ozone'])
    humid = "Hum {}%".format(retVal['currently']['humidity'])
    currTempFeeling = "(" + str( retVal['currently']['apparentTemperature'] ) + u' \N{DEGREE SIGN}' + "C)"
    todayDesc = "It is " + str( retVal['currently']['summary'].lower() ) + " today."

    print(today)
    print(windSpeed)
    print(currWind)
    print(currTemp)
    print(currPress)
    print(uv)
    print(humid)
    print(currTempFeeling)
    print(todayDesc)

    #time.sleep(30)
    sys.exit(0)

test()
