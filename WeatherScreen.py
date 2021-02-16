import os
from sys import exit
import pygame
import time
#import pywapi
import requests
import string
import logging
import datetime
import calendar
import threading

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
# Playing around with the original Code and adding my own Stuff, so I recycled/changed the code mostly.
# If you want to use forecast.io or darksky maybe better using this API: https://github.com/Detrous/darksky
# openweaterdata.org is also a nice API.

#TODO: Threading, Queue, Cleanup, add auto installer, auto config, with python setup tools, and read config ...
# installPath is like "/home/username/installfolder/img/big" ... ".../small"
installPathImgBig = "img/big/"
installPathImgSmall = "img/small/"

# location for Cottbus, Brandenburg, Germany on weather.com
weatherDotComLocationCode = 'GMXX0171'


class PyLcd :
    screen = None;
    colorBlack = (0, 0, 0)

    def init_framebuffer_screen(self):
        "Ininitializes a new pygame screen using the framebuffer"
        # Based on "Python GUI in Linux frame buffer"
        # http://www.karoltomala.com/blog/?p=679
        disp_no = os.getenv("DISPLAY")
        if disp_no:
            print("I'm running under X display = {0}".format(disp_no))

        os.putenv('SDL_FBDEV', '/dev/fb1')

        # Select frame buffer driver
        # Make sure that SDL_VIDEODRIVER is set
        driver = 'fbcon'
        if not os.getenv('SDL_VIDEODRIVER'):
            os.putenv('SDL_VIDEODRIVER', driver)
        try:
            pygame.display.init()
        except Exception as e:
           print("exception: {}".format(e))
        except pygame.error:
            print('Driver: {0} failed.'.format(driver))
            exit(0)

        size = (pygame.display.Info().current_w, pygame.display.Info().current_h)
        self.screen = pygame.display.set_mode(size, pygame.FULLSCREEN)
        # Clear the screen to start
        self.screen.fill((0, 0, 0))
        # Initialise font support
        pygame.font.init()
        # Render the screen
        pygame.display.update()
        logging.debug("pygame runs with fbcon support.")

    def init_xserver_screen(self):
        try:
            pygame.init()
            #pygame.display.init()

            # Create a screen
            #size = (pygame.display.Info().current_w, pygame.display.Info().current_h)
            #self.screen = pygame.display.set_mode(size, pygame.FULLSCREEN)
            self.screen = pygame.display.set_mode((656,415))
            pygame.display.set_caption("WeatherScreen")
            # Clear the screen to start
            self.screen.fill((0, 0, 0))
            # Initialise font support
            pygame.font.init()
            # Render the screen
            pygame.display.update()
            logging.debug("pygame runs with X-Server support.")
        except Exception as e:
           logging.error("Error creating pygame Screen for X-Server: {}".format(e))

    def __init__(self):
        self.init_xserver_screen()
        logging.debug("pygame screen succesful created.")
        print("pygame screen succesful created.")

    def __del__(self):
        logging.info("pygame screen destructor called -> QUIT now.")
        pygame.display.quit()
        #print("Destructor pygame display shuts down.")

# Create an instance of the PyLcd class
lcd = PyLcd()

# Constants
pygame.mouse.set_visible(False)
# colours
colorWhite = (255, 255, 255)
colorBlack = (0, 0, 0)
colorYellow = (255,255,0)
colorGreen = (0,255,0)
colorOrange = (255,100,10)
colorRed = (255,0,0)
colorPurple = (240,0,255)

# font
fontpath = pygame.font.match_font('dejavusansmono')
# set up 3 sizes
font = pygame.font.Font(fontpath, 36)
fontS2 = pygame.font.Font(fontpath, 28)
fontSm = pygame.font.Font(fontpath, 18)
# Constants

