# -*- coding: UTF-8 -*-
import random
import sys

sys.path.append("../base-data-struct/treeNodeDb.py")

import reversi_board_status
import conf
import utils


# 黑白棋
# 配合reversi_board_status使用，board_status维护每一个棋盘状态的属性和操作，reversi用于控制算法的策略
class Reversi(object):
    rootBoard = None
    nowBoard = None
    mysql_conn = None
    terminalFlag = False

    def __init__(self, mysql_conn):
        self.mysql_conn = mysql_conn

    # 从跟节点开始出发迭代一轮，训练
    def practice(self):
        self.nowBoard = self.rootBoard
        return self.iteration()

    # 从某节点出发迭代一轮
    def iteration(self):
        if self.nowBoard.is_terminal == conf.Const.IS_TERMINAL:
            self.backpropagation(self.nowBoard.winResult(), 1)
            return
        # 叶节点，做模拟或者做扩展
        if self.isLeafNode():
            # 叶节点且没触达过的节点，做模拟，模拟一次后从头再来
            if self.nowBoard.total == 0:
                value = self.nowBoard.simulation()
                self.backpropagation(value, 1)
                return
            else:
                # self.expansion()
                self.expansionAndSimulation()
                # 做过扩展，必定能选中一个
                nextNode = self.selection()
                self.nowBoard = nextNode
                return self.iteration()
        else:
            # 前面已经判断过是否叶节点了，是否游戏结束。若当前状态游戏未结束，且非叶节点，那必定能选中一个
            nextNode = self.selection()
            self.nowBoard = nextNode
            return self.iteration()

    # def terminal(self):
    #     legalPosition = self.nowBoard.getNextLegalPosition()
    #     if not legalPosition:
    #         return True
    #     else:
    #         return False

    def isLeafNode(self):
        if not self.getChilds():
            return True
        else:
            return False

    def getChilds(self):
        return reversi_board_status.ReversiBoardStatus.getAllChilds(self.mysql_conn, self.nowBoard.node_id)

    # 经典的MCTS，会倾向于走所有未走过的节点，例如围棋这种搜索空间异常巨大的，则需要有合理的剪枝方案
    # 返回的为某一个子节点对象
    def selection(self):
        # 返回走过节点的UCT最大的节点
        allProbability = {}
        for child in self.getChilds():
            result = child.UCTSelect()
            # 当出现一个最大值的时候，直接选中
            if result == sys.maxsize:
                return child
            allProbability[result] = child
        if not allProbability:
            return False
        # 选择其中的最大值，非概率选择
        keys = allProbability.keys()
        keys.sort()
        return allProbability[keys[-1]]

    # 概率选择，能够避免陷入其中一条路中。根据UTC权重大小选择
    # 返回的为某一个子节点对象
    def selectionRandom(self):
        # 返回走过节点的UCT最大的节点
        allProbability = {}
        for child in self.getChilds():
            result = child.UCTSelect()
            # 当出现一个最大值的时候，直接选中
            if result == sys.maxsize:
                return child
            allProbability[result] = child
        if not allProbability:
            return False
        # 选择其中的最大值，非概率选择
        # TODO 可以改造成概率选择，能够避免陷入其中一条路中，
        keys = allProbability.keys()
        keys.sort()
        return allProbability[keys[-1]]

    # 叶节点，且该叶节点已模拟过
    def expansion(self):
        legalPosition = self.nowBoard.getNextLegalPosition()
        if not legalPosition:
            next = self.nowBoard.turnOverPlayer()
            nodeId = next.getNodeId()
            if not nodeId:
                next.node_id = utils.Utils.getNodeId()
                next.saveNode()
            return next
        result = None
        # 先找其中的某一个节点返回
        position = random.sample(legalPosition, 1)
        # 先存入所有的扩展叶节点
        for i in self.nowBoard.legalPosition:
            nextBoard = self.nowBoard.nextMove(int(i[0:1]), int(i[1:2]))
            nodeId = nextBoard.getNodeId()
            if not nodeId:
                nextBoard.node_id = utils.Utils.getNodeId()
                nextBoard.saveNode()
            if position[0] == i:
                result = nextBoard
        return result

    def expansionAndSimulation(self):
        tempBoard = self.nowBoard
        legalPosition = self.nowBoard.getNextLegalPosition()
        result = None
        if not legalPosition:
            next = self.nowBoard.turnOverPlayer()
            nodeId = next.getNodeId()
            if not nodeId:
                next.node_id = utils.Utils.getNodeId()
                next.saveNode()
            return next

        # 先找其中的某一个节点返回
        position = random.sample(legalPosition, 1)
        # 先存入所有的扩展叶节点
        for i in legalPosition:
            self.nowBoard = tempBoard
            nextBoard = self.nowBoard.nextMove(int(i[0:1]), int(i[1:2]))
            self.nowBoard = nextBoard
            allWinResult = 0
            for j in range(conf.Const.SIMULATION_TIME):
                result = self.simulation()
                allWinResult = allWinResult + result
            self.backpropagation(result, conf.Const.SIMULATION_TIME)
            nodeId = nextBoard.getNodeId()
            if not nodeId:
                nextBoard.node_id = utils.Utils.getNodeId()
                nextBoard.saveNode()
            # 返回随机选择的节点
            if position[0] == i:
                result = nextBoard
        self.nowBoard = tempBoard
        return result

    # 对当前节点执行模拟，获取模拟值
    def simulation(self):
        return reversi_board_status.ReversiBoardStatus.simulation(self.nowBoard)

    def backpropagation(self, value, total):
        return self.nowBoard.backpropagation(value, total)
