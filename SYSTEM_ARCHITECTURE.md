# 交易与行情监控系统架构图

## 系统架构图 (Mermaid)

```mermaid
graph TB
    subgraph "客户端层 Client Layer"
        WEB[Web Browser]
        TRADER[交易员终端]
        MANAGER[基金经理终端]
    end

    subgraph "API网关层 API Gateway"
        NGINX[Nginx Reverse Proxy]
        DJANGO[Django Application]
        CHANNELS[Django Channels]
    end

    subgraph "WebSocket实时通信层"
        CHAT[ChatConsumer<br/>/ws/chat/]
        STOCK[StockConsumer<br/>/ws/stock/]
        POS[PositionConsumer<br/>/ws/pos/]
        ACC[AccountConsumer<br/>/ws/acc/]
        TRADE[TradeStatisticConsumer<br/>/ws/trade_statistic/]
        ORDER[OrderStatisticConsumer<br/>/ws/order_statistic/]
        POSGROUP[PosGroupStatisticConsumer<br/>/ws/pos_group_statistic/]
    end

    subgraph "REST API层"
        INST[指令管理API<br/>/api/instructions/]
        POSAPI[持仓API<br/>/api/positions/]
        CONT[合约API<br/>/api/contract-list/]
        USER[用户权限API<br/>/api/user/]
        DATA[数据查询API<br/>/data/*]
    end

    subgraph "业务逻辑层 Business Logic"
        AUTH[LDAP认证<br/>Token验证]
        PERM[权限控制<br/>UserRoleProduct]
        INST_SVC[指令服务<br/>Instruction管理]
        POS_SVC[持仓服务<br/>PositionAdjustment]
        TRADE_SVC[交易服务<br/>InstructionDetail]
        EMAIL[邮件通知服务]
    end

    subgraph "数据访问层 Data Access"
        ORMDjango[ORM]
        ROUTER[数据库路由器<br/>ContractListRouter]
        CACHE[Redis缓存]
    end

    subgraph "数据存储层 Data Storage"
        MYSQL_STRATEGY[(MySQL: strategy<br/>指令/持仓/用户数据)]
        MYSQL_MONITOR[(MySQL: pms_monitor<br/>实时行情数据)]
        REDIS[(Redis<br/>缓存+消息队列)]
    end

    subgraph "外部系统 External Systems"
        LDAP[LDAP服务器<br/>用户认证]
        SMTP[邮件服务器<br/>通知服务]
        MARKET[行情数据源<br/>实时市场数据]
    end

    %% 连接关系
    WEB -->|HTTPS/WSS| NGINX
    TRADER -->|HTTPS/WSS| NGINX
    MANAGER -->|HTTPS/WSS| NGINX

    NGINX --> DJANGO
    NGINX --> CHANNELS

    DJANGO --> INST
    DJANGO --> POSAPI
    DJANGO --> CONT
    DJANGO --> USER
    DJANGO --> DATA

    CHANNELS --> CHAT
    CHANNELS --> STOCK
    CHANNELS --> POS
    CHANNELS --> ACC
    CHANNELS --> TRADE
    CHANNELS --> ORDER
    CHANNELS --> POSGROUP

    INST --> AUTH
    POSAPI --> AUTH
    CONT --> AUTH
    USER --> AUTH

    AUTH --> LDAP

    INST --> PERM
    POSAPI --> PERM

    INST --> INST_SVC
    POSAPI --> POS_SVC
    DATA --> TRADE_SVC

    INST_SVC --> EMAIL
    EMAIL --> SMTP

    INST_SVC --> ORMDjango
    POS_SVC --> ORMDjango
    CONT --> ROUTER

    ORMDjango --> MYSQL_STRATEGY
    ROUTER --> MYSQL_MONITOR

    CHAT --> REDIS
    STOCK --> REDIS
    POS --> REDIS
    ACC --> REDIS
    TRADE --> REDIS
    ORDER --> REDIS
    POSGROUP --> REDIS

    CACHE --> REDIS

    MARKET --> MYSQL_MONITOR

    style WEB fill:#e1f5ff
    style DJANGO fill:#ffeb99
    style CHANNELS fill:#99ccff
    style REDIS fill:#ff9999
    style MYSQL_STRATEGY fill:#99ff99
    style MYSQL_MONITOR fill:#99ff99
    style LDAP fill:#cc99ff
```

