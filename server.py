from http.server import BaseHTTPRequestHandler, HTTPServer
import re
import numpy as np

from urllib.parse import urlparse
from urllib.parse import parse_qs

from multiprocessing import Process
import multiprocessing

# from fuzzywuzzy import fuzz
# from fuzzywuzzy import process
from rapidfuzz import process
from rapidfuzz import fuzz

import re
import json
from collections import Counter
import sys

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

import numpy as np

use_bert = False
def query(vec,embs,n=3):
    # index = np.argmax(np.dot(embs,vec/np.linalg.norm(vec)))
    if use_bert:
        scores = np.dot(embs,vec/np.linalg.norm(vec))
    else:
        scores = np.dot(embs,vec[0]/np.linalg.norm(vec[0]))
    # nonlocal scores
    # scores = -np.linalg.norm(embs-vec,axis=1)
    indices = np.argsort(scores)
    # for i in indices[-n:][::-1]:
    #     scores1.append(scores[i])
        # print(scores[i])
    return scores,indices[-n:]

def queryParal(procid,vec,embs,n,return_dict):
    scores,indices = query(vec,embs,n=n)
    return_dict[procid] = scores,indices

if __name__ == "__main__":

    # use_bert = True
    if use_bert:
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer('distilbert-base-nli-mean-tokens')
    else:
        from clip_embeddings import embed_text, embed_image

    records = json.loads(open("new_inventory_index.txt","r",encoding="utf-8").read())

    # records[0]

    # len(records)

    records = list(filter(lambda x: ("name" in x and x["name"] is not None) and ("tags" in x and x["tags"] is not None) and ("thumbnailUri" in x and x["thumbnailUri"] is not None), records))
    bad_thumbnails = ["R-18fb0f87-a8dc-426e-85b6-835a96d74ec3","R-47e0eba3-b408-45a6-a25d-771533803680","R-72815276-5acf-4b2f-a6f4-a4ecfa7e284d","R-84e14452-9d93-449a-8c77-910c62694a03","R-8e023894-dc52-43c4-a575-e09db0e3751c","R-a8c347ef-76fc-4759-b9c8-09a6c4c02c3d","R-aa261a5b-747e-49e6-a8a2-a3dc926dc3e7","R-afa0122b-faab-4bf3-a537-938d0a053e55","R-f6fe4528-f67c-46a5-8fb2-d18fd2f471de"]
    records = list(filter(lambda x: x["id"] not in bad_thumbnails, records))

    tags = list(map(lambda x: x["tags"], records))
    names = list(map(lambda x: x["name"], records))
    paths = list(map(lambda x: sum(map(lambda y: list(map(lambda z: z.lower().strip(), re.split(' |-|_',y))),x["path"].split("\\")),[]), records))
    image_thumbnails = list(map(lambda x: "thumbnails/"+x["id"]+".webp.jpg", records))

    len(records)
    # image_embeddings = embed_image(image_thumbnails)
    # sentence_embeddings = embed_text(names)
    # sentence_embeddings = model.encode(names)
    # np.save("sentence_embeddings",sentence_embeddings)
    # np.save("sentence_embeddings_clip",sentence_embeddings)
    # np.save("image_embeddings_clip",image_embeddings)
    ## use pre-computed embeddings for next time putting in Neos
    if use_bert:
        sentence_embeddings = np.load("sentence_embeddings.npy")
        normalized_sentence_embeddings = sentence_embeddings / np.linalg.norm(sentence_embeddings,axis=1, keepdims=True)
    else:
        sentence_embeddings = np.load("sentence_embeddings_clip.npy")
        normalized_sentence_embeddings = sentence_embeddings / np.linalg.norm(sentence_embeddings,axis=1, keepdims=True)
        image_embeddings = np.load("image_embeddings_clip.npy")
        normalized_image_embeddings = image_embeddings / np.linalg.norm(image_embeddings,axis=1, keepdims=True)
    # names = [t.encode('ascii', 'ignore') for t in names]
    # names = [(n if n != "" else " ") for n in names]

    # sentence_weight = 0.5
    default_text_weight = 0.4
    default_image_weight = 0.6
    # default_fuzzy_weight = 0.5
    default_fuzzy_weight = 0.2

    manager = multiprocessing.Manager()

    # def search(query_str,n=3,fuzzy_weight=0.5):
    def search(query_str,n=3,fuzzy_weight=default_fuzzy_weight,text_weight=default_text_weight,image_weight=default_image_weight):
        print(query_str)
        if use_bert:
            query_embedding = model.encode(query_str)
        else:
            # import time
            # start_time = time.time()
            query_embedding = embed_text(query_str)
            # print("--- %s seconds ---" % (time.time() - start_time))

        if use_bert:
            embeddings = normalized_sentence_embeddings
            scores,indices = query(query_embedding,embeddings,n)
            results1 = Counter({i:text_weight*scores[i] for i in indices})
            # print(results1)
            if fuzzy_weight > 0:
                # results2 = process.extract(query_str, {i:x for i,x in enumerate(names)}, limit=n)
                results2 = process.extract(query_str, names, scorer=fuzz.WRatio, limit=n)
                results2 = Counter({x[2]:(fuzzy_weight*x[1]/100) for x in results2})
                # print(results2)
                for key,value in list(results1.most_common()):
                    results2[key] = fuzzy_weight*fuzz.WRatio(query_str,names[key])/100
                for key,value in list(results2.most_common()):
                    results1[key] = text_weight*scores[key]

                results = results1 + results2
                return [key for key,value in results.most_common(n)]
            else:
                return [key for key,value in results1.most_common(n)]
        else:
            # embeddings = sentence_weight * sentence_embeddings + (1-sentence_weight) * image_embeddings
            # embeddings = sentence_weight * normalized_sentence_embeddings + (1-sentence_weight) * normalized_image_embeddings
            # import time
            # start_time = time.time()
            scores_text,indices_text = query(query_embedding,normalized_sentence_embeddings,n)
            # print("--- %s seconds ---" % (time.time() - start_time))
            # start_time = time.time()
            scores_images,indices_images = query(query_embedding,normalized_image_embeddings,n)
            # print("--- %s seconds ---" % (time.time() - start_time))

            # return_dict = manager.dict()
            # p = Process(target=queryParal, args=("text",query_embedding,normalized_sentence_embeddings,n, return_dict))
            # p.start()
            # p2 = Process(target=queryParal, args=("images",query_embedding,normalized_image_embeddings,n, return_dict))
            # p2.start()
            # p.join()
            # p2.join()
            # scores_text, indices_text = return_dict["text"]
            # scores_images, indices_images = return_dict["images"]
            results_text = Counter({i:text_weight*scores_text[i] for i in indices_text})
            results_images = Counter({i:image_weight*scores_images[i] for i in indices_images})
            # print(results1)
            if fuzzy_weight > 0:
                import time
                start_time = time.time()
                # results2 = process.extract(query_str, {i:x for i,x in enumerate(names)}, limit=n)
                # print(query_str)
                # print(type(names))
                print(names[0])
                results2 = process.extract(query_str, names, scorer=fuzz.WRatio, limit=n)
                # results2 = process.extract("hahatest", ["test","tost"], scorer=fuzz.WRatio, limit=1)
                print("--- %s seconds ---" % (time.time() - start_time))
                results2 = Counter({x[2]:(fuzzy_weight*x[1]/100) for x in results2})
                # print(results2)
                for key,value in list(results_text.most_common()):
                    results2[key] = fuzzy_weight*fuzz.WRatio(query_str,names[key])/100
                for key,value in list(results_images.most_common()):
                    results2[key] = fuzzy_weight*fuzz.WRatio(query_str,names[key])/100
                for key,value in list(results2.most_common()):
                    results_text[key] = text_weight*scores_text[key]
                    results_images[key] = image_weight*scores_images[key]

                results = results_text + results_images + results2
                return [key for key,value in results.most_common(n)]
            else:
                return [key for key,value in results1.most_common(n)]

    # things[0]

    #%%

    class S(BaseHTTPRequestHandler):
        def _set_headers(self):
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()

        def do_GET(self):
            print(self.path)
            if self.path == "/favicon.ico": return
            self._set_headers()
            # query=self.path[1:]
            query_params = parse_qs(urlparse(self.path).query)
            query = query_params["q"][0] if "q" in query_params else self.path[1:]
            fuzzy_weight = float(query_params["f"][0]) if "f" in query_params else default_fuzzy_weight
            text_weight = float(query_params["t"][0]) if "t" in query_params else default_text_weight
            image_weight = float(query_params["i"][0]) if "i" in query_params else default_image_weight
            print(query)
            results_ids=[]
            results_str=""
            # for i,thing in enumerate(things):
            #     if query.lower() in thing or query.lower() in things2[i]:
            indices = search(query.lower(),100,fuzzy_weight=fuzzy_weight,text_weight=text_weight,image_weight=image_weight)
            for i in indices:
                results_ids.append(i)
                r=records[i]
                thumbnailUri = r["thumbnailUri"].split(".")[0] if "thumbnailUri" in r else ""
                assetUri = r["assetUri"].split(".")[0]+".7zbson" if "assetUri" in r else ""
                name = r["name"].split(".")[0].replace(",",".") if "name" in r else ""
                ownerName = r["ownerName"].split(".")[0] if "ownerName" in r else ""
                path = r["path"].split(".")[0] if "path" in r else ""
                results_str += thumbnailUri+"|"+assetUri+"|"+name+"|"+ownerName+"|"+path+"|,"
                # results_str += name + " " + r["id"] + "\n"

            # i = np.random.choice(results)

            sys.stdout.flush()
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
