# -*- coding: utf-8 -*-


import Levenshtein

k = "Woyouyigepingguo"
query2 = "Woaiyige"
print(Levenshtein.ratio(k[:len(query2)], query2))