class PygameWeather(object):
    """This class uses pygame and show on [ X-Server | Framebuffer ] graphic Weatherinformation"""

    # class variable
    updateRate = 7200     # seconds, for server call # update interval
    betweenTime = 20      # seconds, befor screen switching (pause time) obsolet
    screenTimeOffset = 20 # same Time like betweenTime, was intentionally the time the screens are show
    # more vars
    app_states = ["initial", "screen1", "screen2", "screen3", "network"]
    lcd_states = [0,1,2]
    state = 0
    weather_data = {}
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
    forecastPrecipProps = {}
    forecastWinds = {}
    forecastIcons = {}
    forecastUVs = {}
    forecastOzones = {}
    forecastHums = {}
    forecastSummary = {}

    # pygame user events
    screen3_event = pygame.USEREVENT + 3
    screen2_event = pygame.USEREVENT + 2
    screen1_event = pygame.USEREVENT + 1

    # set timer for the user events
    pygame.time.set_timer(screen1_event, betweenTime)
    pygame.time.set_timer(screen2_event, betweenTime)
    pygame.time.set_timer(screen3_event, betweenTime)

    #TODO: add all local vars here add self. in front of all local vars

    # def evaluateInformation() # put the var assignment here
    # def updateScreen1         # put graphical change for screen1 here
    # def updateScreen2         # put graphical change for screen2 here

    def getWeekday(self, number):
        d_today = datetime.datetime.today()
        d_weekday = d_today + datetime.timedelta(days=+number)
        dt = d_weekday.weekday()
        #d_strs = list(calendar.day_name)
        d_strs = list(calendar.day_abbr)
        return d_strs[dt]

    # state rotator with text_state, not a good idea, anyway
    def misc(self, text_state, direction):
        state_number = int(text_state[6])
        if direction == "left":
            if (state_number - 1) == 0:
                new_text_state = "screen3"
            else:
                new_text_state = "screen" + str(state_number - 1)
        elif direction == "right":
            if (state_number + 1) == 4:
                new_text_state = "screen1"
            else:
                new_text_state = "screen" + str(state_number + 1)
        else:
            print("This is not a valid direction.")

        return new_text_state

    def raise_event(self, text_state):
        next_event = None
        if text_state == "screen1":
            next_event = self.screen1_event
        elif text_state == "screen2":
            next_event = self.screen2_event
        elif text_state == "screen3":
            next_event = self.screen3_event
        else:
            pass
        pygame.event.post(next_event)


    def progressScreen(self):
       lcd.screen.fill(colorBlack)
       pygame.display.update()
       try:
           picture = installPathImgBig + "easteregg_2.png"
           logo = pygame.image.load(picture).convert()
           self.w = logo.get_width() / 2.0
           self.h = logo.get_height() / 2.0
           logo = pygame.transform.scale(logo, (self.w,self.h))
           self.lcd.screen.blit(logo, (0, 0))
           textAnchorX = 310
           textAnchorY = 5
           textYoffset = 40
           text_surface = self.font.render("Loading ...", True, self.colorWhite)
           lcd.screen.blit(text_surface, (textAnchorX, textAnchorY))
           pygame.display.update()
           time.sleep(self.screenTimeOffset)
       except Exception as e:
           logging.warning(e)

    # call weather server, if no connection or error return old data
    def callServer( self, mydict ):
        """
        returns dictionary with response from weather API Server
        if response HTTP Status != 200 returns None
        """
        old_values = mydict.copy()
        url = 'https://api.forecast.io/forecast/500e8abf656226b5076cd1886f87f8b2/51.0475,13.7404?units=si&lang=de'
        params = {}
        # params = dict(foo='', foo2='')
        resp = requests.get(url=url, params=params)
        if (resp.status_code == 200):
            data = resp.json()
            #pp.pprint(data)
            return data
        if mydict == {}:
            # todo: logging
            return None
        if resp.status_code != 200:
            return old_values
        # todo add dict return

    # see a clock with secounds, just call it in loop or as many times as you need it, after it clear the screen !
    def showClock(self):
        # clear screen and update
        lcd.screen.fill(colorBlack)
        pygame.display.update()
        # show the clock @ (10,260), uodate the screen and wait 1 second
        updated = time.strftime("%H:%M:%S")
        text_surface = fontS2.render(updated, True, colorWhite)
        lcd.screen.blit(text_surface, (10, 260))
        pygame.display.update()
        time.sleep(1)

    def showUVcolored(self):
        uv = self.weather_data['currently']['uvIndex'] # int(self.uv.split()[0])
        if uv >= 0 and uv <= 2:
            colored_text_surface = font.render('{} niedrig'.format(self.uv), True, colorGreen)
        elif uv >= 3 and uv <= 5:
            colored_text_surface = font.render('{} mäßig'.format(self.uv), True, colorYellow)
        elif uv >= 6 and uv <= 7:
            colored_text_surface = font.render('{} hoch'.format(self.uv), True, colorOrange)
        elif uv >= 8 and uv <= 10:
            colored_text_surface = font.render('{} Gefahr!'.format(self.uv), True, colorRed)
        elif uv >= 11:
            colored_text_surface = font.render('{} Extrem!'.format(self.uv), True, colorPurple)
        else:
            colored_text_surface = None
        return colored_text_surface

    def showScreen1(self):
        # blank the screen
        lcd.screen.fill(colorBlack)

        # Render the weather logo at 0,0
        icon = installPathImgBig + (self.weather_data['currently']['icon']) + ".png"
        print(icon)
        try:
            logo = pygame.image.load(icon).convert()
        except e:
            logging.error("Error while loading screen1 icon: {}".format(e))
        self.w = logo.get_width() - 50
        self.h = logo.get_height() - 50
        logo = pygame.transform.scale(logo, (self.w,self.h))
        lcd.screen.blit(logo, (0, 0))

        # set the anchor for the current weather data text
        textAnchorX = 260 # 310 war ok bei 328 Bild
        textAnchorY = 5
        textYoffset = 40

        # add current weather data text artifacts to the screen
        text_surface = font.render(self.todayDesc, True, colorWhite)
        lcd.screen.blit(text_surface, (textAnchorX, textAnchorY))
        textAnchorY+=textYoffset
        textAnchorY+=textYoffset
        text_surface = font.render(self.currTemp, True, colorWhite)
        lcd.screen.blit(text_surface, (textAnchorX, textAnchorY))
        textAnchorY+=textYoffset
        text_surface = font.render(self.currTempFeeling, True, colorWhite)
        lcd.screen.blit(text_surface, (textAnchorX, textAnchorY))
        textAnchorY+=textYoffset
        textAnchorY+=textYoffset
        text_surface = font.render(self.currWind, True, colorWhite)
        lcd.screen.blit(text_surface, (textAnchorX, textAnchorY))
        textAnchorY+=textYoffset
        #text_surface = font.render(self.currPress, True, colorWhite)
        #lcd.screen.blit(text_surface, (textAnchorX, textAnchorY))
        #textAnchorY+=textYoffset
        text_surface = self.showUVcolored()
        lcd.screen.blit(text_surface, (textAnchorX, textAnchorY))
        textAnchorY+=textYoffset
        text_surface = font.render(self.humid, True, colorWhite)
        lcd.screen.blit(text_surface, (textAnchorX, textAnchorY))

        # wait between screen changes screenTimeOffset alias first betweenTime
        pygame.display.update()
        # wait
        time.sleep(self.screenTimeOffset)
        self.betweenTime += self.screenTimeOffset
        # blank the screen after screenTimeOffset
        lcd.screen.fill(colorBlack)
        pygame.display.update()

    def showScreen2(self):
        # state = screen2
        # blank the screen
        lcd.screen.fill(colorBlack)
        pygame.display.update()

        # set X axis text anchor for the forecast text
        textAnchorX = 0
        textAnchorY = 10
        textXoffset = 100 #75
        textYoffset = 40
        #pygame.draw.line(lcd.screen.get_surface(), colorWhite, (50,10), (450,10),4)

        # add summy of the values in one row
        for i in range(0,6):
          text_surface = fontS2.render(self.forecastDesc[i], True, colorWhite)
          lcd.screen.blit(text_surface, (textAnchorX, textAnchorY))
          textAnchorY+=textYoffset

        textAnchorX+=120
        textXoffset = 100

        # add each days forecast text + icon
        for i in range(1, 5):
            try:
                textAnchorY = 10
                print(self.forecastDays[i])
                print(self.forecaseHighs[i])
                print(self.forecaseLows[i])
                print(self.forecastIcons[i])
                text_surface = fontS2.render(self.forecastDays[i], True, colorWhite)
                lcd.screen.blit(text_surface, (textAnchorX, textAnchorY))
                textAnchorY+=textYoffset
                text_surface = fontS2.render(self.forecaseHighs[i], True, colorWhite)
                lcd.screen.blit(text_surface, (textAnchorX, textAnchorY))
                textAnchorY+=textYoffset
                text_surface = fontS2.render(self.forecaseLows[i], True, colorWhite)
                lcd.screen.blit(text_surface, (textAnchorX, textAnchorY))
                textAnchorY+=textYoffset
                text_surface = fontS2.render(self.forecastHums[i], True, colorWhite)
                lcd.screen.blit(text_surface, (textAnchorX, textAnchorY))
                textAnchorY+=textYoffset
                text_surface = fontS2.render(self.forecastWinds[i], True, colorWhite)
                lcd.screen.blit(text_surface, (textAnchorX, textAnchorY))
                textAnchorY+=textYoffset
                text_surface = fontS2.render(self.forecastUVs[i], True, colorWhite)
                lcd.screen.blit(text_surface, (textAnchorX, textAnchorY))
                textAnchorY+=textYoffset
                #text_surface = fontS2.render(self.forecastPrecips[i], True, colorWhite) # Niederschlag
                #lcd.screen.blit(text_surface, (textAnchorX, textAnchorY))
                #textAnchorY+=textYoffset

            except pygame.error as message:
                logging.warning("showscreen2 text: {}".format(message))
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
              logging.warning("showscreen2 icons: {}".format(message))
              textAnchorX+=textXoffset


        # today desc under the table
        textAnchorY = 330
        textAnchorX = 440
        updated = time.strftime("%H:%M")
        text_surface = fontS2.render('{}'.format(updated) , True, colorWhite)
        lcd.screen.blit(text_surface, (textAnchorX, textAnchorY))

        # update when information
        #textAnchorY+=textYoffset
        #updated = time.strftime("%A %H:%M") #time.strftime("%H:%M:%S"), time.strftime("%H:%M"), time.strftime("%c"), time.strftime("%A %H:%M")
        #text_surface = fontS2.render(updated, True, colorWhite)
        #lcd.screen.blit(text_surface, (textAnchorX, textAnchorY))

        # update screen with forecast text
        pygame.display.update()

        # wait
        time.sleep(self.screenTimeOffset)
        self.betweenTime += self.screenTimeOffset

        # blank the screen after screenTimeOffset
        lcd.screen.fill(colorBlack)
        pygame.display.update()
        # Wait
        #time.sleep(updateRate)

    def showScreen3(self):
        # screen3 siesta beginns
        if (time.strftime("%H:%M") >= '11:00' and time.strftime("%H:%M") <= '15:00') and self.weather_data['currently']['uvIndex'] >= 6:
            self.state = "screen3"
            lcd.screen.fill(colorBlack)
            icon = installPathImgBig + "siesta.jpeg"
            logo = pygame.image.load(icon).convert()
            self.w = logo.get_width() - 400
            self.h = logo.get_height() - 400
            logo = pygame.transform.scale(logo, (self.w,self.h))
            lcd.screen.blit(logo, (0, 0))
            textAnchorX = 310
            textAnchorY = 5
            textYoffset = 40
            text_surface = font.render("Siesta ...", True, colorWhite)
            if self.weather_data['currently']['uvIndex'] >= 8:
                text_surface = font.render("Siesta !!!", True, colorRed)
            lcd.screen.blit(text_surface, (textAnchorX, textAnchorY))
            pygame.display.update()
            time.sleep(self.screenTimeOffset)
            self.betweenTime += self.screenTimeOffset
        # screen3 siesta ends
        # screen3 beginn
        if (time.strftime("%H:%M") >= '18:00' and time.strftime("%H:%M") <= '19:00') or (time.strftime("%d/%m") == '05/12'):
            self.state = "screen3"
            lcd.screen.fill(colorBlack)
            icon = installPathImgBig + "easteregg.png"
            logo = pygame.image.load(icon).convert()
            self.w = logo.get_width() - 30
            self.h = logo.get_height() - 30
            logo = pygame.transform.scale(logo, (self.w,self.h))
            lcd.screen.blit(logo, (0, 0))
            textAnchorX = 310
            textAnchorY = 5
            textYoffset = 40
            text_surface = font.render("Pause ...", True, colorWhite)
            lcd.screen.blit(text_surface, (textAnchorX, textAnchorY))
            pygame.display.update()
            time.sleep(self.screenTimeOffset)
            self.betweenTime += self.screenTimeOffset
        # screen3 ends

    def updateValues(self):
        if self.weather_data != {} and self.weather_data != None:
            # extract current data for today
            self.windSpeed = str(self.weather_data['currently']['windSpeed'])
            self.currWind = "{} km/h ".format(self.windSpeed)
            self.currTemp = str( self.weather_data['currently']['temperature'] ) + u' \N{DEGREE SIGN}' + "C"
            self.currPress = str( self.weather_data['currently']['pressure'] ) + " mb"
            self.ozon =  "{} Ozone".format(self.weather_data['currently']['ozone'])
            self.uv = "{} UV-Index".format(self.weather_data['currently']['uvIndex'])
            self.humid = "{}% Humidity".format(self.weather_data['currently']['humidity'] * 100)
            self.currTempFeeling = "gefühlt " + str( self.weather_data['currently']['apparentTemperature'] ) + u' \N{DEGREE SIGN}' + "C"
            self.todayDesc = str( self.weather_data['currently']['summary'] )

            # summary and description of forecast data
            self.forecastDesc = ["Day", "Max" + u'\N{DEGREE SIGN}' + "C", "Min" + u'\N{DEGREE SIGN}' + "C", "Hum", "km/h", "UV"] # forecastDesc = ["Day", "Max", "Min", "Hum", "Kmh"]

            for i in range(0, 5):
                if not(self.weather_data['daily']['data'][i]):
                    break

                self.forecastDays[i] = self.getWeekday(i)
                self.forecastSummary[i] = str(self.weather_data['daily']['data'][i]['summary'])
                self.forecaseHighs[i] = str(self.weather_data['daily']['data'][i]['temperatureHigh'])
                self.forecaseLows[i] = str(self.weather_data['daily']['data'][i]['temperatureLow'])
                self.forecastPrecips[i] = str(self.weather_data['daily']['data'][i]['precipType'])
                self.forecastPrecipProps[i] = str(self.weather_data['daily']['data'][i]['precipProbability'] * 100) + "%"
                self.forecastWinds[i] = str(self.weather_data['daily']['data'][i]['windSpeed'])
                self.forecastHums[i] = str(self.weather_data['daily']['data'][i]['humidity'] * 100) + "%"
                self.forecastUVs[i] = str(self.weather_data['daily']['data'][i]['uvIndex'])
                self.forecastOzones[i] = str(self.weather_data['daily']['data'][i]['ozone'])
                try:
                    self.forecastIcons[i] = installPathImgSmall + str(self.weather_data['daily']['data'][i]['icon']) + ".png"
                    print(str(self.weather_data['daily']['data'][i]['icon']))
                except e:
                    logging.warning("update icons for pictures: {}".format(e))

    def updateScreen(self, state):
        if state == 1:
            self.showScreen1()
        if state == 2:
            self.showScreen2()
        if state == 3:
            self.showScreen3()
        # wait between screen changes screenTimeOffset alias first betweenTime
        pygame.display.update()
        # wait
        time.sleep(self.screenTimeOffset)
        self.betweenTime += self.screenTimeOffset
        # blank the screen after screenTimeOffset
        lcd.screen.fill(colorBlack)
        pygame.display.update()


    # Key Event checker Thread
    def threadEventChecker(self):
        keep_alive = True
        while keep_alive:
            # get the pressed key
            pressed = pygame.key.get_pressed()
            if pressed[pygame.K_LEFT]:
                #self.raise_event( self.misc(self.state, "left") )
                print("left key pressed")
                self.state = self.state - 1
                if self.state < 0:
                    self.state = 2
                print("next screen: {}".format(self.state))
                pygame.time.set_timer( self.screen1_event, 0)
            if pressed[pygame.K_RIGHT]:
                #self.raise_event( self.misc(self.state, "right") )
                print("right key pressed")
                self.state = self.state + 1
                if self.state > 2:
                    self.state = 0
                print("next screen: {}".format(self.state))
                pygame.time.set_timer( self.screen2_event, 0)
            if pressed[pygame.K_ESCAPE]:
                #self.raise_event ( pygame.QUIT )
                pygame.event.post( pygame.QUIT )
                print("esc key pressed")
                keep_alive = False

    # SDL / Pygame Thread
    def threadShowScreen(self):
        while True:

            # Main Event handling
            for e in pygame.event.get():
                pressed = pygame.key.get_pressed()
                if pressed[pygame.K_LEFT]: self.raise_event( self.misc(self.state, "left") )
                if pressed[pygame.K_RIGHT]: self.raise_event( self.misc(self.state, "right") )
                if pressed[pygame.K_ESCAPE]: sys.exit()
                print(e)
                if e.type == self.screen1_event:
                    self.state = "screen1"
                    self.showScreen1()
                elif e.type == self.screen2_event:
                    self.state = "screen2"
                    self.showScreen2()
                elif e.type == self.screen3_event:
                    self.state = "screen3"
                    self.showScreen3()
                if e.type == pygame.QUIT:
                    raise SystemExit

    #todo: Old solution C-Style state-machine|timer based: seperate code in state-machine in run and put other stuff in seperate functions
    #todo: new solution use pygame + python Threading technics (queue, threading) run one thread fetches events, run other thread show the screen (or both?)
    def main(self):
        running = True
        # initial stuff do only one time
        #todo: Call Server and update data should be in thread safe different thread, calling each day 3-5 times (6 hours)
        self.weather_data = self.callServer(self.weather_data)
        if self.weather_data != None:
            self.updateValues()

        while running:
            FPS = 60
            FramePerSec = pygame.time.Clock()
            FramePerSec.tick(FPS)

            # Thread Screen Shower
            t1 = threading.Thread(target=self.showScreen1())
            #t1.daemon = True

            t2 = threading.Thread(target=self.showScreen2())
            #t2.daemon = True

            t3 = threading.Thread(target=self.showScreen3())

            # Event Checker
            #t = threading.Thread(target=self.threadEventChecker)
            #t.daemon = True
            #t.start()

            # Event Checker
            #t2 = threading.Thread(target=self.threadShowScreen)
            #t2.start()

            #t1.start()
            #t2.start()

            # begin main event handling
            for e in pygame.event.get():
                # get the pressed key
                pressed = pygame.key.get_pressed()
                if pressed[pygame.K_ESCAPE]:
                    pygame.event.post( pygame.QUIT )
                    print("esc key pressed")

                # switch screen manually
                # switch screen from timeout
                if e.type == self.screen1_event:
                    self.state = "screen1"
                    print("screen1")
                    pygame.event.clear()
                    #t1.join(5.0)
                    #print(e)
                if e.type == self.screen2_event:
                    self.state = "screen2"
                    print("screen1")
                    pygame.event.clear()
                    #t2.join(5.0)

                if e.type == self.screen3_event:
                    self.state = "screen3"
                    print("screen3")
                    pygame.event.clear()
                    #t3.join(5.0)

                # Exit
                if e.type == pygame.QUIT:
                    running = False
                    pygame.event.clear()
                    t1.join()
                    t2.join()
                    t3.join()
            # end event handling








            # (obsolete) old state machine
            """
            self.showClock()
            self.weather_data = self.callServer(self.weather_data)
            if self.weather_data != None:
                self.updateValues()
                self.state = "screen1"
                self.showScreen1()

                self.state = "screen2"
                self.showScreen2()

                self.state = "screen3"
                self.showScreen3()
            """

            """
            # retrieve data from weather.com and keep old values if no connection
            if self.state == "initial":
              self.weather_data = self.callServer( self.weather_data )
              logging.info("Inital calling server successful!")
              print(self.weather_data)
              self.progressScreen()
              self.state = "screen1"


            if self.betweenTime >= self.updateRate:
              self.betweenTime = 0
              self.state = "network"
              logging.info(format(self.updateRate) + " seconds is over, Calling server...")
              self.weather_data = self.callServer( self.weather_data )
              logging.info("Calling server successful")
              self.state = "screen1"

            # special screen
            self.showScreen3()

            # after network calling update the values
            self.updateValues()

            # 1. screen, dayInformation
            self.showScreen1()

            # 2. screen, forecast
            self.showScreen2()
            """

        pygame.quit()
        exit()

if __name__ == '__main__':
  logging.basicConfig(level=logging.DEBUG, filename="mylogfile", filemode="a+", format="%(asctime)s %(levelname)s:%(message)s")
  try:
    myweatherprogramm = PygameWeather()
    myweatherprogramm.main()
  except Exception as e:
    logging.warning(e)
