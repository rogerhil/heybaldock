from urllib import urlopen

from geopy import geocoders

SEARCH_CEP_URL = 'http://viavirtual.com.br/webservicecep.php?cep=%s'

def lat_long_from_address(address):
    """
    """
    maps = geocoders.Google()
    _, lat, long = maps.geocode(address)
    return lat, long

def search_zip(zipcode):
    """
    """
    page = urlopen(SEARCH_CEP_URL % zipcode)
    content = page.read().decode('iso-8859-1')
    street, district, city, _, ufraw = content.split('||', 4)
    state = ufraw.replace('|', '')
    d = {
        'street': street,
        'district': district,
        'city': city,
        'state': state
    }
    return d