## 数据流图

```mermaid
sequenceDiagram
    participant Client as 客户端
    participant WS as WebSocket Consumer
    participant Cache as Redis
    participant DB as MySQL (pms_monitor)
    participant API as REST API

    %% 持仓数据流
    Note over Client,DB: 实时持仓推送流程
    Client->>WS: 连接 /ws/pos/
    WS->>Cache: 加入 position_realtime 组
    Client->>API: GET /data/strategy_position/
    API->>DB: 查询持仓数据
    DB-->>API: 返回持仓数据
    API-->>Client: 返回初始数据
    Cache-->>WS: 持仓变化推送
    WS-->>Client: 推送持仓更新

    %% 指令创建流程
    Note over Client,DB: 指令创建流程
    Client->>API: POST /api/instructions/adjustment/
    API->>API: 验证权限
    API->>DB: 创建指令记录
    API->>DB: 创建持仓快照
    API->>API: 发送邮件通知
    API->>Cache: 触发WebSocket通知
    Cache-->>Client: 推送指令更新
    API-->>Client: 返回成功
```

## 部署架构图

```mermaid
graph TB
    subgraph "用户端"
        USER[用户浏览器]
    end

    subgraph "负载均衡层"
        LB[负载均衡器<br/>Nginx]
    end

    subgraph "应用服务器集群"
        APP1[Django App 1<br/>Daphne]
        APP2[Django App 2<br/>Daphne]
        APP3[Django App N<br/>Daphne]
    end

    subgraph "缓存与消息队列"
        REDIS[(Redis Cluster<br/>缓存 + Channel Layer)]
    end

    subgraph "数据库集群"
        MYSQL_STRATEGY[(MySQL: strategy<br/>主从复制)]
        MYSQL_MONITOR[(MySQL: pms_monitor<br/>主从复制)]
    end

    subgraph "外部服务"
        LDAP[LDAP]
        SMTP[SMTP]
        MARKET[行情源]
    end

    USER -->|HTTPS/WSS| LB
    LB --> APP1
    LB --> APP2
    LB --> APP3

    APP1 --> REDIS
    APP2 --> REDIS
    APP3 --> REDIS

    APP1 --> MYSQL_STRATEGY
    APP2 --> MYSQL_STRATEGY
    APP3 --> MYSQL_STRATEGY

    APP1 --> MYSQL_MONITOR
    APP2 --> MYSQL_MONITOR
    APP3 --> MYSQL_MONITOR

    APP1 --> LDAP
    APP1 --> SMTP
    MYSQL_MONITOR --> MARKET
```

## 模块关系图

```mermaid
erDiagram
    %% 用户与权限
    User ||--o{ UserRoleProduct : "has"
    Product ||--o{ UserRoleProduct : "assigns"
    UserRoleProduct }o--|| Role : "uses"

    %% 指令相关
    Instruction ||--o{ PositionAdjustment : "contains"
    Instruction }o--|| Product : "belongs to"
    Instruction }o--|| User : "created by"

    %% 持仓调整相关
    PositionAdjustment ||--o{ InstructionDetail : "generates"
    PositionAdjustment }o--|| ContractList : "references"

    %% 合约相关
    ContractList {
        string c_instrument_id PK
        string c_instrument_name
        string c_exchange_id
        string c_type_name
        string c_stype_name
    }

    %% 指令相关表
    Instruction {
        int id PK
        string product_code
        string status
        decimal total_current_delta_value
        decimal total_adjusted_delta_value
        datetime created_at
    }

    PositionAdjustment {
        int id PK
        int instruction_id FK
        string c_instrument_id FK
        decimal current_position
        decimal adjusted_position
        string status
    }

    InstructionDetail {
        int id PK
        int position_adjustment_id FK
        string open_close
        string buy_sell
        decimal quantity
        decimal price
        decimal filled_quantity
        string trade_id
    }

    %% 用户相关表
    User {
        int id PK
        string username
        string english_name
        string chinese_name
    }

    UserRoleProduct {
        int id PK
        int user_id FK
        string role
        string product_code
    }

    Product {
        string code PK
        string name
    }

    Role {
        string name PK
        string description
    }
```

