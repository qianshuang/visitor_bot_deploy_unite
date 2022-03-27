# -*- coding: utf-8 -*-

import Levenshtein
import pandas as pd

from whoosh.qparser import QueryParser
from whoosh.query import FuzzyTerm

from config import *


def rsync(bot_n):
    bot_version = r.hget("bot_version", bot_n)
    bot_process_version = r.hget("bot_version&" + bot_n, str(os.getpid()))

    if bot_version != bot_process_version:
        print("starting rsync...")
        bot_intents_dict[bot_n] = r_to_dict(r, "bot_intents&" + bot_n)
        bot_intents_whoosh_dict[bot_n] = r_to_dict(r, "bot_intents_whoosh&" + bot_n)
        bot_priorities[bot_n] = r_to_str_list(r, "bot_priorities&" + bot_n)
        bot_recents[bot_n] = r_to_str_list(r, "bot_recent&" + bot_n)
        bot_frequency[bot_n] = r_to_dict(r, "bot_frequency&" + bot_n, "int")
        bot_trie[bot_n] = r_get_pickled(r, "bot_trie", bot_n)
        bot_whoosh[bot_n] = r_get_pickled(r, "bot_whoosh", bot_n)
        r.hset("bot_version&" + bot_n, str(os.getpid()), int(bot_version))


def rank(bot_n, trie_res):
    frequency_ = []
    recents_ = []
    for item in trie_res:
        if item in bot_frequency[bot_n]:
            frequency_.append(bot_frequency[bot_n][item])
        else:
            frequency_.append(0)

        if item in bot_recents[bot_n]:
            recents_.append(len(bot_recents[bot_n]) - bot_recents[bot_n].index(item))
        else:
            recents_.append(0)
    df = pd.DataFrame({"trie_res": trie_res, "frequency": frequency_, "recents": recents_})
    df.sort_values(by=["frequency", "recents"], ascending=False, inplace=True)
    return df["trie_res"].values.tolist()


def whoosh_search(bot_n, query, lim=10):
    ix_ = bot_whoosh[bot_n]
    qp_and_ = QueryParser("content", ix_.schema, termclass=FuzzyTerm)
    # qp_and_.add_plugin(qparser.FuzzyTermPlugin())

    query = qp_and_.parse(query)
    # print(query)

    results = ix_.searcher().search(query, limit=lim)
    # 还原原文本
    res = []
    for r_ in results:
        res.extend(r_.values())
    return [bot_intents_whoosh_dict[bot_n][r_] for r_ in res]


def smart_hint(bot_n, query):
    query = pre_process_4_trie(query)
    result = bot_trie[bot_n].keys(query)
    return list(result)


# def leven(bot_n, query, lim=10):  # 有性能问题
#     query1 = pre_process_4_trie(query)
#     query2 = get_pinyin(query1)
#
#     q2_res = process.extract(query2, bot_intents_dict[bot_n].keys(), limit=lim)
#     final_res = [bot_intents_dict[bot_n][r[0]] for r in q2_res if r[1] >= 75]
#     return final_res

def leven(bot_n, query):
    query1 = pre_process_4_trie(query)
    query2 = get_pinyin(query1)

    res = []
    for k in bot_intents_dict[bot_n].keys():
        if len(query2) <= len(k):
            for i in range(len(k) - len(query2)):
                score2 = Levenshtein.ratio(k[i:i + len(query2)], query2)
                if score2 >= 0.8:
                    res.append(bot_intents_dict[bot_n][k])
                    break
    return res


def get_priorities(bot_n):
    return bot_priorities[bot_n]
