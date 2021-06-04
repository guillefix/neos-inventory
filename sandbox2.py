from http.server import BaseHTTPRequestHandler, HTTPServer
import re
import numpy as np

from fuzzywuzzy import fuzz
from fuzzywuzzy import process

import re
import json
from collections import Counter
# records = json.loads(open("new_inventory_index.txt","r",encoding="utf-8").read())
#
# # records[0]
#
# # len(records)
#
# records = list(filter(lambda x: ("name" in x and x["name"] is not None) and ("tags" in x and x["tags"] is not None) and ("thumbnailUri" in x and x["thumbnailUri"] is not None), records))
#
# tags = list(map(lambda x: x["tags"], records))
# names = list(map(lambda x: x["name"], records))
# paths = list(map(lambda x: sum(map(lambda y: list(map(lambda z: z.lower().strip(), re.split(' |-|_',y))),x["path"].split("\\")),[]), records))
# image_thumbnails = list(map(lambda x: "thumbnails/"+x["id"]+".webp", records))

import os
dir_path = os.path.dirname(os.path.realpath(__file__))
# dir_path = "D:/code/neos/neos-inventory"

from PIL import Image
# Image.open(dir_path+"/thumbnails/R-000a2f01-1d22-4108-994e-02a030ec8968.webp")
from pathlib import Path
# Image.open(Path('D:/code/neos/neos-inventory/thumbnails/R-000a2f01-1d22-4108-994e-02a030ec8968.webp'))
# Image.open(Path(r'C:\Users\Guillermo Valle\Pictures\R-000a2f01-1d22-4108-994e-02a030ec8968.webp'))
# Image.open("C:/Users/Guillermo Valle/Pictures/R-000a2f01-1d22-4108-994e-02a030ec8968.webp")
# Image.open(open("a.jpg","rb"))
Image.open("a.jpg")
