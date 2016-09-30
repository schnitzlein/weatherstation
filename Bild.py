import os, syslog
import pygame
import time
import pywapi
import string
import logging
 
# *** Not to be used for commercial use without permission!
# if you want to buy the icons for commercial use please send me a note - http://vclouds.deviantart.com/ ***
#
# Credit goes to Karol Tomala for Python GUI in Linux frame buffer: http://www.karoltomala.com/blog/?p=679 
# Credit goes to Jamie Jackson http://blog.jacobean.net/?p=1016 for his nice Tutorial and great Parts of his Code, which i re-use.
# Credit goes to Merlin the Red for his great pictures: http://vclouds.deviantart.com/art/plain-weather-icons-157162192 , which i use.
#  ^-> I use his svg files and bring them to ~ 328x328 px
#
# I modify the original code for my 4 inch display and that it work in two 'screens'. First shows the currentday, Secound shows the forecast.
# Further I add some Code and play around with this and that.
# Now there are two img sizes big and small in seperate folders.

# installPath is like "/home/username/installfolder/img/big" ... ".../small"
installPathImgBig = "/home/pi/weatherstation/img/big/"
installPathImgSmall = "/home/pi/weatherstation/img/small/"
 
# location for Cottbus, Brandenburg, Germany on weather.com
weatherDotComLocationCode = 'GMXX0171'

 
class PyLcd :
    screen = None;
    colourBlack = (0, 0, 0)
 
    def __init__(self):
        "Ininitializes a new pygame screen using the framebuffer"
        # Based on "Python GUI in Linux frame buffer"
        # http://www.karoltomala.com/blog/?p=679
        disp_no = os.getenv("DISPLAY")
        if disp_no:
            print "I'm running under X display = {0}".format(disp_no)
 
        os.putenv('SDL_FBDEV', '/dev/fb1')
 
        # Select frame buffer driver
        # Make sure that SDL_VIDEODRIVER is set
        driver = 'fbcon'
        if not os.getenv('SDL_VIDEODRIVER'):
            os.putenv('SDL_VIDEODRIVER', driver)
        try:
            pygame.display.init()
        except Exception as e:
           print "exception: %s" % (e,)
        except pygame.error:
            print 'Driver: {0} failed.'.format(driver)
            exit(0)
 
        size = (pygame.display.Info().current_w, pygame.display.Info().current_h)
        self.screen = pygame.display.set_mode(size, pygame.FULLSCREEN)
        # Clear the screen to start
        self.screen.fill((0, 0, 0))
        # Initialise font support
        pygame.font.init()
        # Render the screen
        pygame.display.update()
 
    def __del__(self):
        logging.info("Ende.")
        pygame.display.quit()
        #print "Destructor pygame display shuts down."
 
# Create an instance of the PyLcd class
lcd = PyLcd()

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
# Constants 

