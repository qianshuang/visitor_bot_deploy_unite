# -*- coding: utf-8 -*-

import pickle
import string
import os
import re
import datetime
import pypinyin
from zhon.hanzi import punctuation


def open_file(filename, mode='r'):
    return open(filename, mode, encoding='utf-8', errors='ignore')


def read_file(filename):
    if not os.path.exists(filename):
        return []
    return [line.strip() for line in open(filename).readlines() if line.strip() != ""]


def write_file(filename, content):
    open_file(filename, mode="w").write(content)


def write_lines(filename, list_res):
    test_w = open_file(filename, mode="w")
    for j in list_res:
        test_w.write(j + "\n")


def pre_process_4_trie(query):
    # 1. 转小写
    query = query.lower()

    # 2. 去标点
    query = re.sub(r"[%s]+" % punctuation, "", query)
    for c in string.punctuation:
        query = query.replace(c, "")

    # 3. 去空格
    query = re.sub(r'\s+', '', query)
    return query


def get_pinyin(hanz):
    pinyin = pypinyin.lazy_pinyin(hanz, style=pypinyin.NORMAL)
    return re.sub(r'\s+', '', "".join(pinyin))


def time_cost(start, type_="sec"):
    interval = datetime.datetime.now() - start
    if type_ == "sec":
        return interval.total_seconds()
    elif type_ == "day":
        return interval.days


def r_set_pickled(r, name, key, value):
    return r.hset(name, key, pickle.dumps(value))


def r_get_pickled(r, name, key):
    return pickle.loads(r.hget(name, key))


def r_to_str_list(r, name):
    r_list = r.lrange(name, 0, -1)
    return [str(i, encoding='utf-8') for i in r_list]


def r_to_dict(r, name, v_type="str"):
    r_dict = r.hgetall(name)
    if v_type == "int":
        return {str(k, encoding='utf-8'): int(v) for k, v in r_dict.items()}
    return {str(k, encoding='utf-8'): str(v, encoding='utf-8') for k, v in r_dict.items()}


def del_dict_key(dic, key):
    if key in dic:
        del dic[key]
