# MPL Pool Item Picklist Generator
This script generates a pull list HTML file from a plain text file of barcode numbers. Each library barcode number should be given its own line without punctuation. This is intended for use by LibLime Koka users within the South Central Library System in Wisconsin.

## System requirements
* Python 3.*
* BeautifulSoup

## Usage
```
poolPL.py [-h] [-b BRANCHCODE] -i INPUT [-o OUTPUT]

Arguments:
-h, --help        Show this help message and exit
-b BRANCHCODE, --branchcode BRANCHCODE
                  Override the branch code for the library at which the picklist was generated
-i INPUT, --input INPUT
                  Input text file name; This file's extension must end in .txt and the provided filename will be relative to the present working directory
```
