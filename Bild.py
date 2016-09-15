import os, syslog
import pygame
import time
import pywapi
import string
import logging
 
# *** Not to be used for commercial use without permission!
# if you want to buy the icons for commercial use please send me a note - http://vclouds.deviantart.com/ ***
#
# Credit goes to Jamie Jackson http://blog.jacobean.net/?p=1016 for his nice Tutorial and great Parts of his Code, which i re-use.
# Credit goes to Merlin the Red for his great pictures: http://vclouds.deviantart.com/art/plain-weather-icons-157162192 , which i use.
#  ^-> I use his svg files and bring them to ~ 328x328 px
#
# I modify the original code for my 4 inch display and that it work in two 'screens'. First shows the currentday, Secound shows the forecast.
 
installPath = "/opt/PiTFTWeather/"
 
# location for Cottbus, Brandenburg, Germany on weather.com
weatherDotComLocationCode = 'GMXX0171'

 
class pitft :
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
 
# Create an instance of the PyScope class
mytft = pitft()
 
pygame.mouse.set_visible(False)

# font colours
colourWhite = (255, 255, 255)
colourBlack = (0, 0, 0)
 
# update interval
updateRate = 3600 # seconds, for server call
betweenTime = 20 # seconds, befor screen switching

screenTimeOffset = 20

# set up the fonts
# choose the font
fontpath = pygame.font.match_font('dejavusansmono')
# set up 2 sizes
font = pygame.font.Font(fontpath, 36)
fontS2 = pygame.font.Font(fontpath, 28)
fontSm = pygame.font.Font(fontpath, 18)

# possbile 
states = ["initial", "screen1", "screen2", "network"]
state = "initial"
weather_com_result = {}
h = 0
w = 0
 
