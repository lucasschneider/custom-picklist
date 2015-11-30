 #!/usr/bin/python

import getpass
import argparse
import http.cookiejar
import urllib.request
import datetime
from dateutil.relativedelta import relativedelta
from operator import itemgetter, attrgetter, methodcaller
from bs4 import BeautifulSoup
import sys
import os
import re
import webbrowser
new = 2 # open in a new tab, if possible

import tkinter as tk
from tkinter import filedialog

root = tk.Tk()
root.withdraw()

directorySlash = '\\' if os.name == 'nt' else '/'

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
parser = argparse.ArgumentParser(description='This script generates a pull list HTML file from a plain text file of barcode numbers. Each library barcode number should be given its own line without punctuation. This is intended for use by LibLime Koka users within the South Central Library System in Wisconsin.')
parser.add_argument('-b','--branchcode',help='Override the library branch code', nargs='?')
parser.add_argument('-i','--input', help='Input text filename (.txt); Relative to the present working directory')
parser.add_argument('-o','--output',help='Output web filename (.html); Relative to the input file')
args = parser.parse_args()

inFile = args.input

while inFile is None:
  inFile = filedialog.askopenfilename()
  if not inFile:
    sys.exit(0)
print(inFile)

if inFile[-4:] != '.txt':
    print("The file \"" + os.path.realpath(inFile) + "\" does not appear to be a text file.\nPlease check the file type (.txt) and try again.")
    sys.exit(0)
  
try:
  barcodes = [x.strip('\n') for x in open(inFile).readlines()]
except IOError:  
  print("The text file \"" + os.path.realpath(inFile) + "\" could not be found.\nPlease try again with a valid filepath.") 
  sys.exit(0)

while True:
  ## Attempt login ##
  loginCred = login()

  ## Begin HTML requests ##
  # Store the cookies and create an opener that will hold them
  cj = http.cookiejar.CookieJar()
  opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))

  # Add our headers
  opener.addheaders = [('User-agent', 'KohaPoolPicklist')]

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

barcodes = list(filter(None, barcodes))
barcodeList = ""
for barcode in barcodes:
  if re.match("\d{14}",barcode):
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
lostIdx = 0
damagedIdx = 0
otherStatusIdx = 0
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
  elif headers[i].get_text().strip() == "Lost status":
    lostIdx = i
  elif headers[i].get_text().strip() == "Damaged status":
    damagedIdx = i
  elif headers[i].get_text().strip() == "Other item status":
    otherStatusIdx = i
  elif headers[i].get_text().strip() == "Not for loan status":
    notForLoanIdx = i
  elif headers[i].get_text().strip() == "Checked out":
    checkedOutIdx = i

results = soup.find(id="itemst").tbody.find_all('tr')
pullItems = []
thisMonth = datetime.date.today().strftime('%m-%Y')
pullMonth = (datetime.date.today() + relativedelta(months=+6)).strftime('%m-%Y')
branchCode = str.upper(loginCred[0][:3]) if not args.branchcode else args.branchcode

for i in range(len(results)):
  result = results[i].find_all('td')

  withdrawn = str(result[withdrawnIdx].get_text().strip()) if withdrawnIdx != 0 else ""
  lost = str(result[lostIdx].get_text().strip()) if lostIdx != 0 else ""
  damaged = str(result[damagedIdx].get_text().strip()) if damagedIdx != 0 else ""
  otherStatus = str(result[otherStatusIdx].get_text().strip()) if otherStatusIdx != 0 else ""
  notForLoan = str(result[notForLoanIdx].get_text().strip())  if notForLoanIdx != 0 else ""
  checkedOut = ""

  itemStatus = withdrawn;
  itemStatus += "<br />" + lost if itemStatus else lost
  itemStatus += "<br />" + damaged if itemStatus else damaged
  itemStatus += "<br />" + otherStatus if itemStatus else otherStatus
  itemStatus += "<br />" + notForLoan if itemStatus else notForLoan
  if not itemStatus:
    itemStatus = "OK"
  
  if checkedOutIdx != 0:
    checkedOutStr = str(result[checkedOutIdx].get_text().strip())
    if checkedOutStr:
      checkedOut = "Yes"
  pullItems.append(Item(result[titleIdx].a.get_text(),result[collectionIdx].get_text(),result[locationIdx].get_text(),result[callNumIdx].get_text(),result[barcodeIdx].get_text(), itemStatus, checkedOut))

sortedItems = sorted(pullItems, key=attrgetter('location','collection','callNum','title'))

if args.output:
  outFile = str(args.output)
  if outFile[-5:] != '.html':
    outFile += '.html'
else:
  outFile = str(os.path.dirname(os.path.realpath(inFile)) + directorySlash + branchCode + "-POOL-" + sortedItems[0].collection.replace(' ','-') + "-PULL-ON-" + pullMonth + ".html")

f = open(outFile, 'w')
f.write("<html>\n<head>\n<style>\nth{font-weight: bold;}td{padding:5px 7px;}</style></head>\n<body>\n")
f.write("<p>[POOL ITEMS] " + sortedItems[0].collection + "</p>")
f.write("<p>Arrived at "+ branchCode + " " +  thisMonth + ", to be pulled " + pullMonth + "</p>")
f.write("<table>\n<tr>\n<th>Call #</th>\n<th>Title</th>\n<th>Barcode</th>\n<th>Item status</th>\n<th>Checked out?</th>\n</tr>\n")
for item in sortedItems:
  
  f.write("<tr>\n<td>"+str(item.callNum)+"</td>\n<td>"+str(item.title)+"</td>\n<td>"+str(item.barcode)+"</td>\n<td>"+str(item.status)+"</td>\n<td>"+str(item.checkedOut)+"</td>\n</tr>\n")
f.write("</table>\n</body>\n</html>")
f.close()

webbrowser.open(outFile,new=new)

print ('Output saved to:\n' + outFile)
