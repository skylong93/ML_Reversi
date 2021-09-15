# -*- coding: UTF-8 -*-
import mysql.connector
import reversi
import reversi_board_status
import time
import sys
import signal


class Main(object):
    signalFlag = False

    # 信号处理程序
    def sigintHandler(self, signum, frame):
        print 'graceful exit.put signal.'
        self.signalFlag = True
        pass

    def run(self):
        signal.signal(signal.SIGINT, self.sigintHandler)  # 由Interrupt Key产生，通常是CTRL+C或者DELETE产生的中断
        signal.signal(signal.SIGHUP, self.sigintHandler)  # 发送给具有Terminal的Controlling Process，当terminal 被disconnect时候发送
        signal.signal(signal.SIGTERM, self.sigintHandler)  # 请求中止进程，kill命令缺省发送
        signal.signal(signal.SIGQUIT, self.sigintHandler)  # 请求中止进程，kill命令缺省发送
        if len(sys.argv) != 2:
            print 'must input node_id'
            exit(0)

        mysql_conn = mysql.connector.connect(user='root', password='@123MhxzKhl',
                                             host='10.96.108.195',
                                             database='machine_learning')
        treeNode = reversi_board_status.ReversiBoardStatus.getTreeNode(mysql_conn, sys.argv[1])
        if not treeNode:
            print 'input node_id is not exit'
            exit(0)

        reversiObj = reversi.Reversi(mysql_conn)
        reversiObj.nowBoard = treeNode
        reversiObj.rootBoard = treeNode
        beginTime = int(time.time())
        while (True):
            now = int(time.time())
            print 'now time', now
            if self.signalFlag:
                print 'grateful quit'
                break
            if now < beginTime + 1:
                reversiObj.practice()
            else:
                print 'quit'
                break
        mysql_conn.close()
        exit(0)


main = Main()
main.run()
