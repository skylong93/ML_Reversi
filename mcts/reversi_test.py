# -*- coding: UTF-8 -*-
import mysql.connector
import reversi
import reversi_board_status
import time

mysql_conn = mysql.connector.connect(user='root', password='123456',
                                     host='127.0.0.1',
                                     database='machine_learning')
treeNode = reversi_board_status.ReversiBoardStatus.getTreeNode(mysql_conn, 720806)
reversi = reversi.Reversi(mysql_conn)
reversi.nowBoard = treeNode
reversi.rootBoard = treeNode

reversi.nowBoard.printBoard()
