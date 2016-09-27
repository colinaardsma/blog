import urllib2
from google.appengine.ext import db
from dbmodels import Users, Blog #import Users and Blog classes from python file named dbmodels
import hashing, gqlqueries, validuser #import python files I've made
from xml.dom import minidom

IP_URL = "http://freegeoip.net/xml/"

def get_coords(ip): #determines coordinates based on IP provided (doesn't work when running locally)
    ip = "184.154.83.119"
    ip = "72.229.28.185"
    ip = "134.201.250.155"
    url = IP_URL + ip
    content = None
    try:
        content = urllib2.urlopen(url).read()
    except urllib2.URLError:
        return

    if content:
        #parse xml and find coordinates
        p = minidom.parseString(content)
        lat = p.getElementsByTagName('Latitude')[0].childNodes[0].nodeValue
        lon = p.getElementsByTagName('Longitude')[0].childNodes[0].nodeValue
        return db.GeoPt(lat, lon)

def getMap(points):
    mapUrl = "https://maps.googleapis.com/maps/api/staticmap?size=750x375"
    if points:
        for p in points:
            marker = "&markers=" + str(p)
            mapUrl += marker
    return mapUrl
