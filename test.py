# -*- coding: utf-8 -*-


import Levenshtein

k = "我是中国"
query2 = "我爱中国"
print(Levenshtein.ratio(k[:len(query2)], query2))
