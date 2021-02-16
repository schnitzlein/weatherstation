# outside do: curl https://api.forecast.io/forecast/500e8abf656226b5076cd1886f87f8b2/51.7781718,14.2472211?units=si > mylog.json
# possible icons are:
# clear-day, clear-night, rain, snow, sleet, wind, fog, cloudy, partly-cloudy-day, partly-cloudy-night, hail, thunderstorm, tornado
# source: https://developer.forecast.io/docs/v2#forecast_call
# online api, with stad login: https://developer.forecast.io/
import time
import json
import string
import urllib2
import pprint
from Bild import PyLcd as d
import pygame
import logging
pp = pprint.PrettyPrinter(indent=4)

#mydict = []
#with open('mylog.json', 'r') as inf:
#  mydict = eval(inf.read())
  
#pp.pprint(mydict['currently'])

# load image from mydict['currently']['icon']
# and before copy images to folder where .py file is and rename them to icon names
# do things better with ['currently']['summary'] evalution...


# Create an instance of the PyLcd class
lcd = d()

# Constants 
pygame.mouse.set_visible(False)
# colours
colourWhite = (255, 255, 255)
colourBlack = (0, 0, 0)

# font
fontpath = pygame.font.match_font('dejavusansmono')
# set up 3 sizes
font = pygame.font.Font(fontpath, 36)
fontS2 = pygame.font.Font(fontpath, 28)
fontSm = pygame.font.Font(fontpath, 18)

