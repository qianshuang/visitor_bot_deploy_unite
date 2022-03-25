# -*- coding: utf-8 -*-

import pickle

import marisa_trie
import redis

from jieba.analyse import ChineseAnalyzer
from whoosh.fields import Schema, TEXT
from whoosh.index import create_in
from whoosh.qparser import QueryParser
from whoosh.query import FuzzyTerm

from common import *

# primary data type
r = redis.Redis()
print(r.set('foo', 'bar'))
print(r.get('foo'))

# trie
trie = marisa_trie.Trie(["我是谁？", "你叫什么名字？"])
print(r.hset("bot_trie", "bot1", pickle.dumps(trie)))
print(pickle.loads(r.hget('bot_trie', 'bot1')).keys("我"))

# whoosh
schema = Schema(content=TEXT(stored=True, analyzer=ChineseAnalyzer(stoplist=None)))
ix = create_in("bot_resources/bot1/index", schema)
writer = ix.writer()
for line in read_file("bot_resources/bot1/intents.txt"):
    writer.add_document(content=line)
writer.commit()
print(r.hset("bot_whoosh", "bot1", pickle.dumps(ix)))

ix = pickle.loads(r.hget('bot_whoosh', 'bot1'))
qp = QueryParser("content", ix.schema, termclass=FuzzyTerm)  # default edit distance maxdist = 1，q长度为1时自动是0
query = qp.parse("我")
results = ix.searcher().search(query)
print(results)
