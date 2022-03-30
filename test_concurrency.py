# -*- coding: utf-8 -*-

import requests
import json
from common import *

import threading

post_data = json.dumps({
    "bot_name": "banking demo4",
    "query": "cus",
    "size": 500,
    "cn_enable": True
})


def doWaiting():
    start = datetime.datetime.now()
    r = requests.post("http://127.0.0.1:8088/search", data=post_data)
    print(r.text)
    print(time_cost(start))


for i in range(500):
    t = threading.Thread(target=doWaiting)
    t.start()