class PygameWeather(object): 
    """This class uses pygame and show on console Weatherinformation graphicaly"""
    
    # class variable not shared by all instances    
    updateRate = 21600     # seconds, for server call # update interval
    betweenTime = 20      # seconds, befor screen switching (pause time) obsolet
    screenTimeOffset = 20 # same Time like betweenTime, was intentionally the time the screens are show 
    # more vars
    states = ["initial", "screen1", "screen2", "screen3", "network"]
    state = "initial"
    weather_com_result = {}
    h = 0
    w = 0
    
    # today variables
    today = ""
    windSpeed = ""
    currWind = ""
    currTemp = ""
    currTempFeeling = ""
    currPress = ""
    uv = ""
    todayDesc = ""
    humid = ""
    
    # forecast variables
    forecastDesc = ""
    # forecast data
    forecastDays = {}
    forecaseHighs = {}
    forecaseLows = {}
    forecastPrecips = {}
    forecastWinds = {}
    forecastIcons = {}

     def run(self):
       #global forecastIcons
       quit = False
       while not quit:
                for event in pygame.event.get():
                    if event.type == QUIT: #sth wrong here if pygame.QUIT
                      sys.exit()
                      quit = True
                    elif event.type == KEYDOWN and event.key == K_ESCAPE:
                      quit = True
                      logging.info("ESC Key was pressed")  
                   
                    if quit is True:
                      print "Escape Button was pressed."
                      return
               
                # retrieve data from weather.com and keep old values if no connection
                if self.state == "initial":
                  self.weather_com_result = urllib2.urlopen('https://api.forecast.io/forecast/500e8abf656226b5076cd1886f87f8b2/51.0687216,13.6849743?units=si')
                  self.state = "screen1"
                  # if weather_com_result is empty check TODO: FIXME
                
                if self.betweenTime >= self.updateRate:
                  self.betweenTime = 0
                  self.state = "network"
                  logging.info(format(self.updateRate) + " seconds is over, Calling server...")
                  self.weather_com_result = urllib2.urlopen('https://api.forecast.io/forecast/500e8abf656226b5076cd1886f87f8b2/51.0687216,13.6849743?units=si')
                  logging.info("Calling server successful")
                  self.state = "screen1"
                  # if weather_com_result is empty check TODO: FIXME
                  # run alternative data
                #
                
                # screen3 beginn
                if (time.strftime("%H:%M") >= '19:00' and time.strftime("%H:%M") <= '19:30') or (time.strftime("%d/%m") == '05/12'):
                    self.state = "screen3"
                    lcd.screen.fill(colourBlack)
                    icon = installPathImgBig + "easteregg.png"
                    logo = pygame.image.load(icon).convert()
                    self.w = logo.get_width() - 30
                    self.h = logo.get_height() - 30
                    logo = pygame.transform.scale(logo, (self.w,self.h)) 
                    lcd.screen.blit(logo, (0, 0))
                    textAnchorX = 310 
                    textAnchorY = 5
                    textYoffset = 40
                    text_surface = font.render("Pause ...", True, colourWhite)
                    lcd.screen.blit(text_surface, (textAnchorX, textAnchorY))
                    pygame.display.update()
                    time.sleep(self.screenTimeOffset)
                    self.betweenTime += self.screenTimeOffset
                # screen3 ends
                
                
                # extract current data for today
                self.today = ""
                self.windSpeed = self.weather_com_result['currently']['windSpeed']
                self.currWind = "{}km/h ".format(self.windSpeed)
                self.currTemp = self.weather_com_result['currently']['temperature'] + u'\N{DEGREE SIGN}' + "C"
                self.currPress = self.weather_com_result['currently']['pressure'] + "mb"
                self.uv = "Ozone {}".format(self.weather_com_result['currently']['ozone'])
                self.humid = "Hum {}%".format(self.weather_com_result['currently']['humidity'])
                self.currTempFeeling = "(" + self.weather_com_result['currently']['apparentTemperature'] + u'\N{DEGREE SIGN}' + "C)"
                self.todayDesc = "It is " + self.weather_com_result['currently']['summary'].lower() + " today."
 
                # summary and description of forecast data                
                self.forecastDesc = ["Day", "Max", "Min", "   ", "   "] # forecastDesc = ["Day", "Max", "Min", "Hum", "Kmh"]
                
                
                for i in range(0, 5):
                    if not(self.weather_com_result['forecasts'][i]):
                        break
                        
                    self.forecastDays[i] = ""
                    self.forecaseHighs[i] = "" + u'\N{DEGREE SIGN}' + "C"
                    self.forecaseLows[i] = "" + u'\N{DEGREE SIGN}' + "C"
                    self.forecastPrecips[i] = "" + "%"
                    self.forecastWinds[i] = ""
                    self.forecastIcons[i] = ""
                
                        
                # 1. screen, dayInformation
                # blank the screen
                lcd.screen.fill(colourBlack)
 
                # Render the weather logo at 0,0
                icon = installPathImgBig + (data['daily']['data'][0]['icon']) + ".png"
                #logo = pygame.image.load(icon).convert()
                #self.w = logo.get_width() - 50
                #self.h = logo.get_height() - 50
                #logo = pygame.transform.scale(logo, (self.w,self.h)) 
                #lcd.screen.blit(logo, (0, 0))
 
                # set the anchor for the current weather data text
                textAnchorX = 260 # 310 war ok bei 328 Bild
                textAnchorY = 5
                textYoffset = 40
 
                # add current weather data text artifacts to the screen
                text_surface = font.render(self.today, True, colourWhite)
                lcd.screen.blit(text_surface, (textAnchorX, textAnchorY))
                textAnchorY+=textYoffset
                text_surface = font.render(self.currTemp, True, colourWhite)
                lcd.screen.blit(text_surface, (textAnchorX, textAnchorY))
                textAnchorY+=textYoffset
                text_surface = font.render(self.currTempFeeling, True, colourWhite)
                lcd.screen.blit(text_surface, (textAnchorX, textAnchorY))
                textAnchorY+=textYoffset
                text_surface = font.render(self.currWind, True, colourWhite)
                lcd.screen.blit(text_surface, (textAnchorX, textAnchorY))
                textAnchorY+=textYoffset
                text_surface = font.render(self.currPress, True, colourWhite)
                lcd.screen.blit(text_surface, (textAnchorX, textAnchorY))
                textAnchorY+=textYoffset
                text_surface = font.render(self.uv, True, colourWhite)
                lcd.screen.blit(text_surface, (textAnchorX, textAnchorY))
                textAnchorY+=textYoffset
                text_surface = font.render(self.humid, True, colourWhite)
                lcd.screen.blit(text_surface, (textAnchorX, textAnchorY))
 
                
                # wait between screen changes screenTimeOffset alias first betweenTime
                pygame.display.update()
                
                # wait
                time.sleep(self.screenTimeOffset)
                self.betweenTime += self.screenTimeOffset
               
                # blank the screen after screenTimeOffset
                lcd.screen.fill(colourBlack)
                pygame.display.update()
                
                
                # 2. screen
                # state = screen2
                # blank the screen
                lcd.screen.fill(colourBlack)
                pygame.display.update()
                
                # set X axis text anchor for the forecast text
                textAnchorX = 0
                textXoffset = 75 #100
                textAnchorY = 10
                #pygame.draw.line(lcd.screen.get_surface(), colourWhite, (50,10), (450,10),4)

                # add summy of the values in one row
                for i in range(0,5):
                  text_surface = fontS2.render(self.forecastDesc[i], True, colourWhite)
                  lcd.screen.blit(text_surface, (textAnchorX, textAnchorY))
                  textAnchorY+=textYoffset
                  
                textAnchorX+=80
                textXoffset = 100
 
                # add each days forecast text + icon
                for i in range(1, 5):
                    textAnchorY = 10
                    text_surface = fontS2.render(self.forecastDays[i], True, colourWhite)
                    lcd.screen.blit(text_surface, (textAnchorX, textAnchorY))
                    textAnchorY+=textYoffset
                    text_surface = fontS2.render(self.forecaseHighs[i], True, colourWhite)
                    lcd.screen.blit(text_surface, (textAnchorX, textAnchorY))
                    textAnchorY+=textYoffset
                    text_surface = fontS2.render(self.forecaseLows[i], True, colourWhite)
                    lcd.screen.blit(text_surface, (textAnchorX, textAnchorY))
                    textAnchorY+=textYoffset
                    #text_surface = fontS2.render(self.forecastPrecips[i], True, colourWhite)
                    #lcd.screen.blit(text_surface, (textAnchorX, textAnchorY))
                    #textAnchorY+=textYoffset
                    #text_surface = fontS2.render(self.forecastWinds[i], True, colourWhite)
                    #lcd.screen.blit(text_surface, (textAnchorX, textAnchorY))
                    #textAnchorX+=textXoffset
                    try:
                      #logo = pygame.image.load(self.forecastIcons[i]).convert()
                      #self.w = logo.get_width()
                      #self.h = logo.get_height()
                      #logo = pygame.transform.scale(logo, (self.w,self.h)) 
                      #lcd.screen.blit(logo, (textAnchorX, textAnchorY))
                      #textAnchorX+=textXoffset
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
                text_surface = fontS2.render(self.todayDesc, True, colourWhite)
                lcd.screen.blit(text_surface, (textAnchorX, textAnchorY))
                
                # update when information
                textAnchorY+=textYoffset
                updated = time.strftime("%H:%M") #time.strftime("%H:%M:%S")
                text_surface = fontS2.render(updated, True, colourWhite)
                lcd.screen.blit(text_surface, (textAnchorX, textAnchorY))
                
                # update screen with forecast text
                pygame.display.update()
                
                # wait
                time.sleep(self.screenTimeOffset)
                self.betweenTime += self.screenTimeOffset
               
                # blank the screen after screenTimeOffset
                lcd.screen.fill(colourBlack)
                pygame.display.update()
               
                # Wait
                #time.sleep(updateRate)
                
                #i = 0                
                #while i < screenTimeOffset:
                  #global betweenTime
                  #time.sleep(1)
                  #i = i + 1
                  #lcd.screen.fill(colourBlack) time.sleep(1)
                  #pygame.display.update()
                  #self.showClock()
                  #pygame.display.update() 
                  
                  
                #betweenTime+=screenTimeOffset
                

