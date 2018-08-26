import os, syslog
import pygame
import logging

class PyLcd :
    screen = None;
    colourBlack = (0, 0, 0)

    def __init__(self):
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

    def __del__(self):
        logging.info("pygame screen destructor called -> QUIT now.")
        pygame.display.quit()
        #print("Destructor pygame display shuts down.")
