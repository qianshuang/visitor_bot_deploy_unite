# -*- coding: utf-8 -*-

import json

import Levenshtein
from common import *

from flask import Flask, jsonify

print(Levenshtein.ratio(get_pinyin("woshi中gu人"), get_pinyin("我是中国人")))

result = {
    "bot_name": "bot1",
    "query": "芷\若"
}
# ori_rd = str(result)
# print(ori_rd)

# ori_rd = re.sub(r"\\", "", ori_rd)
# print(ori_rd)
ori_rd = json.dumps(result)
print(ori_rd)

resq_data = json.loads(ori_rd)
print(resq_data)
