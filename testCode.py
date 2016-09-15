import pywapi
import pprint
pp = pprint.PrettyPrinter(indent=4)
 
cottbus = pywapi.get_weather_from_weather_com('GMXX0171')
 
pp.pprint(cottbus)