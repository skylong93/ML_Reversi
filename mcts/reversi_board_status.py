# -*- coding: UTF-8 -*-
import copy
import conf
import json
import random
import utils
import hashlib
import sys
import math

"""
黑白棋的棋盘操作
黑白棋为 8 * 8 棋盘，从左上编号为0，从左到右从上到下以此从0到7
竖直往下是x轴，水平往右是y轴，向量(0,1)表示向下的箭头，和编号吻合
内存中使用二维数组表示棋盘（类似领接矩阵），压缩表示为用数组记录黑子位置和白子位置（类似领接表）
数组中0表示无子，1表示有黑子，2表示有白子
如下
0 0 0 0 0 0 0 0
0 0 0 0 0 0 0 0
0 0 0 0 1 0 0 0
0 0 0 1 1 0 0 0
0 0 0 2 1 0 0 0
0 0 0 0 0 0 0 0
0 0 0 0 0 0 0 0
0 0 0 0 0 0 0 0
黑子在35位置下了一步棋，将45位置的白棋变成了黑棋。
压缩表示
{"1":["24","33","34","44"],"2":["43"]}
"""


class ReversiBoardStatus(object):
    win = 0
    total = 0
    player = 0
    is_terminal = 0
    parent_node_id = 0
    node_id = 0
    mysql_conn = None
    childs_node = []

    # 黑子所在位置，44代表棋盘的第四行第四列有黑子
    black_position = []
    # 白字所在位置，同上
    white_position = []
    board = [[]]
    # 下一步可行的位置,如{"34": [[-1,-1],[0,1]]}
    # 代表这下一步可以走在
    legalPosition = {}

    # # 获取初始棋盘，初始棋盘属于白子，下一步黑子走
    # def __init__(self):
    #     self.player = 2
    #     self.black_position = ["33", "44"]
    #     self.white_position = ["34", "43"]
    #     self.board = conf.Const.BOARD_EMPTY
    #     self.board[3][3] = 1
    #     self.board[4][4] = 1
    #     self.board[3][4] = 2
    #     self.board[4][3] = 2

    def getBoard(self):
        return self.board

    def getOppositePlayer(self):
        if self.player == 1:
            return 2
        if self.player == 2:
            return 1
        raise ValueError("player value is illegal")

    # 此处默认该点是已可行的，不然若去判断其合法性，需要再做一次遍历，耗时长
    # 入参是3，4这样代表位置的数字
    def nextMove(self, position_line, position_column):
        if not self.legalPosition.has_key(str(position_line) + str(position_column)):
            return False
        nextBoardStatus = copy.deepcopy(self)
        nextBoardStatus.win = 0
        nextBoardStatus.total = 0
        nextBoardStatus.player = self.getOppositePlayer()
        nextBoardStatus.is_terminal = 1
        nextBoardStatus.parent_node_id = self.node_id
        # nextBoardStatus.node_id = utils.Utils.getNodeId()
        nextBoardStatus.mysql_conn = self.mysql_conn
        nextBoardStatus.black_position = []
        nextBoardStatus.white_position = []
        nextBoardStatus.player = self.getOppositePlayer()
        nextBoardStatus.board[position_line][position_column] = nextBoardStatus.player

        vertor = self.legalPosition[str(position_line) + str(position_column)]
        for i in vertor:
            nowPositionLine = position_line
            nowPositionColumn = position_column
            while True:
                nowPositionLine = nowPositionLine + i[0]
                nowPositionColumn = nowPositionColumn + i[1]
                if nextBoardStatus.board[nowPositionLine][nowPositionColumn] == self.player:
                    nextBoardStatus.board[nowPositionLine][nowPositionColumn] = nextBoardStatus.player
                else:
                    break
        nextBoardStatus.flushPositionByBoard()
        return nextBoardStatus

    # 以当前棋局状态，调转玩家。
    def turnOverPlayer(self):
        nextBoardStatus = copy.deepcopy(self)
        nextBoardStatus.win = 0
        nextBoardStatus.total = 0
        nextBoardStatus.player = self.getOppositePlayer()
        nextBoardStatus.is_terminal = 1
        nextBoardStatus.parent_node_id = self.node_id
        # nextBoardStatus.node_id = utils.Utils.getNodeId()
        nextBoardStatus.mysql_conn = self.mysql_conn
        return nextBoardStatus

    # 用board去更新black和white的数组
    def flushPositionByBoard(self):
        self.legalPosition = {}
        self.black_position = []
        self.white_position = []
        for lineIndex in range(len(self.board)):
            for columnIndex in range(len(self.board[lineIndex])):
                if self.board[lineIndex][columnIndex] == conf.Const.BLACK:
                    self.black_position.append(str(lineIndex) + str(columnIndex))
                elif self.board[lineIndex][columnIndex] == conf.Const.WHITE:
                    self.white_position.append(str(lineIndex) + str(columnIndex))
        if self.terminal():
            self.is_terminal = 2
        return

    def flushPositionByPosition(self):
        self.board = [[0 for i in range(8)] for i in range(8)]
        for positionBlack in self.black_position:
            self.board[int(positionBlack[0:1])][int(positionBlack[1:2])] = conf.Const.BLACK
        for positionWhite in self.white_position:
            self.board[int(positionWhite[0:1])][int(positionWhite[1:2])] = conf.Const.WHITE
        return

    def getBoardJson(self):
        result = {"1": self.black_position, "2": self.white_position}
        return json.dumps(result)

    """
    落点的三个要求
    1、空白点
    2、（假设轮到黑子走子），落点附近的8格必须有一个白子
    3、落点的8个方向上必须存在至少一个黑子
    返回map,其中一项如下 {"34", "position_vertor": [[-1,-1],[0,1]]}
    34代表行列位置，第三行第四列，position_vertor为可提子的向量方向，二维数组，每一行是一个向量值
    
    目前采取的策略是遍历棋盘。另外的方案，先去查position，找与自身棋子相同的子，查周围空白点，判断空白点是否可下，在加上位标志的方式，看哪些点被访问过了。
    """

    def getNextLegalPosition(self):
        if self.legalPosition:
            return self.legalPosition
        legalPosition = {}
        for i in range(0, 8, 1):
            for j in range(0, 8, 1):
                vertor = self.__isLegalPosition(i, j)
                if vertor:
                    legalPosition[str(i) + str(j)] = vertor
        if not legalPosition:
            return False
        self.legalPosition = legalPosition
        return legalPosition

    # 判断某个点是否是合法点
    def __isLegalPosition(self, position_line, position_column):
        if self.board[position_line][position_column] != 0:
            return False
        if position_line < 0 or position_line > 7 or position_column < 0 or position_column > 7:
            return False

        legalVertor = []
        for i in range(-1, 2, 1):
            for j in range(-1, 2, 1):
                if position_line + i >= 0 and position_line + i <= 7 and position_column + j >= 0 and position_column + j <= 7 and \
                        self.board[position_line + i][position_column + j] == self.player:
                    if self.__findSameColor(position_line, position_column, i, j, self.getOppositePlayer()):
                        legalVertor.append([i, j])

        if len(legalVertor) == 0:
            return False
        else:
            return legalVertor

    # 找某一个位置，在某个向量上是否有同颜色棋子
    def __findSameColor(self, position_line, position_column, vertical_vector, horizontal_vector, player):
        tmpVertical = vertical_vector
        tmpHorizontal = horizontal_vector
        while True:
            if position_line + tmpVertical < 0 or position_line + tmpVertical > 7 or position_column + tmpHorizontal < 0 or position_column + tmpHorizontal > 7:
                return False
            if self.board[position_line + tmpVertical][position_column + tmpHorizontal] == 0:
                return False
            if self.board[position_line + tmpVertical][position_column + tmpHorizontal] == player:
                return True
            tmpVertical += vertical_vector
            tmpHorizontal += horizontal_vector
            continue
        return False

    def terminal(self):
        legalPosition = self.getNextLegalPosition()
        if not legalPosition:
            nextBoard = self.turnOverPlayer()
            nextLegalPosition = nextBoard.getNextLegalPosition()
            if not nextLegalPosition:
                return True
            else:
                return False
        else:
            return False

    def winResult(self):
        if not self.terminal():
            return False
        if len(self.black_position) > len(self.white_position):
            return 1
        else:
            return 0

    def printWinResult(self):
        if not self.terminal():
            return False
        print 'black:', len(self.black_position)
        print 'white:', len(self.white_position)

    def getJsonBoardStatus(self):
        mapResp = {"1": self.black_position, "2": self.white_position}
        return json.dumps(mapResp)

    def saveNode(self):
        if self.player != 1 and self.player != 2:
            return False
        if self.is_terminal != 1 and self.is_terminal != 2:
            return False

        sql = "INSERT INTO Reversi (node_id, parent_node_id,win,total,board_status,board_status_hash,player,is_terminal) VALUES (%s, %s, %s, %s,%s, %s, %s, %s)"
        boardStatusMap = {"1": self.black_position, "2": self.white_position}
        boardStatusJson = json.dumps(boardStatusMap)
        val = (
            self.node_id, self.parent_node_id, self.win, self.total, boardStatusJson,
            hashlib.md5(boardStatusJson).hexdigest(),
            self.player, self.is_terminal)
        # print "execute insert:", sql, val
        self.mysql_conn.cursor().execute(sql, val)
        # insert没有报错则成功执行，报错则会抛异常
        self.mysql_conn.commit()
        return True

    def updateNode(self, value,total):
        sql = "UPDATE Reversi set win=win + %s,total=total + %s where node_id=%s"
        val = (value, total,self.node_id)
        # print "execute update:", sql, val
        self.mysql_conn.cursor().execute(sql, val)
        # insert没有报错则成功执行，报错则会抛异常
        self.mysql_conn.commit()
        return True

    # nextMove后，根据棋盘状态获取node_id
    def getNodeId(self):
        sql = "select node_id from Reversi where parent_node_id=%s and board_status_hash=%s"
        boardStatusMap = {"1": self.black_position, "2": self.white_position}
        boardStatusJson = json.dumps(boardStatusMap)
        val = (self.parent_node_id, hashlib.md5(boardStatusJson).hexdigest())
        # print "execute select:",sql,val
        curs = self.mysql_conn.cursor()
        curs.execute(sql, val)
        result = curs.fetchone()
        # print "select results:", result
        if result:
            return result[0]
        else:
            return False

    """
    · 表示空位置 B-black代表黑棋 W-white代表白棋
    """

    # 〇
    def printBoard(self):
        for line in self.board:
            for a in line:
                if a == 0:
                    print '·',
                elif a == 1:
                    print 'B',
                elif a == 2:
                    print 'W',
                else:
                    print 'I',
            print ''

    """
    棋盘状态类似如下的json数组
    {"1":["44","55"],"2":["54","45"]}
    1代表黑棋，2代表白棋。
    数组内的值代表黑子的落点，上述为初始棋盘状态
    """

    @staticmethod
    def getInstance(json_board_status):
        reversiBoardStatus = ReversiBoardStatus()
        boardStatus = json.loads(json_board_status, object_hook=utils.Utils.hookConvert)
        reversiBoardStatus.black_position = boardStatus["1"]
        reversiBoardStatus.white_position = boardStatus["2"]
        reversiBoardStatus.flushPositionByPosition()
        return reversiBoardStatus

    def simulation(self):
        if self.terminal():
            return self.winResult()
        legalPosition = self.getNextLegalPosition()
        if legalPosition:
            position = random.sample(legalPosition, 1)
            nextBoardStatus = self.nextMove(int(position[0][0:1]), int(position[0][1:2]))
            if not nextBoardStatus:
                return False
            return ReversiBoardStatus.simulation(nextBoardStatus)
        else:
            nextBoardStatus = self.turnOverPlayer()
            return ReversiBoardStatus.simulation(nextBoardStatus)

    def backpropagation(self, value,total):
        self.updateNode(value,total)
        if self.parent_node_id:
            treeNode = ReversiBoardStatus.getTreeNode(self.mysql_conn, self.parent_node_id)
            treeNode.backpropagation(value,total)
        return

    # 计算当前节点的UCT值。找父节点，父节点的total=子节点total的和
    def UCTSelect(self):
        treeNode = ReversiBoardStatus.getTreeNode(self.mysql_conn, self.parent_node_id)
        # total为0的情况，返回int最大值
        if self.total == 0:
            return sys.maxsize
            # win保存的永远是黑棋的胜率，黑棋的话，选择的是黑棋胜率最好的。相反，如果是白棋，则选择黑棋胜率最低的
        if self.player == 1:
            result = self.win / self.total + conf.Const.C * math.sqrt(
                math.log(treeNode.total, 10) / self.total)
        else:
            result = (self.total - self.win) / self.total + conf.Const.C * math.sqrt(
                math.log(treeNode.total, 10) / self.total)
        return result

    @staticmethod
    def getTreeNode(mysql_conn, node_id):
        sql = "select node_id, parent_node_id,win,total,board_status,player,is_terminal from Reversi where node_id=%s"
        val = (node_id,)
        # print "execute select:",sql,val
        curs = mysql_conn.cursor()
        curs.execute(sql, val)
        result = curs.fetchone()
        if not result:
            return False
        # print "select results:", result
        reversiBoard = ReversiBoardStatus.getInstance(str(result[4]))
        reversiBoard.node_id = result[0]
        reversiBoard.parent_node_id = result[1]
        reversiBoard.win = result[2]
        reversiBoard.total = result[3]
        reversiBoard.player = result[5]
        reversiBoard.is_terminal = result[6]
        reversiBoard.mysql_conn = mysql_conn
        return reversiBoard

    @staticmethod
    def getAllChilds(mysql_conn, parent_node_id):
        sql = "select node_id, parent_node_id,win,total,board_status,player,is_terminal from Reversi where parent_node_id=%s"
        val = (parent_node_id,)
        # print "execute select:", sql, val
        curs = mysql_conn.cursor()
        curs.execute(sql, val)
        results = curs.fetchall()
        # print "select results:", results
        childs = []
        for result in results:
            reversiBoard = ReversiBoardStatus.getInstance(str(result[4]))
            reversiBoard.node_id = result[0]
            reversiBoard.parent_node_id = result[1]
            reversiBoard.win = result[2]
            reversiBoard.total = result[3]
            reversiBoard.player = result[5]
            reversiBoard.is_terminal = result[6]
            reversiBoard.mysql_conn = mysql_conn
            childs.append(reversiBoard)
        return tuple(childs)
