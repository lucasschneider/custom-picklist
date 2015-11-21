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
import sys

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
parser.add_argument('-p','--print-style',help='(1) standard paper, (2) receipt paper')
args = parser.parse_args()

while True:
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
  resp = urllib.request.urlopen(req)
  html = resp.read()
  soup = BeautifulSoup(html, 'html.parser')
  
  if soup.find(id="login_error") == None:
    break;
  else:
    print("\nIncorrect username or password, please try again.\n")

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

headers = soup.find(id="itemst").thead.find_all('th')
titleIdx = 0
collectionIdx = 0
locationIdx = 0
callNumIdx = 0
barcodeIdx = 0
for i in range(len(headers)):
  if headers[i].get_text().strip() == "Title":
    titleIdx = i
  if headers[i].get_text().strip() == "Collection code":
    collectionIdx = i
  if headers[i].get_text().strip() == "Shelving location":
    locationIdx = i
  if headers[i].get_text().strip() == "Full call number":
    callNumIdx = i
  if headers[i].get_text().strip() == "Barcode":
    barcodeIdx = i

results = soup.find(id="itemst").tbody.find_all('tr')
pullItems = []

for i in range(len(results)):
  result = results[i].find_all('td')
  pullItems.append(Item(result[titleIdx].a.get_text(),result[collectionIdx].get_text(),result[locationIdx].get_text(),result[callNumIdx].get_text(),result[barcodeIdx].get_text()))

sortedItems = sorted(pullItems, key=attrgetter('location','collection','callNum'))

f = open(str(args.output), 'w')
f.write("<html>\n<head>\n<style>\nth{font-weight: bold;}td{padding:5px 7px;}</style></head>\n<body>\n")
f.write("<p>"+datetime.date.today().strftime('This list was generated on:       %x') + '<br />')
f.write((datetime.date.today() + relativedelta(months=+6)).strftime('These items should be pulled on:  %x') + '</p>')
f.write("<table>\n<tr>\n<th>Call #</th>\n<th>Title</th>\n<th>Collection</th>\n<th>Location</th>\n<th>Barcode</th>\n</tr>\n")
for item in sortedItems:
  f.write("<tr>\n<td>"+str(item.callNum)+"</td>\n<td>"+str(item.title)+"</td>\n<td>"+str(item.collection)+"</td>\n<td>"+str(item.location)+"</td>\n<td>"+str(item.barcode)+"</td>\n</tr>\n")
f.write("</table>\n</body>\n</html>")
f.close()
