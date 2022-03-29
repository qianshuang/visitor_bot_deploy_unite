# -*- coding: utf-8 -*-

# import threading
# import time

import redis
import redis_lock

r = redis.Redis()
redis_lock.reset_all(r)

# lock_1 = redis_lock.Lock(r, "lock_1")
#
# if lock_1.acquire(blocking=False):
#     print("get lock 1, start sleep...")
#     print(lock_1.id)
#
#     lock_2 = redis_lock.Lock(r, "lock_2")
#     print(lock_2.acquire(blocking=False))
#     print(lock_2.id)
#
#     time.sleep(60)
#     lock_1.release()
#     print("sleep done. release lock 1.")
#
# def doWaiting():
#     print("new thread attempt to get lock...")
#     print(lock_2.acquire(blocking=False))
#
#
# t = threading.Thread(target=doWaiting)
# t.start()

# lock_1 = redis_lock.Lock(r, "lock_1")
# r_set_pickled(r, "bot_lock", "bot_1", lock_1)
#
# print(r_get_pickled(r, "bot_lock", "bot_1").acquire(blocking=False))
