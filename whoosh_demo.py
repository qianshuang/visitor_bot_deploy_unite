# -*- coding: utf-8 -*-

import json

from flask import Flask
from flask import request
from gevent import pywsgi
from jieba.analyse import ChineseAnalyzer

from whoosh import qparser
from whoosh.analysis import StandardAnalyzer
from whoosh.index import create_in
from whoosh.fields import *
from whoosh.qparser import QueryParser
from whoosh.query import FuzzyTerm
from whoosh.writing import AsyncWriter

from common import *

import os

app = Flask(__name__)

# schema = Schema(content=TEXT(stored=True, analyzer=StandardAnalyzer(stoplist=None)))
schema = Schema(content=TEXT(stored=True, analyzer=ChineseAnalyzer(stoplist=None)))
if not os.path.exists("index"):
    os.mkdir("index")
ix = create_in("index", schema)
# writer = ix.writer()
writer = AsyncWriter(ix)
for line in read_file("bot_resources/bot1/intents.txt"):
    writer.add_document(content=line)
writer.commit()
print("building index finished...")

searcher = ix.refresh().searcher().refresh()


@app.route('/search', methods=['GET', 'POST'])
def search():
    resq_data = json.loads(request.get_data())
    query = resq_data["query"].strip()

    qp = QueryParser("content", ix.schema, termclass=FuzzyTerm)  # default edit distance maxdist = 1，q长度为1时自动是0
    # qp.add_plugin(qparser.FuzzyTermPlugin())

    # query = pre_process(query)
    # query = " ".join([w + "~" for w in query.split(" ")])

    print(query)
    query = qp.parse(query)
    print(query)

    results = searcher.search(query)
    print(results)
    # print(results.score(0))
    print(results.top_n)

    res = []
    for r in results:
        print(r)
        res.extend(r.values())
    return {'code': 0, 'msg': 'success', 'data': res}


if __name__ == '__main__':
    server = pywsgi.WSGIServer(('0.0.0.0', 8089), app)
    server.serve_forever()
