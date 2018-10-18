# weatherstation
Project with Raspberry Pi, pywapi, pygame


I use the project from Jamie Jackson: http://blog.jacobean.net/?p=1016
in my scope are two screens, a simple state machine and little changes.


My Hardware was a Raspberry Pi B+ with a Kuman 3,5 inch LCD Display.


Software
python + pygame + pywapi-repository

pygame Resolution
width  = 656
height = 415


Disclaimer Warranty

The Icons are by Merlin the Red, with great thanks to him, my Art Skills are ... okay.
http://www.deviantart.com/art/plain-weather-icons-157162192
There are only for private purpose not for commercial use.

## setup
install python, pygame, and pywapi-repository
have an LCD Screen connected via Raspberry PI, driver setup is done

## runme
run: python Bild.py


### rework is on develop Branch, currently changes going on
+ rework Classes and inherit to Sub-class
+ reuse screen functions and even drawing process -> less lines of Code -> more complexity
TODO:
+ change in server call (optional)
+ add config file
+ add setuptools
+ rework screen elements shown
if pywapi is used and call is not successful -> fallback server solution
(- remove pywapi, use different implementation or write own)
+ add simple screen builder pattern, for create customscreen for drawing
