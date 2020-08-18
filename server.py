from http.server import BaseHTTPRequestHandler, HTTPServer
import re

import json
records = json.loads(open("InventoryScrap.txt","r",encoding="utf-8").read())

len(records)

# things = list(map(lambda x: x["tags"], records))
#%%
# records = list(filter(lambda x: x["recordType"]=="object",records))
# things = list(map(lambda x: x["tags"], records))
records = list(filter(lambda x: x["RecordType"]=="object",records))
things = list(map(lambda x: x["Tags"], records))
# things2 = list(map(lambda x: x["Name"], records))
things2 = list(map(lambda x: sum(map(lambda y: list(map(lambda z: z.lower().strip(), re.split(' |-|_',y))),x["Path"].split("\\")),[]), records))

# things[0]

import numpy as np
#%%

class S(BaseHTTPRequestHandler):
    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self):
        print(self.path)
        self._set_headers()
        query=self.path[1:]
        results_ids=[]
        results_str=""
        for i,thing in enumerate(things):
            if query.lower() in thing or query.lower() in things2[i]:
                results_ids.append(i)
                results_str += records[i]["ThumbnailURI"].split(".")[0]+"|"+records[i]["AssetURI"].split(".")[0]+","

        # i = np.random.choice(results)

        self.wfile.write(bytes(str(results_str), "utf-8"))

    def do_HEAD(self):
        self._set_headers()

    def do_POST(self):
        # Doesn't do anything with posted data
        self._set_headers()
        self.wfile.write(bytes("<html><body><h1>POST!</h1></body></html>", "utf-8"))

def run(server_class=HTTPServer, handler_class=S, port=80):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print('Starting httpd...')
    httpd.serve_forever()

run(port=42069)
