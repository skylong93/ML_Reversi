# ML_Reversi
使用蒙特卡洛树搜索mcts训练黑白棋。原始mcts，无监督学习，无价值网络判断，仅只用mcts训练模型。


目前使用mysql存储数据，redis生成唯一键，key为reversi_node_id，初始值为1.
