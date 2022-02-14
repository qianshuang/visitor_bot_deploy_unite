# -*- coding: utf-8 -*-

import Levenshtein
import pandas as pd
from config import *


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


def whoosh_search(bot_n, query):
    query = bot_qp[bot_n].parse(query)
    print(query)

    results = bot_searcher[bot_n].search(query)
    # 还原源文本
    res = []
    for r in results:
        res.extend(r.values())
    # return res
    return [bot_intents_whoosh_dict[bot_n][r] for r in res]


def smart_hint(bot_n, query):
    query = pre_process_4_trie(query)
    result = bot_trie[bot_n].keys(query)
    return list(result)


def leven(bot_n, query):
    query1 = pre_process_4_trie(query)
    query2 = get_pinyin(query)

    res = []
    for k in bot_intents_dict[bot_n].keys():
        score1 = Levenshtein.ratio(k[:len(query1)], query1)
        score2 = Levenshtein.ratio(k[:len(query2)], query2)
        if score1 >= 0.8 or score2 >= 0.8:
            res.append(k)
    return res
