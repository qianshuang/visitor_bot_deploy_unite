# -*- coding: utf-8 -*-

import Levenshtein
from common import *

print(Levenshtein.ratio(get_pinyin("woshi中gu人"), get_pinyin("我是中国人")))