## WebSocket 端点说明

| 端点 | Consumer | 用途 | 数据类型 |
|------|----------|------|----------|
| `/hsapi/ws/chat/` | ChatConsumer | 团队聊天 | 文本消息 |
| `/hsapi/ws/stock/` | StockConsumer | 实时行情 | 行情数据 |
| `/hsapi/ws/pos/` | PositionConsumer | 持仓监控 | 持仓、Delta、市值 |
| `/hsapi/ws/acc/` | AccountConsumer | 账户监控 | 资金、风险指标 |
| `/hsapi/ws/trade_statistic/` | TradeStatisticConsumer | 成交统计 | 成交数据 |
| `/hsapi/ws/order_statistic/` | OrderStatisticConsumer | 委托统计 | 挂单数据 |
| `/hsapi/ws/pos_group_statistic/` | PosGroupStatisticConsumer | 持仓分组统计 | 分组持仓 |

## 核心API端点

### 指令管理
- `GET/POST /hsapi/wsapp/api/instructions/` - 指令列表/创建
- `GET /hsapi/wsapp/api/instructions/{id}/` - 指令详情
- `PUT /hsapi/wsapp/api/instructions/{id}/status/` - 更新状态
- `POST /hsapi/wsapp/api/instructions/adjustment/` - 创建调仓指令
- `GET /hsapi/wsapp/api/instructions/{id}/positions/` - 持仓明细

### 持仓与交易
- `POST /hsapi/wsapp/api/positions/` - 获取持仓数据
- `GET /hsapi/wsapp/api/trade-details/` - 待交易明细
- `PUT /hsapi/wsapp/api/positions/{id}/status/` - 更新持仓状态

### 合约管理
- `GET/POST /hsapi/wsapp/api/contract-list/` - 合约列表
- `GET /hsapi/wsapp/api/contract-list/{instrument_id}/` - 合约详情
- `GET /hsapi/wsapp/api/contracts/` - 需调整合约

### 数据查询
- `POST /hsapi/wsapp/data/strategy_position/` - 持仓数据
- `POST /hsapi/wsapp/data/strategy_account/` - 账户数据
- `POST /hsapi/wsapp/data/trade_statistic/` - 成交统计
- `POST /hsapi/wsapp/data/order_statistic/` - 委托统计
- `POST /hsapi/wsapp/data/all/` - 全部数据

## 数据库配置

### strategy 数据库 (默认)
- **主机**: 192.168.123.58
- **端口**: 3306
- **用途**: 指令、持仓、用户数据

### pms_monitor 数据库
- **主机**: 192.168.123.58
- **端口**: 3306
- **用途**: 实时行情数据 (只读)

### dataweb_read 数据库
- **主机**: 192.168.201.188
- **端口**: 3306
- **用途**: 用户管理数据 (只读)

## 系统特性

1. **实时性**: WebSocket推送确保数据实时更新
2. **可扩展性**: Redis Channel Layer支持横向扩展
3. **安全性**: LDAP认证 + 基于角色的权限控制
4. **高可用**: 数据库主从复制 + 应用集群部署
5. **性能优化**: Redis缓存减少数据库压力
