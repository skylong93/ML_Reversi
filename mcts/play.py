# -*- coding: UTF-8 -*-
import reversi
import reversi_board_status
import conf
import mysql.connector


# 实战
# 如果该节点已经选过，则直接根据UTC选择。如果没有选择过，则实时根据simulation选择其中一个点（选择可接受的迭代次数）。
# 同时，该盘结果以权重为C（该参数可调整，初定为5），做为监督学习的数据
class PlayReversi:
    reversiObj = None
    color = 'white'

    def __init__(self):
        mysql_conn = mysql.connector.connect(user='root', password='123456',
                                             host='127.0.0.1',
                                             database='machine_learning')
        # treeNode = reversi_board_status.ReversiBoardStatus.getTreeNode(mysql_conn, 12)
        treeNode = reversi_board_status.ReversiBoardStatus.getTreeNode(mysql_conn, 12)
        self.reversiObj = reversi.Reversi(mysql_conn)
        self.reversiObj.nowBoard = treeNode
        self.reversiObj.rootBoard = treeNode

    def play(self):
        player = self.getPlayer()
        self.color = 'white'
        if player == self.reversiObj.nowBoard.player:
            self.color = 'black'
            self.computerPlay()
        while (True):
            # 玩家走子
            if not self.humanPlay():
                break

            # 电脑走子
            if not self.computerPlay():
                break
        exit(0)

    def humanPlay(self):
        if self.reversiObj.nowBoard.terminal():
            print 'game is over.'
            self.reversiObj.nowBoard.printWinResult()
            return False
        self.reversiObj.nowBoard.printBoard()
        print 'is your turn,your play.', self.color
        print 'now node id is:', self.reversiObj.nowBoard.node_id

        move = self.enterNextNode()
        nextBoard = self.reversiObj.nowBoard.nextMove(int(move[0:1]), int(move[1:2]))
        nodeId = nextBoard.getNodeId()

        if nodeId:
            self.reversiObj.nowBoard = nextBoard
            self.reversiObj.nowBoard.node_id = nodeId
        else:
            self.reversiObj.expansionAndSimulation()
            nextBoard = self.reversiObj.nowBoard.nextMove(int(move[0:1]), int(move[1:2]))
            nodeId = nextBoard.getNodeId()
            self.reversiObj.nowBoard = nextBoard
            self.reversiObj.nowBoard.node_id = nodeId
        return True

    def computerPlay(self):
        # 电脑走子
        if self.reversiObj.nowBoard.terminal():
            print 'game is over.'
            self.reversiObj.nowBoard.printWinResult()
            return False

        self.reversiObj.nowBoard.printBoard()
        print 'is computer turn.'
        print 'now node id is:', self.reversiObj.nowBoard.node_id

        nextBoard = self.getNextNode()
        self.reversiObj.nowBoard = nextBoard
        return True

    def getPlayer(self):
        player = input('please enter your player.[white type 2/black type 1]:')
        if player != 1 and player != 2:
            print 'wrong player was input.'
            return self.getPlayer()
        return player

    """
    获取最优的下一步
    """

    def getNextNode(self):
        if self.reversiObj.nowBoard.is_terminal == conf.Const.IS_TERMINAL:
            return False
        if self.reversiObj.isLeafNode():
            # 叶节点且没触达过的节点，做模拟，模拟一次后从头再来
            if self.reversiObj.nowBoard.total == 0:
                value = self.reversiObj.nowBoard.simulation()
                self.reversiObj.backpropagation(value,1)
                # 做扩展的同时，每个节点做10次模拟
                self.reversiObj.expansionAndSimulation()
                # 做过扩展，必定能选中一个
                nextNode = self.reversiObj.selection()
                return nextNode
            else:
                self.reversiObj.expansionAndSimulation()
                # 做过扩展，必定能选中一个
                nextNode = self.reversiObj.selection()
                return nextNode
        else:
            # 前面已经判断过是否叶节点了，是否游戏结束。若当前状态游戏未结束，且非叶节点，那必定能选中一个
            nextNode = self.reversiObj.selection()
            return nextNode

    def enterNextNode(self):
        # 例如34，意味着下在行3列4的位置，从0开始算
        legalPosition = self.reversiObj.nowBoard.getNextLegalPosition()
        print 'all legalPosition', legalPosition
        while (True):
            move = raw_input('please enter opposite player move:')
            if not legalPosition.has_key(move):
                print 'wrong position was input.'
                continue
            break
        return move


print 'begin play'
playReversi = PlayReversi()
playReversi.play()
