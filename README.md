# weatherstation
Project with Raspberry Pi, pywapi, forecast.io, pygame

Project uses fbcon driver (framebuffer) from shell and disable X Server.
Goal is to show Weather Information + grahpics on LCD Display.

Previous runs with pywapi API, now runs with forecast.io Weather API.
Pygame delivers the graphics framework to show pictures and react one touch-screen events.


I used the project from Jamie Jackson: http://blog.jacobean.net/?p=1016
in my scope are two screens, a simple state machine and little changes.


My Hardware was a Raspberry Pi B+ with a Kuman 3,5 inch LCD Touchscreen Display.


Software
python + pygame + pywapi-repository

pygame Resolution
width  = 656
height = 415


Disclaimer Warranty

The Icons are by Merlin the Red, with great thanks to him.
http://www.deviantart.com/art/plain-weather-icons-157162192
There are only for private purpose not for commercial use.

## Installation

Install pygame and use python3 (because python2 is End-of-Life support (EOL))

If there is any error related missing something from SDL Library, like:

```
ERROR:root:Error creating pygame Screen for X-Server: font module not available (ImportError: libSDL2_ttf-2.0.so.0: cannot open shared object file: No such file or directory)
```


install python3 SDL Support
```
sudo apt-get install python3-sdl2
```


### fbcon driver only (no X-Server)
disable the x-server in os and make sure fbcon driver is set properly.


### openweater data api usage
tbd