# starting class
class Example(object): 
   
    # call weather server, if no connection or error return old data
    def callServer( self, mydict ):
       old_values = mydict.copy()
       weather_com_result = pywapi.get_weather_from_weather_com(weatherDotComLocationCode)
       #check if the dictionary has error keep old data; else return new data
       if weather_com_result.has_key('error'):
           logging.info(weather_com_result['error'])
           return old_values
       else:
           return weather_com_result
       
      
    #todo: seperate code in state-machine in run and put other stuff in seperate functions
    # implement run method
    def run(self):
       global betweenTime
       global updateRate
       global screenTimeOffset
       global weather_com_result
       global state
       global w
       global h
       global forecastIcons
       quit = False
       while not quit:
                global blub
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
               
                #FIXME: every iteration will be generated an new Object that memory bad...
                # retrieve data from weather.com and keep old values if no connection
                if state == "initial":
                  blub = Example()
                  weather_com_result = blub.callServer( weather_com_result )
                  state = "screen1"
                  # if weather_com_result is empty check TODO: FIXME
                  # run alternative data, infunction
                
                if betweenTime >= updateRate:
                  betweenTime = 0
                  state = "network"
                  blub = Example()
                  logging.info("1 hour is over, Calling server...")
                  weather_com_result = blub.callServer( weather_com_result )
                  logging.info("Calling server successful")
                  state = "screen1"
                  # if weather_com_result is empty check TODO: FIXME
                  # run alternative data
                #
                
                
                # extract current data for today
                today = weather_com_result['forecasts'][0]['day_of_week'][0:3] + " " \
                    + weather_com_result['forecasts'][0]['date'][4:] + " " \
                    + weather_com_result['forecasts'][0]['date'][:3]
                windSpeed = weather_com_result['current_conditions']['wind']['speed']
                currWind = "{}km/h ".format(windSpeed) + weather_com_result['current_conditions']['wind']['text']  
                currTemp = weather_com_result['current_conditions']['temperature'] + u'\N{DEGREE SIGN}' + "C"
                currPress = weather_com_result['current_conditions']['barometer']['reading'][:-3] + "mb"
                uv = "UV {}".format(weather_com_result['current_conditions']['uv']['text'])
                humid = "Hum {}%".format(weather_com_result['current_conditions']['humidity'])
                currTempFeeling = "(" + weather_com_result['current_conditions']['feels_like'] + u'\N{DEGREE SIGN}' + "C)"
                todayDesc = "It is " + weather_com_result['current_conditions']['text'].lower() + " today."
 
                # summary and description of forecast data                
                forecastDesc = ["Day", "Max", "Min", "Hum", "Kmh"]
                
                # extract forecast data
                forecastDays = {}
                forecaseHighs = {}
                forecaseLows = {}
                forecastPrecips = {}
                forecastWinds = {}
                forecastIcons = {}
 
                for i in range(0, 5):
                    if not(weather_com_result['forecasts'][i]):
                        break
                        
                    forecastDays[i] = weather_com_result['forecasts'][i]['day_of_week'][0:3]
                    forecaseHighs[i] = weather_com_result['forecasts'][i]['high'] + u'\N{DEGREE SIGN}' + "C"
                    forecaseLows[i] = weather_com_result['forecasts'][i]['low'] + u'\N{DEGREE SIGN}' + "C"
                    forecastPrecips[i] = weather_com_result['forecasts'][i]['day']['chance_precip'] + "%"
                    forecastWinds[i] = weather_com_result['forecasts'][i]['day']['wind']['speed'] + \
                        weather_com_result['forecasts'][i]['day']['wind']['text']
                    forecastIcons[i] = installPath+ (weather_com_result['forecasts'][i]['day']['icon']) + ".png"
                
                        
                # 1. screen, dayInformation
                # blank the screen
                mytft.screen.fill(colourBlack)
 
                # Render the weather logo at 0,0
                icon = installPath+ (weather_com_result['current_conditions']['icon']) + ".png"
                logo = pygame.image.load(icon).convert()
                w = logo.get_width() - 50
                h = logo.get_height() - 50
                logo = pygame.transform.scale(logo, (w,h)) 
                mytft.screen.blit(logo, (0, 0))
 
                forecastIcons[0] = icon # BugFix
                # set the anchor for the current weather data text
                textAnchorX = 260 # 310 war ok bei 328 Bild
                textAnchorY = 5
                textYoffset = 40
 
                # add current weather data text artifacts to the screen
                text_surface = font.render(today, True, colourWhite)
                mytft.screen.blit(text_surface, (textAnchorX, textAnchorY))
                textAnchorY+=textYoffset
                text_surface = font.render(currTemp, True, colourWhite)
                mytft.screen.blit(text_surface, (textAnchorX, textAnchorY))
                # my code
                # feeled temp
                textAnchorY+=textYoffset
                text_surface = font.render(currTempFeeling, True, colourWhite)
                mytft.screen.blit(text_surface, (textAnchorX, textAnchorY))
                # my code
                textAnchorY+=textYoffset
                text_surface = font.render(currWind, True, colourWhite)
                mytft.screen.blit(text_surface, (textAnchorX, textAnchorY))
                textAnchorY+=textYoffset
                text_surface = font.render(currPress, True, colourWhite)
                mytft.screen.blit(text_surface, (textAnchorX, textAnchorY))
                textAnchorY+=textYoffset
                text_surface = font.render(uv, True, colourWhite)
                mytft.screen.blit(text_surface, (textAnchorX, textAnchorY))
                textAnchorY+=textYoffset
                text_surface = font.render(humid, True, colourWhite)
                mytft.screen.blit(text_surface, (textAnchorX, textAnchorY))
 
                
                # wait between screen changes screenTimeOffset alias first betweenTime
                pygame.display.update()
                i = 0                
                while i < screenTimeOffset:
                  global betweenTime
                  time.sleep(1)
                  i = i + 1
                  pygame.display.update() 
                  #time.sleep(screenTimeOffset)
                  
                betweenTime+=screenTimeOffset
                
                # 2. screen
                # state = screen2
                # blank the screen
                mytft.screen.fill(colourBlack)
                pygame.display.update()
                
                # set X axis text anchor for the forecast text
                textAnchorX = 0
                textXoffset = 75 #100
                textAnchorY = 10
                #pygame.draw.line(mytft.screen.get_surface(), colourWhite, (50,10), (450,10),4)

                # add summy of the values in one row
                for i in range(0,5):
                  text_surface = fontS2.render(forecastDesc[i], True, colourWhite)
                  mytft.screen.blit(text_surface, (textAnchorX, textAnchorY))
                  textAnchorY+=textYoffset
                  
                textAnchorX+=70
 
                # add each days forecast text
                for i in range(0, 5):
                    textAnchorY = 10
                    text_surface = fontS2.render(forecastDays[i], True, colourWhite)
                    mytft.screen.blit(text_surface, (textAnchorX, textAnchorY))
                    textAnchorY+=textYoffset
                    text_surface = fontS2.render(forecaseHighs[i], True, colourWhite)
                    mytft.screen.blit(text_surface, (textAnchorX, textAnchorY))
                    textAnchorY+=textYoffset
                    text_surface = fontS2.render(forecaseLows[i], True, colourWhite)
                    mytft.screen.blit(text_surface, (textAnchorX, textAnchorY))
                    textAnchorY+=textYoffset
                    #text_surface = fontS2.render(forecastPrecips[i], True, colourWhite)
                    #mytft.screen.blit(text_surface, (textAnchorX, textAnchorY))
                    #textAnchorY+=textYoffset
                    #text_surface = fontS2.render(forecastWinds[i], True, colourWhite)
                    #mytft.screen.blit(text_surface, (textAnchorX, textAnchorY))
                    #textAnchorX+=textXoffset
                    try:
                      logo = pygame.image.load(forecastIcons[i]).convert()
                      w = logo.get_width() - 265
                      h = logo.get_height() - 265
                      logo = pygame.transform.scale(logo, (w,h)) 
                      mytft.screen.blit(logo, (textAnchorX, textAnchorY))
                      textAnchorX+=textXoffset
                    finally:
                      if w < 10 or h < 10:
                        logging.warn(forecastIcons)
                        str = "scale err: {}" .format(w) #+ " " + .format(h)
                        logging.warn(str)
                        w = logo.get_width() - 150
                        h = logo.get_height() - 150
                      #mytft.screen.blit("blah", (textAnchorX, textAnchorY))
                      #textAnchorX+=textXoffset
                      #logging.warn("icon err")
                     # logging.warn(forecastIcon[0])
                
                
                # today desc under the table
                textAnchorY = 220
                textAnchorX = 10
                text_surface = fontS2.render(todayDesc, True, colourWhite)
                mytft.screen.blit(text_surface, (textAnchorX, textAnchorY))
                
                # update when information
                textAnchorY+=textYoffset
                updated = time.strftime("%H:%M:%S")
                text_surface = fontS2.render(updated, True, colourWhite)
                mytft.screen.blit(text_surface, (textAnchorX, textAnchorY))
                
                # update screen with forecast text
                pygame.display.update()
                
                # wait
                time.sleep(screenTimeOffset)
                betweenTime += screenTimeOffset
               
                # blank the screen after screenTimeOffset
                mytft.screen.fill(colourBlack)
                pygame.display.update()
                #time.sleep(3)
               
                # Wait
                #time.sleep(updateRate)
                

if __name__ == '__main__':
  logging.basicConfig(level=logging.DEBUG, filename="logfile", filemode="a+", format="%(asctime)s %(message)s")
  try: 
    Example().run()
  except Exception as e:
    #print "\n except: %s" % (e,)
    logging.warn(e)

