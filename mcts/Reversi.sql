CREATE TABLE `Reversi` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT COMMENT '主键id',
  `node_id` bigint(20) NOT NULL DEFAULT '0' COMMENT '当前节点id',
  `parent_node_id` bigint(20) NOT NULL DEFAULT '0' COMMENT '父节点id',
  `win` int(11) NOT NULL DEFAULT '0' COMMENT '胜利次数',
  `total` int(11) NOT NULL DEFAULT '0' COMMENT '总次数',
  `board_status` varchar(1024) NOT NULL DEFAULT '' COMMENT '当前棋盘状态',
  `board_status_hash` varchar(32) NOT NULL DEFAULT '' COMMENT '棋盘状态hash',
  `player` tinyint(4) NOT NULL DEFAULT '0' COMMENT '棋手(1为执黑，2为执白)',
  `is_terminal` tinyint(4) NOT NULL DEFAULT '0' COMMENT '是否结束（1为未结束，2为已结束）',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uniq_node_id` (`node_id`),
  UNIQUE KEY `uniq_board` (`parent_node_id`,`board_status_hash`)
) ENGINE=InnoDB AUTO_INCREMENT=2079241 DEFAULT CHARSET=utf8
