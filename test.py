# -*- coding: utf-8 -*-

# from common import *
# from fuzzywuzzy import fuzz
# from fuzzywuzzy import process
# from fuzzyfinder import fuzzyfinder

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

# print(process.extract("howmach", ["howmuchisthisapple", "你是谁"], limit=10))

# suggestions = fuzzyfinder('abc', ['defabca', 'abcd', 'aagbec', 'xyz', 'qux'])
# print(list(suggestions))

# lines = read_file("bot_resources/HE long version4/intents.txt")
# start = datetime.datetime.now()
# suggestions = fuzzyfinder('setting up my quickbook', lines)
# print(list(suggestions))
# print(time_cost(start))
import Levenshtein

print(Levenshtein.ratio("wojiaolihuanyin", "wojiaolihaanyin"))
