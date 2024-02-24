# 项目下载
- 安装git lfs(在git bash中输入 git lfs install)，用于下载项目中的大文件
- git clone -b master <远程仓库url> ，下载ActiveDNS项目
- 进入仓库目录，输入git lfs fetch，从远程服务器下载大文件
- 使用 git lfs checkout 命令将文件检出到工作目录中
# 项目介绍
## 相关技术介绍

- **BIND**（Berkeley Internet Name Domain）是一个广泛使用的开源 DNS服务器软件。它是互联网上最常用的 DNS 服务器之一，用于将域名解析为与之对应的 IP 地址，并提供其他 DNS 相关功能。
- **DLZ**（Database Lookaside Zone）是 BIND的一个功能模块，它允许将 DNS的数据存储在外部数据库中，而不是传统的文本文件中。DLZ 提供了一种灵活的方式来管理 DNS 记录，使得可以将 DNS 数据存储在各种数据库中，如 MySQL、PostgreSQL 等，在ActiveDNS中使用**PostgreSQL**来完成数据存储。DLZ 的工作原理是通过与 BIND 的插件结合，将 DNS 查询转发到外部数据库，并从数据库中检索相应的 DNS 记录。这种方式可以实现动态更新 DNS 记录、灵活的数据管理和与其他应用程序集成的能力。
- **安装环境：** Ubuntu 22.04
# 项目安装 
## 0. python所需模块
```
psycopg2-binary 
datedays 
numpy 
ping3
requests
dnspython
```
在这些库中需要通过pip进行安装：

- psycopg2：用于连接和操作 PostgreSQL 数据库的库。
- datedays：python日期工具。
- numpy：用于进行科学计算和数组操作的库。
- ping3：用于执行网络 ping 测试的库。
- requests：用于发送 HTTP 请求的库。
- dnspython：用于解析和操作 DNS 的库。

在这些库中，以下是Python的内置模块：

- datetime：日期和时间处理模块，无需额外安装。
- json：用于处理 JSON 数据的内置模块。
- csv：用于读写 CSV 文件的内置模块。
- futures：提供了并发执行任务的功能

## 1.安装&配置

- 由于脚本中涉及到环境变量的设置，所以需要使用source命令来运行脚本
- 脚本install.sh：完成postgreSQL、BIND的安装及配置，启动named服务（**named** 是 BIND 服务的核心组件，通过运行 named 可以启动 BIND DNS 服务器）
## 2.数据测量、数据库更新

- 执行scheduled_exec.sh脚本文件，将measure.sh脚本设置为每天0点定时执行，运行测量程序、数据库更新程序，将清除过期IP的python文件设置为每十分钟执行一次。
```python
#!/bin/bash

# 安装 cron
echo "$SUDO_PASSWORD" | sudo -S apt install cron -y

# 添加定时任务到 crontab
(crontab -l ; echo "0 0 * * * export PROJECT_DIR=${PROJECT_DIR} && ${PROJECT_DIR}/ActiveDNS/measure.sh > ${PROJECT_DIR}/ActiveDNS/Log/measure.log") | crontab -
(crontab -l ; echo "*/10 * * * * export PROJECT_DIR=${PROJECT_DIR} && python3 ${PROJECT_DIR}/ActiveDNS/Src/Monitor_ip.py > ${PROJECT_DIR}/ActiveDNS/Log/Monitor_ip.log") | crontab -
echo "Scheduled task has been set up successfully!"




```

- measure.sh脚本：进行数据测量、完成数据库更新
- Monitor_ip.py：清除过期的IP