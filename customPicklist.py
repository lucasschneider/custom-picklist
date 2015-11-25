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
  def __init__(self, t, c, l, cn, b, s, co):
    self.title = t
    self.collection = c
    self.location = l
    self.callNum = cn
    self.barcode = b
    self.status = s
    self.checkedOut = co

  def __repr__(self):
    return repr((self.location, self.collection, self.callNum))

## Function to login into Koha before data extraction ##
def login():
    user = input("Username [%s]: " % getpass.getuser())
    if not user:
        user = getpass.getuser()

    p1 = getpass.getpass()

    return [user, p1]

## Parse for proper argumets ##
parser = argparse.ArgumentParser(description='This script generates a pull list HTML file from a plain text file of barcode numbers. Each library barcode number should be given its own line without punctuation. This is intended for use by LibLime Koka users withing the South Central Library System in Wisconsin.')
parser.add_argument('-i','--input', help='Input file name (.txt)',required=True)
parser.add_argument('-o','--output',help='Output file name (.html)', required=True)
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
withdrawnIdx = 0
damagedIdx = 0
notForLoanIdx = 0
checkedOutIdx = 0
for i in range(len(headers)):
  if headers[i].get_text().strip() == "Title":
    titleIdx = i
  elif headers[i].get_text().strip() == "Collection code":
    collectionIdx = i
  elif headers[i].get_text().strip() == "Shelving location":
    locationIdx = i
  elif headers[i].get_text().strip() == "Full call number":
    callNumIdx = i
  elif headers[i].get_text().strip() == "Barcode":
    barcodeIdx = i
  elif headers[i].get_text().strip() == "Withdrawn status":
    withdrawnIdx = i
  elif headers[i].get_text().strip() == "Damaged status":
    damagedIdx = i
  elif headers[i].get_text().strip() == "Not for loan status":
    notForLoanIdx = i
  elif headers[i].get_text().strip() == "Checked out":
    checkedOutIdx = i

results = soup.find(id="itemst").tbody.find_all('tr')
pullItems = []
thisMonth = datetime.date.today().strftime('%m/%Y')
pullMonth = (datetime.date.today() + relativedelta(months=+6)).strftime('%m/%Y')
branchCode = str.upper(loginCred[0][:3])

for i in range(len(results)):
  result = results[i].find_all('td')
  
  withdrawn = str(result[withdrawnIdx].get_text().strip())
  damaged = str(result[damagedIdx].get_text().strip())
  notForLoan = str(result[notForLoanIdx].get_text().strip())
  itemStatus = "OK"
  checkedOut = ""
  
  if withdrawn and damaged and notForLoan:
    itemStatus = withdrawn + "<br />" + damaged + "<br />" + notForLoan
  elif withdrawn and damaged:
    itemStatus = withdrawn + "<br />" + damaged
  elif withdrawn and notForLoan:
    itemStatus = withdrawn + "<br />" + notForLoan
  elif damaged and notForLoan:
    itemStatus = damaged + "<br />" + notForLoan
  elif withdrawn:
    itemStatus = withdrawn
  elif damaged:
    itemStatus = damaged
  elif notForLoan:
    itemStatus = notForLoan
  
  if checkedOutIdx != 0:
    checkedOutStr = str(result[checkedOutIdx].get_text().strip())
    if checkedOutStr:
      checkedOut = "Yes"
  pullItems.append(Item(result[titleIdx].a.get_text(),result[collectionIdx].get_text(),result[locationIdx].get_text(),result[callNumIdx].get_text(),result[barcodeIdx].get_text(), itemStatus, checkedOut))

sortedItems = sorted(pullItems, key=attrgetter('location','collection','callNum'))

f = open(str(args.output), 'w')
f.write("<html>\n<head>\n<style>\nth{font-weight: bold;}td{padding:5px 7px;}</style></head>\n<body>\n")
f.write("<p>[POOL ITEMS] " + sortedItems[0].collection + "</p>")
f.write("<p>Arrived at "+ branchCode + " " +  thisMonth + ", to be pulled " + pullMonth + "</p>")
f.write("<table>\n<tr>\n<th>Call #</th>\n<th>Title</th>\n<th>Barcode</th>\n<th>Item status</th>\n<th>Checked out?</th>\n</tr>\n")
for item in sortedItems:
  
  f.write("<tr>\n<td>"+str(item.callNum)+"</td>\n<td>"+str(item.title)+"</td>\n<td>"+str(item.barcode)+"</td>\n<td>"+str(item.status)+"</td>\n<td>"+str(item.checkedOut)+"</td>\n</tr>\n")
f.write("</table>\n</body>\n</html>")
f.close()
