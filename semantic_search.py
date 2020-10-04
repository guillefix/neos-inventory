from sentence_transformers import SentenceTransformer
model = SentenceTransformer('distilbert-base-nli-mean-tokens')
sentences = ['This framework generates embeddings for each input sentence',
    'Sentences are passed as a list of string.',
    'The quick brown fox jumps over the lazy dog.']
sentence_embeddings = model.encode(sentences)
for sentence, embedding in zip(sentences, sentence_embeddings):
    print("Sentence:", sentence)
    print("Embedding:", embedding)
    print("")

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
sentence_embeddings = model.encode(things2)
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
    print([things2[i] for i in indices])
    # process.extract("multitool", things2, limit=n)
    results2 = process.extract(query_str, {i:x for i,x in enumerate(things2)}, limit=n)
    print(results2)
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
    return [things2[key] for key,value in results.most_common(n)]

# np.where(["multitool" in t.lower() for t in things2])

records[23]
# things2[5610]

search("H3 multitool",10)
search("plant",30)
search("wallet",30)

search("wet",10)

search("happiness",10)

search("do not open this",10)

search("how do i go there",10)

search("drink",10)

search("superman vs",10)

search("egypt",10)

search("canada",10)

search("a thing to calculate with numbers",10)

search("transistor",10)

search("",20)


fuzz.ratio("this is a test", "this is a test!aaaaaaaaaaaaaaaaaaaaaaaaaa")
