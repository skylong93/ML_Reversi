# -*- coding: UTF-8 -*-

class Const(object):
    C = 2
    SIMULATION_TIME = 5
    # 直接引用的话，因为是数组，会被当成指针引用。所以该数组会变化
    # BOARD_EMPTY = [[0 for i in range(8)] for i in range(8)]
    BOARD_JSON_EMPTY = '{"1": ["44", "55"], "2": ["54", "45"]}'
    BLACK = 1
    WHITE = 2
    IS_NOT_TERMINAL = 1
    IS_TERMINAL = 2
    REDIS_CONF = {"host": "127.0.0.1", "port": 6379, "password": "123456"}
    MYSQL_CONF = {'user': 'root', 'password': '123456', 'host': '127.0.0.1', 'database': 'machine_learning'}
