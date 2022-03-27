# -*- coding: utf-8 -*-

import redis
import redis_lock

import marisa_trie

from whoosh.index import create_in
from whoosh.fields import *
from jieba.analyse import ChineseAnalyzer

from common import *

BOT_SRC_DIR = "bot_resources"
# 默认返回大小
default_size = 10

# 本地缓存
bot_intents_dict = {}
bot_intents_whoosh_dict = {}
bot_priorities = {}
bot_recents = {}
bot_frequency = {}
bot_trie = {}
bot_whoosh = {}

r = redis.Redis()
global_lock = redis_lock.Lock(r, "global_lock")


def build_bot_intents_dict_trie(bot_name):
    rk_bot_intents = "bot_intents&" + bot_name
    INTENT_FILE_ = os.path.join(BOT_SRC_DIR, bot_name, "intents.txt")
    intents_dict_ = {}
    for intent_ in read_file(INTENT_FILE_):
        intent_pro_ = pre_process_4_trie(intent_)
        r.hset(rk_bot_intents, intent_pro_, intent_)
        intents_dict_[intent_pro_] = intent_

        intent_pinyin_ = get_pinyin(intent_pro_)
        r.hset(rk_bot_intents, intent_pinyin_, intent_)
        intents_dict_[intent_pinyin_] = intent_

    all_intents = [str(k) for k in r.hkeys(rk_bot_intents)]
    trie = marisa_trie.Trie(all_intents)
    r_set_pickled(r, "bot_trie", bot_name, trie)

    bot_intents_dict[bot_name] = intents_dict_
    bot_trie[bot_name] = trie


def build_bot_whoosh_index(bot_name, index_dir_):
    rk_bot_intents_whoosh = "bot_intents_whoosh&" + bot_name
    INTENT_FILE_ = os.path.join(BOT_SRC_DIR, bot_name, "intents.txt")
    DICT_FILE_ = os.path.join(BOT_SRC_DIR, bot_name, "userdict.txt")
    intents_dict_ = {}

    schema_ = Schema(content=TEXT(stored=True, analyzer=ChineseAnalyzer(stoplist=None, cachesize=-1)))
    ix_ = create_in(index_dir_, schema_)
    writer_ = ix_.writer()
    # writer_ = AsyncWriter(ix_, writerargs={"limitmb": 1024, "procs": multiprocessing.cpu_count()})
    for intent_ in read_file(INTENT_FILE_):
        for ud in read_file(DICT_FILE_):
            intent_pro_ = intent_.replace(ud, " " + ud + " ")
            r.hset(rk_bot_intents_whoosh, intent_pro_, intent_)
            intents_dict_[intent_pro_] = intent_
            writer_.add_document(content=intent_pro_)
        r.hset(rk_bot_intents_whoosh, intent_, intent_)
        intents_dict_[intent_] = intent_
        writer_.add_document(content=intent_)
    writer_.commit(optimize=True)

    r_set_pickled(r, "bot_whoosh", bot_name, ix_)
    bot_intents_whoosh_dict[bot_name] = intents_dict_
    bot_whoosh[bot_name] = ix_


def build_bot_priorities(bot_name):
    rk_bot_priorities = "bot_priorities&" + bot_name
    PRIORITY_FILE = os.path.join(BOT_SRC_DIR, bot_name, "priority.txt")

    r.delete(rk_bot_priorities)
    for line in read_file(PRIORITY_FILE):
        r.rpush(rk_bot_priorities, line)
    bot_priorities[bot_name] = read_file(PRIORITY_FILE)


redis_lock.reset_all(r)

if global_lock.acquire(blocking=False):
    for bot_na in os.listdir(BOT_SRC_DIR):
        # 创建bot lock
        redis_lock.Lock(r, "lock_" + bot_na)

        # 创建bot version
        r.hdel("bot_version", bot_na)
        r.hdel("bot_version&" + bot_na, str(os.getpid()))
        r_v_ = r.hincrby("bot_version", bot_na)
        r.hset("bot_version&" + bot_na, str(os.getpid()), r_v_)

        # build bot intent dict
        build_bot_intents_dict_trie(bot_na)
        print(bot_na, "intents dict and trie finished building...")

        # 加载whoosh索引文件
        index_dir = os.path.join(BOT_SRC_DIR, bot_na, "index")
        if not os.path.exists(index_dir):
            os.mkdir(index_dir)
        build_bot_whoosh_index(bot_na, index_dir)
        print(bot_na, "whoosh index finished building...")

        # 加载priority文件，越top优先级越高
        build_bot_priorities(bot_na)
        print(bot_na, "priority file finished loading...")

        # 设置过期时间
        bot_recents[bot_na] = r_to_str_list(r, "bot_recent&" + bot_na)
        bot_frequency[bot_na] = r_to_dict(r, "bot_frequency&" + bot_na, "int")
        r.expire("bot_recent&" + bot_na, 30 * 24 * 3600)  # 设置过期时间30天
        r.expire("bot_frequency&" + bot_na, 30 * 24 * 3600)  # 设置过期时间30天

    global_lock.release()
else:
    print("Someone else has the lock.")
