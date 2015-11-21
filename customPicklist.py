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

pullItems = []
for barcode in barcodes:
  # Input parameters we are going to send
  payload = {
    'search-form': '39078053952421'#str(barcode)
    }

  # Use urllib to encode the payload
  data = urllib.parse.urlencode(payload)
  data = data.encode('utf8')

  url = 'http://scls-staff.kohalibrary.com/cgi-bin/koha/catalogue/moredetail.pl'
  req = urllib.request.Request(url, data)

  # Make the request and read the response
  resp = urllib.request.urlopen(req)
  html = resp.read()

  soup = BeautifulSoup(html, 'html.parser')
  itemEditURL = soup.select(".yui-g a")[0].get("href")
  print(itemEditURL)
  sys.exit(0)
  req = urllib.request.Request(str(itemEditURL))
  
  # Make the request and read the response
  resp = urllib.request.urlopen(req)
  html = resp.read()
  
  soup = BeautifulSoup(html, 'html.parser')
  results = soup.find('cataloguing_additem_newitem').select('.subfield_line');
  print(results)
  sys.exit(0)

  for i in range(len(results)):
    result = results[i].find_all('td')
    pullItems.append(Item(result[1].a.get_text(),result[6].get_text(),result[10].get_text(),result[14].get_text(),result[15].get_text()))

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
