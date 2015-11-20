#!/usr/bin/python

import getpass
import argparse
import http.cookiejar
import urllib
import urllib.request
#import urllib.error
from bs4 import BeautifulSoup

## Function to login into Koha before data extraction ##
def login():
    user = input("Username [%s]: " % getpass.getuser())
    if not user:
        user = getpass.getuser()

    p1 = getpass.getpass()

    return [user, p1]

loginCred = login()

## Parse for proper argumets ##
#parser = argparse.ArgumentParser(description='This is a demo script by nixCraft.')
#parser.add_argument('-i','--input', help='Input file name',required=True)
#parser.add_argument('-o','--output',help='Output file name', required=True)
#args = parser.parse_args()
 
## show values ##
#print ("Input file: %s" % args.input )
#print ("Output file: %s" % args.output )

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

url = 'http://scls-staff.kohalibrary.com/cgi-bin/koha/catalogue/search.pl'
req = urllib.request.Request(url)

# Make the request and read the response
resp = urllib.request.urlopen(req)
html = resp.read()

soup = BeautifulSoup(html, 'html.parser')
print(soup.prettify(encoding='utf-8'))