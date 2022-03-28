# -*- coding: utf-8 -*-

import shutil
import json

from helper import *

from flask import Flask, jsonify
from flask import request

app = Flask(__name__)


@app.route('/search', methods=['GET', 'POST'])
def search():
    """
    input json:
    {
        "bot_name": "xxxxxx",  # 要查询的bot name
        "query": "xxxxxx",  # 用户query
        "size": 10,         # 最大返回大小，默认10
        "cn_enable": true   # 默认为false，不开启中文拼音强化功能，性能较差
    }

    return:
    {   'code': 0,
        'msg': 'success',
        'data': []
    }
    """
    print("process id:", os.getpid())

    ori_rd = request.get_data(as_text=True)
    ori_rd = ori_rd.replace('\\"', ',')
    ori_rd = ori_rd.replace('\\', '')
    resq_data = json.loads(ori_rd)

    bot_n = resq_data["bot_name"].strip()
    data = resq_data["query"].strip(string.punctuation).strip(punctuation).strip()
    size = int(resq_data["size"]) if "size" in resq_data else default_size
    cn_enable = resq_data["cn_enable"] if "cn_enable" in resq_data else False

    if pre_process_4_trie(data) == "":
        return {'code': 0, 'msg': 'success', 'data': []}

    # 0. 同步Redis缓存
    rsync(bot_n)

    # 1. 前缀搜索
    trie_res = smart_hint(bot_n, data)
    # 2. 断句前缀搜索
    if_split = bool(re.search(r'[,，.。？?！!（(”"]', data))
    if if_split:
        trie_res = trie_res + smart_hint(bot_n, re.split(r'[,，.。？?！!（(”"]', data)[-1].strip())
    if cn_enable:
        # 3. 拼音前缀搜索
        data_pinyin = get_pinyin(data)
        trie_res = trie_res + smart_hint(bot_n, data_pinyin)
        # 4. 断句拼音前缀搜索
        if if_split:
            trie_res = trie_res + smart_hint(bot_n, re.split(r'[,，.。？?！!（(”"]', data_pinyin)[-1].strip())

    # 5. 全文检索
    whoosh_res = whoosh_search(bot_n, data, size)
    # whoosh_res = rank(bot_n, whoosh_res)

    priorities_res = get_priorities(bot_n)
    ranked_trie_res = rank(bot_n, list(set(trie_res) - set(priorities_res)))

    # 6. 编辑距离（仅在中文bot开启）
    leven_res = []
    if cn_enable:
        if len(set(priorities_res + ranked_trie_res + whoosh_res)) < size:
            if if_split:
                data = re.split(r'[,，.。？?！!（(”"]', data)[-1].strip()
            leven_res = leven(bot_n, data)
    ranked_leven_res = rank(bot_n, list(set(leven_res) - set(priorities_res + ranked_trie_res + whoosh_res)))

    ori_res = priorities_res + ranked_trie_res + whoosh_res + ranked_leven_res
    final_res = sorted(set(ori_res), key=ori_res.index)  # 保序去重
    return {'code': 0, 'msg': 'success', 'data': final_res[:size]}


@app.route('/callback', methods=['GET', 'POST'])
def callback():
    """
    {
        "bot_name": "xxxxxx",  # 要操作的bot name
        "intent": "xxxxxx"  # 匹配到的标准答案
    }
    """
    resq_data = json.loads(request.get_data())
    bot_n = resq_data["bot_name"].strip()
    intent = resq_data["intent"].strip()

    # 回写recent文件
    rk_bot_recent = "bot_recent&" + bot_n
    r.lrem(rk_bot_recent, 0, intent)
    r.lpush(rk_bot_recent, intent)

    # 回写frequency文件
    rk_bot_frequency = "bot_frequency&" + bot_n
    r.hincrby(rk_bot_frequency, intent)

    result = {'code': 0, 'msg': 'success', 'data': resq_data}
    return jsonify(result)


@app.route('/refresh', methods=['GET', 'POST'])
def refresh():
    """
    更新intents.txt、priority.txt后，需要手动刷新才生效
    {
        "bot_name": "xxxxxx",  # 要操作的bot name
        "operate": "upsert",  # 操作。upsert：更新或新增；delete：删除
    }
    """
    start = datetime.datetime.now()

    resq_data = json.loads(request.get_data())
    bot_n = resq_data["bot_name"].strip()
    operate = resq_data["operate"].strip()

    # 加锁
    bot_lock = redis_lock.Lock(r, "lock_" + bot_n)
    if bot_lock.acquire(blocking=False):
        if operate == "upsert":
            build_bot_intents_dict_trie(bot_n)
            print(bot_n, "intents dict and trie finished rebuilding...")

            index_dir_ = os.path.join(BOT_SRC_DIR, bot_n, "index")
            if not os.path.exists(index_dir_):
                os.mkdir(index_dir_)
            build_bot_whoosh_index(bot_n, index_dir_)
            print(bot_n, "whoosh index finished rebuilding...")

            build_bot_priorities(bot_n)
            print(bot_n, "priority file finished reloading...")

            r_v = r.hincrby("bot_version", bot_n)
            r.hset("bot_version&" + bot_n, str(os.getpid()), r_v)

            ret = {'code': 0, 'msg': 'success', 'time_cost': time_cost(start)}
        elif operate == "delete":
            # 删除bot
            bot_path = os.path.join(BOT_SRC_DIR, bot_n)
            if os.path.exists(bot_path):
                shutil.rmtree(bot_path)
            r.delete("bot_intents&" + bot_n)
            r.delete("bot_intents_whoosh&" + bot_n)
            r.delete("bot_recent&" + bot_n)
            r.delete("bot_frequency&" + bot_n)
            r.delete("bot_priorities&" + bot_n)
            r.delete("bot_version&" + bot_n)
            r.hdel("bot_trie", bot_n)
            r.hdel("bot_whoosh", bot_n)
            r.hdel("bot_version", bot_n)

            del_dict_key(bot_intents_dict, bot_n)
            del_dict_key(bot_intents_whoosh_dict, bot_n)
            del_dict_key(bot_recents, bot_n)
            del_dict_key(bot_frequency, bot_n)
            del_dict_key(bot_priorities, bot_n)
            del_dict_key(bot_trie, bot_n)
            del_dict_key(bot_searcher, bot_n)
            del_dict_key(bot_qp, bot_n)

            ret = {'code': 0, 'msg': 'success', 'time_cost': time_cost(start)}
        else:
            ret = {'code': -1, 'msg': 'unsupported operation', 'time_cost': time_cost(start)}

        bot_lock.release()
        return ret
    else:
        return {'code': -2, 'msg': 'someone is refreshing this bot, please wait.', 'time_cost': time_cost(start)}


if __name__ == '__main__':
    app.run()