if __name__ == '__main__':
  logging.basicConfig(level=logging.DEBUG, filename="logfile", filemode="a+", format="%(asctime)s %(message)s")
  try: 
    PygameWeather().run()
  except Exception as e:
    #print "\n except: %s" % (e,)
    logging.warn(e)
    
    
    
    
    
    
# request server Data
#response = urllib2.urlopen('https://api.forecast.io/forecast/500e8abf656226b5076cd1886f87f8b2/51.0687216,13.6849743?units=si')
#data = json.load(response)   
#print data['currently']

#dump server data in result.json file
#with open('result.json', 'w') as fp:
#    json.dump(data, fp)



#currTemp = data['currently']['temperature']
#feelTemp = data['currently']['apparentTemperature']
#humidity = data['currently']['humidity'] # * 100; to str; + "%"
#wind = data['currently']['windSpeed'] # to str; + km/h
#pressure = data['currently']['pressure'] # to str; + "mbar"
#ozone = data['currently']['ozone']
#icon = data['currently']['icon']
#time_in_ms = data['currently']['time']
#summary = data['currently']['summary']
#precipType = data['currently']['precipType']


#data['latitude']
#data['longitude']

#daily_max = data['daily']['data'][0]['temperatureMax']
#daily_min = data['daily']['data'][0]['temperatureMin']
#daily_sum = data['daily']['data'][0]['summary']
#daily_icon = data['daily']['data'][0]['icon']
#daily_view_range = data['daily']['data'][0]['visibility']

#for i in range(0,8):
#   pp.pprint(int(mydict['daily']['data'][i]['temperatureMax']))


# alternative zur alternative vorher requets installieren
# http://docs.python-requests.org/en/latest/user/install/#install
"""
import requests
r = requests.get('https://api.forecast.io/forecast/500e8abf656226b5076cd1886f87f8b2/51.7781718,14.2472211?units=si')
r.json()

#oder

r.text
"""


