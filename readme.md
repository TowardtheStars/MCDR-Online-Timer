# Online Timer

玩家总在线时长查看器

## 第一次安装

安装方式同其他 MCDR 插件。第一次加载之后，需要手动在后台输入 `!!oltime reload` 加载历史信息。

## 使用方法

### MCDR 命令

- `!!oltime` 查看帮助信息
  - `!!oltime help` 查看帮助信息
  - `!!oltime reload` 从 Minecraft 日志加载玩家登入登出的历史记录，要求至少 MCDR 等级 3 的权限
- `!!olt` 查看玩家自己的总在线时长，控制台使用无效
  - `!!olt <玩家名>` 查看对应玩家的总在线时长，控制台可以使用
- `!!oltop` 查看总在线时长排行榜的第一页
  - `!!oltop <页数>` 查看总在线时长排行榜的其他页数

## 配置文件说明

文件夹：`config/online_timer`

### `data.json`

用于存储玩家在线总时长的数据，勿动。

### `config.json`

- `max_oltop`: 正整数，表示每页总在线时长排行榜的条目数量
