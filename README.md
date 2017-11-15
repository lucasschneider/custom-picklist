# Overview
This script generates a pull list HTML file from a plain text file of barcode numbers. Each library barcode number should be given its own line without punctuation. This is intended for use by LibLime Koka users within the South Central Library System in Wisconsin.

## System requirements
* Python 3.*
* BeautifulSoup

## Usage
```
poolPL.py [-h] [-b BRANCHCODE] -i INPUT [-o OUTPUT]

Optional rguments:
-h, --help        Show this help message and exit
-b BRANCHCODE, --branchcode BRANCHCODE
                  Override the branch code for the library at which the picklist was generated;
                  default based on the Koha login username
-i INPUT, --input INPUT
                  Input text filename; This file's extension must end in .txt and the provided filename
                  will be relative to the present working directory; default based on on GUI input
-o OUTPUT, --output OUTPUT
                  Output web filename; This file's extension will end in .html whether or not it is
                  specified and will be created relative to the location of the input file; default
                  saved to same directory as filepath
```
