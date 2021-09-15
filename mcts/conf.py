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
    REDIS_CONF = {"host": "10.96.108.195", "port": 6379, "password": "@123MhxzKhl"}
    MYSQL_CONF = {'user': 'root', 'password': '@123MhxzKhl', 'host': '10.96.108.195', 'database': 'machine_learning'}
