# -*- coding: utf-8 -*-

# from fuzzywuzzy import fuzz
from fuzzywuzzy import process

#
# print(fuzz.ratio("this is a 我 test", "this is a test!"))
# print(fuzz.partial_ratio("this is a test", "this is a test!"))
# print(fuzz.token_sort_ratio("fuzzy wuzzy was a bear", "wuzzy fuzzy was a bear"))
# print(fuzz.token_set_ratio("fuzzy was a bear", "fuzzy fuzzy was a bear"))
#
# choices = ["Atlanta Falcons", "New York Jets", "New York Giants", "Dallas Cowboys"]
# print(process.extract("new york jets", choices, limit=2))
# print(process.extractOne("cowboys", choices))

# import string
# from zhon.hanzi import punctuation
#
# q = "...！   i am Jim....    。。。。！"
# print(q.strip(string.punctuation).strip(punctuation).strip())
# print(punctuation)

print(process.extract("howmach", ["howmuchisthisapple", "你是谁"], limit=10))
