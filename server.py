from http.server import BaseHTTPRequestHandler, HTTPServer
import re

# import json
# records = json.loads(open("InventoryScrap.txt","r",encoding="utf-8").read())
#
# len(records)
#
# # things = list(map(lambda x: x["tags"], records))
# #%%
# # records = list(filter(lambda x: x["recordType"]=="object",records))
# # things = list(map(lambda x: x["tags"], records))
# records = list(filter(lambda x: x["RecordType"]=="object",records))
# things = list(map(lambda x: x["Tags"], records))
# # things2 = list(map(lambda x: x["Name"], records))
# things2 = list(map(lambda x: sum(map(lambda y: list(map(lambda z: z.lower().strip(), re.split(' |-|_',y))),x["Path"].split("\\")),[]), records))

from sentence_transformers import SentenceTransformer
model = SentenceTransformer('distilbert-base-nli-mean-tokens')

from fuzzywuzzy import fuzz
from fuzzywuzzy import process

import re
import json
from collections import Counter
records = json.loads(open("InventoryScrap.txt","r",encoding="utf-8").read())

things = list(map(lambda x: x["Tags"], records))
things2 = list(map(lambda x: x["Name"], records))
things3 = list(map(lambda x: sum(map(lambda y: list(map(lambda z: z.lower().strip(), re.split(' |-|_',y))),x["Path"].split("\\")),[]), records))

len(records)
things2 = list(filter(lambda x: x is not None, things2))
# sentence_embeddings = model.encode(things2)
# import numpy as np
# np.save("sentence_embeddings",sentence_embeddings)
## TODO: use pre-computed embeddings for next time putting in Neos
sentence_embeddings = np.load("sentence_embeddings.npy")
things2 = [t.encode('ascii', 'ignore') for t in things2]

import numpy as np
def search(query_str,n=3,fuzzy_weight=0.5):
    query_embedding = model.encode(query_str)

    def query(vec,embs,n=3):
        # index = np.argmax(np.dot(embs,vec/np.linalg.norm(vec)))
        # scores = np.dot(embs,vec/np.linalg.norm(vec))
        # nonlocal scores
        scores = -np.linalg.norm(embs-vec,axis=1)
        indices = np.argsort(scores)
        # for i in indices[-n:][::-1]:
        #     scores1.append(scores[i])
            # print(scores[i])
        return scores,indices[-n:]

    scores,indices = query(query_embedding,sentence_embeddings,n)
    # results1 = [(i,1+scores[i]/32) for i in indices]
    results1 = Counter({i:(1+scores[i]/32)**2 for i in indices})
    # print([things2[i] for i in indices])
    # process.extract("multitool", things2, limit=n)
    results2 = process.extract(query_str, {i:x for i,x in enumerate(things2)}, limit=n)
    # print(results2)
    results2 = Counter({x[2]:(fuzzy_weight*x[1]/100)**2 for x in results2})
    for key,value in list(results1.most_common()):
        # if key not in results2:
        results2[key] = (fuzzy_weight*fuzz.WRatio(query_str,things2[key])/100)**2
            # results2[key] = (fuzzy_weight*fuzz.ratio(query_str,things2[key])/100)**2

    for key,value in list(results2.most_common()):
        # if key not in results1:
        results1[key] = (1+scores[key]/32)**2

    # results = Counter()
    # for key,value in list(results2.most_common()):
    #     results[key] = np.maximum(results1[key],value) + results1[key] + value
    results = results1 + results2
    return [key for key,value in results.most_common(n)]

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
        # for i,thing in enumerate(things):
        #     if query.lower() in thing or query.lower() in things2[i]:
        indices = search(query.lower(),100)
        for i in indices:
            results_ids.append(i)
            r=records[i]
            results_str += r["ThumbnailURI"].split(".")[0]+"|"+r["AssetURI"]+"|"+r["Name"]+"|"+r["OwnerName"]+"|"+r["Path"]+","

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

run(port=6969)
