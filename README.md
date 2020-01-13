
# 说明
- 实时交易
- 历史回撤

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

# 数据库
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

# 策略说明
## 流程图

```flow
st=>start: 开始
e=>end: 结束
op1=>operation: 读取股票价格数据
op2=>operation: 产生短期均线序列

op3=>operation: 识别极点

op4=>operation: 过滤微小波动

op5=>operation: 产生滤波后的均线

op6=>operation: 识别高低点

op7=>operation: 进行策略判断

op8=>operation: 做出买卖判断

st->op1->op2->op3->op4->op5->op6->op7->op8->e

```

## 长均线保护策略

当股价处于明显的下降通道时，不应进行多头开仓，而当股价处于明显的上升通道时，不应进行空头开仓。

* 当滤波后的均线低于f日长均线时，不进行多头开仓操作，已经持有的多头仓位应进行平仓。**在股市里，如果持股，则是卖出的条件。**

* 当滤波后的均线高于f日长均线时，不进行空头开仓操作，已经持有的空头仓位应进行平仓。**在股市里，是买入的条件。**



## 高低点比较策略

### 极小值

* <买入> 如果当前低点比前一个低点的向上漂移项高，则多头开仓或持有多头；

* <卖出> 如果当前低点比前一个低点的向下漂移项低，则空头开仓或持有空头；

* <卖出> 如果当前低点位于前一个低点的向下漂移项和向上漂移项之间，则平仓或空仓。

### 极大值

* <卖出> 如果当前高点比前一个高点的向下漂移项低，则空头开仓或持有空头；

* <买入> 如果当前高点比前一个高点的向上漂移项高，则多头开仓或持有多头；

* <卖出> 如果当前高点位于前一个高点的向下漂移项和向上漂移项之间，则平仓或空仓。



## 高低点突破策略为

+ 如果滤波后的均线比前一个高点的向下漂移项高，则平仓或空仓；

+ 如果滤波后的均线比前一个高点的向上漂移项高，则多头开仓或持有多头。 

+ 如果滤波后的均线比前一个低点的向上漂移项低，则平仓或空仓；

+ 如果滤波后的均线比前一个低点的向下漂移项低，则空头开仓或持有空头。





