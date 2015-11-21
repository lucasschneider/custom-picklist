#!/usr/bin/python

import getpass
import argparse
import http.cookiejar
import urllib
import urllib.request
#import urllib.error
import datetime
from dateutil.relativedelta import relativedelta
from operator import itemgetter, attrgetter, methodcaller
from bs4 import BeautifulSoup

## Class to store picklist items ##
class Item:
  def __init__(self, t, c, l, cn, b):
    self.title = t
    self.collection = c
    self.location = l
    self.callNum = cn
    self.barcode = b

  def __repr__(self):
    return repr((self.location, self.collection, self.callNum))

  def setTitle(t):
    self.title = t
  def setCollection(c):
    self.collection = c
  def setLocation(l):
    self.location = l
  def setCallNum(cn):
    self.callNum = cn
  def setBarcode(b):
    self.barcode = b

  def getTitle():
    return str(self.title)
  def getCollection():
    return str(self.collection)
  def getLocation():
    return str(self.location)
  def getCallNum():
    return str(self.callNum)
  def getBarcode():
    return str(self.barcode)

## Function to login into Koha before data extraction ##
def login():
    user = input("Username [%s]: " % getpass.getuser())
    if not user:
        user = getpass.getuser()

    p1 = getpass.getpass()

    return [user, p1]

## Parse for proper argumets ##
parser = argparse.ArgumentParser(description='This is a demo script by nixCraft.')
parser.add_argument('-i','--input', help='Input file name',required=True)
parser.add_argument('-o','--output',help='Output file name', required=True)
args = parser.parse_args()

## Attempt login ##
loginCred = login()

## Begin HTML requests ##
# Store the cookies and create an opener that will hold them
cj = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))

# Add our headers
opener.addheaders = [('User-agent', 'KohaTesting')]

# Install our opener (note that this changes the global opener to the one
# we just made, but you can also just call opener.open() if you want)
urllib.request.install_opener(opener)

# The action/ target from the form
authentication_url = 'http://scls-staff.kohalibrary.com/cgi-bin/koha/mainpage.pl'

# Input parameters we are going to send
payload = {
  'branch': '',
  'userid': loginCred[0],
  'password': loginCred[1]
  }

# Use urllib to encode the payload
data = urllib.parse.urlencode(payload)
data = data.encode('utf8')

# Build our Request object (supplying 'data' makes it a POST)
req = urllib.request.Request(authentication_url, data)
urllib.request.urlopen(req)

## Parse for proper argumets ##
parser = argparse.ArgumentParser(description='This is a demo script by nixCraft.')
parser.add_argument('-i','--input', help='Input file name',required=True)
parser.add_argument('-o','--output',help='Output file name', required=True)
args = parser.parse_args()

barcodes = [x.strip('\n') for x in open(str(args.input)).readlines()]
barcodes = list(filter(None, barcodes))
barcodeList = ""
for barcode in barcodes:
  barcodeList += barcode + '\r\n'

# Input parameters we are going to send
payload = {
  'op': 'show',
  'barcodelist': str(barcodeList)
  }

# Use urllib to encode the payload
data = urllib.parse.urlencode(payload)
data = data.encode('utf8')

url = 'http://scls-staff.kohalibrary.com/cgi-bin/koha/tools/batchMod.pl'
req = urllib.request.Request(url, data)

# Make the request and read the response
resp = urllib.request.urlopen(req)
html = resp.read()

soup = BeautifulSoup(html, 'html.parser')

results = soup.find(id="itemst").tbody.find_all('tr')
pullItems = []

for i in range(len(results)):
  result = results[i].find_all('td')
  pullItems.append(Item(result[1].a.get_text(),result[6].get_text(),result[11].get_text(),result[15].get_text(),result[16].get_text()))

sortedItems = sorted(pullItems, key=attrgetter('location','collection','callNum'))

f = open(str(args.output), 'w')
f.write(datetime.date.today().strftime('This list was generated on:       %x') + '\n')
f.write((datetime.date.today() + relativedelta(months=+6)).strftime('These items should be pulled on:  %x') + '\n\n')
f.write("Title\tCollection\tLocation\tCall #\n----- Barcode\n\n")
for item in sortedItems:
  f.write(str(item.title)+"\t"+str(item.collection)+"\t"+str(item.location)+"\t"+str(item.callNum)+"\n----- Barcode: "+str(item.barcode)+"\n\n")
#  f.write("Title:       " + str(item.title) + '\n')
#  f.write("Collection:  " + str(item.collection) + '\n')
#  f.write("Location:    " + str(item.location) + '\n')
#  f.write("Call #:      " + str(item.callNum) + '\n')
#  f.write("Barcode:     " + str(item.barcode) + '\n\n')
f.close()
