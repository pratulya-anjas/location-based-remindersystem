
import geocoder

def get_current_coordinates():
   g = geocoder.ip('me')
   return g.latlng


lat, lon= get_current_coordinates()

print(lat,lon)