class PygameWeather(object): 
    """This class uses pygame and show on console Weatherinformation graphicaly"""
    
    # class variable not shared by all instances    
    updateRate = 3600     # seconds, for server call # update interval
    betweenTime = 20      # seconds, befor screen switching (pause time) obsolet
    screenTimeOffset = 20 # same Time like betweenTime, was intentionally the time the screens are show 
    # more vars
    states = ["initial", "screen1", "screen2", "network"]
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
    
    #TODO: add all local vars here add self. in front of all local vars
    
    # def evaluateInformation() # put the var assignment here
    # def updateScreen1         # put graphical change for screen1 here
    # def updateScreen2         # put graphical change for screen2 here
    
    # call weather server, if no connection or error return old data
    def callServer( self, mydict ):
       old_values = mydict.copy()
       self.weather_com_result = pywapi.get_weather_from_weather_com(weatherDotComLocationCode)
       #check if the dictionary has error keep old data; else return new data
       if self.weather_com_result.has_key('error'):
           logging.info(self.weather_com_result['error'])
           logging.info("the server send broken data, pywapi return there is a problem with some .json tag")
           return old_values
       else:
           return self.weather_com_result
       
    
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
    
    #todo: seperate code in state-machine in run and put other stuff in seperate functions
    # implement run method
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
                  self.weather_com_result = self.callServer( self.weather_com_result )
                  self.state = "screen1"
                  # if weather_com_result is empty check TODO: FIXME
                  # run alternative data, infunction
                
                if self.betweenTime >= self.updateRate:
                  self.betweenTime = 0
                  self.state = "network"
                  logging.info(format(self.updateRate) + " seconds is over, Calling server...")
                  self.weather_com_result = self.callServer( self.weather_com_result )
                  logging.info("Calling server successful")
                  self.state = "screen1"
                  # if weather_com_result is empty check TODO: FIXME
                  # run alternative data
                #
                
                
                # extract current data for today
                self.today = self.weather_com_result['forecasts'][0]['day_of_week'][0:3] + " " \
                    + self.weather_com_result['forecasts'][0]['date'][4:] + " " \
                    + self.weather_com_result['forecasts'][0]['date'][:3]
                self.windSpeed = self.weather_com_result['current_conditions']['wind']['speed']
                self.currWind = "{}km/h ".format(self.windSpeed) + self.weather_com_result['current_conditions']['wind']['text']  
                self.currTemp = self.weather_com_result['current_conditions']['temperature'] + u'\N{DEGREE SIGN}' + "C"
                self.currPress = self.weather_com_result['current_conditions']['barometer']['reading'][:-3] + "mb"
                self.uv = "UV {}".format(self.weather_com_result['current_conditions']['uv']['text'])
                self.humid = "Hum {}%".format(self.weather_com_result['current_conditions']['humidity'])
                self.currTempFeeling = "(" + self.weather_com_result['current_conditions']['feels_like'] + u'\N{DEGREE SIGN}' + "C)"
                self.todayDesc = "It is " + self.weather_com_result['current_conditions']['text'].lower() + " today."
 
                # summary and description of forecast data                
                self.forecastDesc = ["Day", "Max", "Min", "   ", "   "] # forecastDesc = ["Day", "Max", "Min", "Hum", "Kmh"]
                
                
                for i in range(0, 5):
                    if not(self.weather_com_result['forecasts'][i]):
                        break
                        
                    self.forecastDays[i] = self.weather_com_result['forecasts'][i]['day_of_week'][0:3]
                    self.forecaseHighs[i] = self.weather_com_result['forecasts'][i]['high'] + u'\N{DEGREE SIGN}' + "C"
                    self.forecaseLows[i] = self.weather_com_result['forecasts'][i]['low'] + u'\N{DEGREE SIGN}' + "C"
                    self.forecastPrecips[i] = self.weather_com_result['forecasts'][i]['day']['chance_precip'] + "%"
                    self.forecastWinds[i] = self.weather_com_result['forecasts'][i]['day']['wind']['speed'] + \
                        self.weather_com_result['forecasts'][i]['day']['wind']['text']
                    self.forecastIcons[i] = installPathImgSmall + (self.weather_com_result['forecasts'][i]['day']['icon']) + ".png"
                
                        
                # 1. screen, dayInformation
                # blank the screen
                lcd.screen.fill(colourBlack)
 
                # Render the weather logo at 0,0
                icon = installPathImgBig + (self.weather_com_result['current_conditions']['icon']) + ".png"
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
                      logo = pygame.image.load(self.forecastIcons[i]).convert()
                      self.w = logo.get_width()
                      self.h = logo.get_height()
                      logo = pygame.transform.scale(logo, (self.w,self.h)) 
                      lcd.screen.blit(logo, (textAnchorX, textAnchorY))
                      textAnchorX+=textXoffset
                    except pygame.error as message:
                      logging.warn(self.forecastIcons) # to see which icons are missing or is empty json
                      str = "err width: {}" .format(self.w)
                      str = str + " height: {}" .format(h)
                      logging.warn(str)
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

