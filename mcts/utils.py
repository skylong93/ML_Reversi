# -*- coding: UTF-8 -*-
import uuid
import redis

class Utils(object):
    r = redis.StrictRedis(host='10.96.108.195', port=6379, password="@123MhxzKhl")

    @staticmethod
    def getNodeId():
        return Utils.r.incr("reversi_node_id")

    @staticmethod
    def hookConvert(input):
        if isinstance(input, dict):
            return {Utils.hookConvert(key): Utils.hookConvert(value) for key, value in input.iteritems()}
        elif isinstance(input, list):
            return [Utils.hookConvert(element) for element in input]
        elif isinstance(input, unicode):
            return input.encode('utf-8')
        else:
            return input