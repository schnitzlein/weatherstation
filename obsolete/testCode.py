import pywapi
import pprint
import json

# Formated Printer
pp = pprint.PrettyPrinter(indent=4)
 
# Server call
cottbus = pywapi.get_weather_from_weather_com('GMXX0171')
 
# Print to console
pp.pprint(cottbus)


# print in file
#dump server data in result.json file
with open('result.json', 'w') as fp:
    json.dump(cottbus, fp)