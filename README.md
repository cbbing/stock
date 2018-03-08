[toc]

[2018-02-25]
# 行情下载
- 股票基本信息

> [py3/security_data]

```
data_download.download_stock_basic_info()
```

- 股票行情和指数行情
```
data_download.download_all_stock_history_k_line()
```

# 均线策略
## 1, 表结构
```
CREATE TABLE `stock_kline` (
  `code` varchar(32) NOT NULL,
  `date` date NOT NULL,
  `open` double DEFAULT NULL,
  `high` double DEFAULT NULL,
  `low` double DEFAULT NULL,
  `close` double DEFAULT NULL COMMENT '收盘价（前复权）',
  `close_hfq` double DEFAULT NULL COMMENT '收盘价（后复权）',
  `volume` double DEFAULT NULL COMMENT '成交量',
  `update_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`code`,`date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
```





# 说明
- 实时交易
- 历史回撤

