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
#import threading

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
#
# This application have the goal to show weathergraphics with SDL Library under it.
# Using Pygame as a Wrapper for SDL Lib. Usage is with X-Server (for testing) and with framebuffer /dev/fbcon.
# With a LCD Display as main display the framebuffer is used as graphic driver.

# installPath is like "/home/username/installfolder/img/big" ... ".../small"
installPathImgBig = "img/big/"
installPathImgSmall = "img/small/"


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
        # chose
        #disp_no = os.getenv("DISPLAY")
        #if disp_no:
        # run X
        #else
        # run under fbcon

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
    rotationTime = 20000  # miliseconds, for switching between screens
    updateRate = 7200     # seconds, for server call # update interval
    betweenTime = 20      # seconds, befor screen switching (pause time)
    screenTimeOffset = 20 # same Time like betweenTime, was intentionally the time the screens are show
    # more vars
    app_states = ["initial", "screen1", "screen2", "screen3", "network"] #obsolete
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
    auto_screen_event = pygame.USEREVENT + 50
    screen3_event = pygame.USEREVENT + 3
    screen2_event = pygame.USEREVENT + 2
    screen1_event = pygame.USEREVENT + 1

    # set timer for the user events
    #pygame.time.set_timer(screen1_event, rotationTime) #  fires the event every betweenTime milliseconds
    #pygame.time.set_timer(screen2_event, rotationTime)
    #pygame.time.set_timer(screen3_event, rotationTime)

    def getWeekday(self, number):
        d_today = datetime.datetime.today()
        d_weekday = d_today + datetime.timedelta(days=+number)
        dt = d_weekday.weekday()
        #d_strs = list(calendar.day_name)
        d_strs = list(calendar.day_abbr)
        return d_strs[dt]

    # create a new event in event queue for state_number
    def raise_event(self, state_number):

        if   state_number == 0:
            ee = pygame.event.Event(self.screen1_event)
        elif state_number == 1:
            ee = pygame.event.Event(self.screen2_event)
        elif state_number == 2:
            ee = pygame.event.Event(self.screen3_event)
        else:
            return # state is not known
        #pygame.event.post(ee)
        pygame.fastevent.post(ee) # enqueue new event

    #  enabled the timer; timer fires the event every given time milliseconds
    def enable_event_timer(self):
        #todo: make it generic:  betweenTime * n-Screennumber
        #pygame.time.set_timer(self.screen1_event, self.rotationTime)
        #pygame.time.set_timer(self.screen2_event, self.rotationTime*2)
        #pygame.time.set_timer(self.screen3_event, self.rotationTime*3)
        pygame.time.set_timer(self.auto_screen_event, self.rotationTime)

    # disables the timer for event firing
    def disable_event_timer(self):
        #pygame.time.set_timer(self.screen1_event, 0)
        #pygame.time.set_timer(self.screen2_event, 0)
        #pygame.time.set_timer(self.screen3_event, 0)
        pygame.time.set_timer(self.auto_screen_event, 0)

    # shows the next screen, ring rotation style
    def showNext(self):
        self.rotate_right()
        self.show_screens()


    def progressScreen(self):
       lcd.screen.fill(colorBlack)
       pygame.display.update()
       try:
           #picture = installPathImgBig + "easteregg_2.png"
           #logo = pygame.image.load(picture).convert()
           #self.w = logo.get_width() / 2.0
           #self.h = logo.get_height() / 2.0
           #logo = pygame.transform.scale(logo, (self.w,self.h))
           #self.lcd.screen.blit(logo, (0, 0))
           #textAnchorX = 310
           #textAnchorY = 5
           #textYoffset = 40
           #text_surface = self.font.render("Loading ...", True, self.colorWhite)
           #lcd.screen.blit(text_surface, (textAnchorX, textAnchorY))
           #pygame.display.update()
           #time.sleep(self.screenTimeOffset)
           #todo: draw a graphics or use fancy circle something
           pass
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

    # see a clock with secounds
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

    # format text based on value and return it for blit on text surface
    def showUVcolored(self):
        uv = self.weather_data['currently']['uvIndex']
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

    def showScreen2(self):
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


    def showScreen3(self):
        # screen3 siesta beginns
        if (time.strftime("%H:%M") >= '01:00' and time.strftime("%H:%M") <= '15:00') or self.weather_data['currently']['uvIndex'] >= 6:
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
            #time.sleep(self.screenTimeOffset)
            self.betweenTime += self.screenTimeOffset
        # screen3 siesta ends
        # screen3 beginn
        if (time.strftime("%H:%M") >= '18:00' and time.strftime("%H:%M") <= '24:00') or (time.strftime("%d/%m") == '05/12'):
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
            #time.sleep(self.screenTimeOffset)
            self.betweenTime += self.screenTimeOffset
        # screen3 ends

    def updateValues(self):
        if self.weather_data != {} and self.weather_data != None:
            try:
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
            except e:
                logging.warning("in update values: {}".format(e))

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
                    #print(str(self.weather_data['daily']['data'][i]['icon']))
                except e:
                    logging.warning("update icons for pictures: {}".format(e))
            logging.debug("update values/icons done.")

    def updateScreen(self, state):
        # clear everything before changeing screens
        lcd.screen.fill(colorBlack)
        pygame.display.update()
        if state == 1:
            self.showScreen1()
        if state == 2:
            self.showScreen2()
        if state == 3:
            self.showScreen3()
        if state < 0 or state > 3:
            logging.warning("updateScreen(): updateing to unknown state")



    # Key Event checker Thread
    def threadEventChecker(self):
        keep_alive = True
        while keep_alive:
            event = pygame.fastevent.wait()
            #print(event)

            if event.type == pygame.KEYDOWN:
            # Was it the Escape key? If so, stop the loop.
                if event.key == pygame.K_ESCAPE:
                    print("helper thread is dieing")
                    keep_alive = False

                if event.key == pygame.K_RIGHT:
                    print("right key pressed")
                    self.state = self.state + 1
                    if self.state > 2:
                        self.state = 0
                        ee = pygame.event.Event(self.screen1_event) # enqueue new event
                    else:
                        if self.state == 1:
                            ee = pygame.event.Event(self.screen2_event) # enqueue new event
                        if self.state == 2:
                            ee = pygame.event.Event(self.screen3_event) # enqueue new event
                    pygame.fastevent.post(ee)
                    print("next screen: {}".format(self.state))

                if event.key == pygame.K_LEFT:
                    print("left key pressed")
                    self.state = self.state - 1
                    if self.state < 0:
                        self.state = 2
                        ee = pygame.event.Event(self.screen3_event)
                    else:
                        if self.state == 0:
                            ee = pygame.event.Event(self.screen1_event) # enqueue new event
                        if self.state == 1:
                            ee = pygame.event.Event(self.screen2_event)
                    pygame.fastevent.post(ee)
                    print("next screen: {}".format(self.state))

            # Events Screen related
            if event.type == pygame.USEREVENT:
                if event.type == self.screen1_event:
                    print("need to handle screen1 change")
                    self.showScreen1()
                if event.type == self.screen2_event:
                    print("need to handle screen2 change")
                    self.showScreen2()
                if event.type == self.screen3_event:
                    print("need to handle screen3 change")
                    self.showScreen3()

    # rotate the states left
    def rotate_left(self):
        self.state = self.state - 1
        if self.state < 0:
            self.state = 2

    # rotate the states right
    def rotate_right(self):
        self.state = self.state + 1
        if self.state > 2:
            self.state = 0

    # show the screens matching states
    def show_screens(self):
        if self.state == 0:
            self.showScreen1()
        if self.state == 1:
            self.showScreen2()
        if self.state == 2:
            self.showScreen3()
        time.sleep(0.001)


    def main(self):
        # initial stuff do only one time
        #todo: Call Server and update data (calling each day 3-5 times (6 hours))
        #todo: in initial setup, fire an event which rise again in 6 hours

        # initial server calling
        self.weather_data = self.callServer(self.weather_data)
        if self.weather_data != None:
            self.updateValues()

        FPS = 60
        FramePerSec = pygame.time.Clock()
        FramePerSec.tick(FPS)

        pygame.fastevent.init()
        pygame.event.set_blocked(pygame.MOUSEMOTION)

        while pygame.fastevent.get_init() == False:
            pass

        # initial screen
        self.state = 0
        self.showScreen1()

        # enable timer for screen rotation
        self.enable_event_timer()

        running = True
        print("=== Initial Stuff done ===")

        # main loop
        while running:

            # Event Checker
            event = pygame.event.wait()
            #for event in pygame.fastevent.get():
            #print(event)
            if event.type == pygame.NOEVENT:
                #ee = pygame.event.Event(self.screen1_event)
                #pygame.fastevent.post(ee)
                pass

            # Events Exit related
            elif event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    print("main thread is dieing")
                    running = False

                # switching between screens on Events Arrow Keys
                if event.key == pygame.K_RIGHT:
                    self.rotate_right()
                    self.show_screens()

                if event.key == pygame.K_LEFT:
                    self.rotate_left()
                    self.show_screens()

            # Events manageing
            elif event.type == self.auto_screen_event:
                print("=== screen rotation ===")
                self.showNext()
            elif event.type == self.screen1_event:
                print("event for screen1 recon")
            elif event.type == self.screen2_event:
                print("event for screen2 recon")
                self.showScreen2()
            elif event.type == self.screen3_event:
                print("event for screen3 recon")
                self.showScreen3()

            else:
                pass # ignore other event types
            # Event Checker


            # (obsolete) old state machine
            """
            if self.betweenTime >= self.updateRate:
              self.betweenTime = 0
              self.progressScreen() # todo: draw some graphical informations on current screen
              logging.info(format(self.updateRate) + " seconds is over, Calling server...")
              self.weather_data = self.callServer( self.weather_data )
              logging.info("Calling server successful")

            """
        pygame.display.quit()
        #pygame.quit()
        exit()

if __name__ == '__main__':
  logging.basicConfig(level=logging.DEBUG, filename="mylogfile", filemode="a+", format="%(asctime)s %(levelname)s:%(message)s")
  try:
    myweatherprogramm = PygameWeather()
    myweatherprogramm.main()
  except Exception as e:
    logging.warning(e)
