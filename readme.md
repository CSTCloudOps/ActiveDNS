# 项目介绍
## 相关技术介绍

- **BIND**（Berkeley Internet Name Domain）是一个广泛使用的开源 DNS服务器软件。它是互联网上最常用的 DNS 服务器之一，用于将域名解析为与之对应的 IP 地址，并提供其他 DNS 相关功能。
- **DLZ**（Database Lookaside Zone）是 BIND的一个功能模块，它允许将 DNS的数据存储在外部数据库中，而不是传统的文本文件中。DLZ 提供了一种灵活的方式来管理 DNS 记录，使得可以将 DNS 数据存储在各种数据库中，如 MySQL、PostgreSQL 等，在ActiveDNS中使用**PostgreSQL**来完成数据存储。DLZ 的工作原理是通过与 BIND 的插件结合，将 DNS 查询转发到外部数据库，并从数据库中检索相应的 DNS 记录。这种方式可以实现动态更新 DNS 记录、灵活的数据管理和与其他应用程序集成的能力。
- **安装环境：** Ubuntu 22.04
# 0. python所需依赖、模块（自行安装）
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

# 安装&配置

- 脚本install.sh：完成postgreSQL、BIND的安装及配置，启动named服务（**named** 是 BIND 服务的核心组件，通过运行 named 可以启动 BIND DNS 服务器）
```bash
#!/bin/bash

#启用"遇到错误即退出"的模式
set -e

#将错误流重定向到屏幕
exec 2>&1

##获取管理员权限所需的密码
read -p "Enter current user's password: " sudo_password

# 提示用户输入当前项目所在目录
read -p "Please enter the directory where the current project is located: " project_dir

echo "export PROJECT_DIR=\"$project_dir\"" >> ~/.bashrc

echo "export SUDO_PASSWORD=\"$sudo_password\"" >> ~/.bashrc

source ~/.bashrc


# 更新、升级当前系统使用的软件包
echo "$sudo_password" | sudo -S apt update -y
echo "$sudo_password" | sudo -S apt upgrade -y

# 安装 DLZ 所需的依赖库和开发包
echo "$sudo_password" | sudo -S apt install -y curl
echo "$sudo_password" | sudo -S apt install -y libreadline-dev
echo "$sudo_password" | sudo -S apt install -y gcc make pkg-config libuv1 libuv1-dev libssl-dev libcap-dev libxml2-dev 
echo "$sudo_password" | sudo -S apt install -y python3-pip libpq-dev

# 下载并安装PostgreSQL，使用新创建的用户postgres初始化并启动PostgreSQL数据库服务
cd ${project_dir}/ActiveDNS/Downloads/postgresql-15.2
echo "$sudo_password" | sudo -S ./configure
echo "$sudo_password" | sudo -S make 
echo "$sudo_password" | sudo -S make install

# 新建用户postgres并对数据文件夹进行授权

# 提示用户输入密码
read -p "Please set a password for the new user postgres: " new_user_password
echo

# 使用 adduser 命令创建用户，并传递密码
echo -e "$sudo_password\n$new_user_password\n$new_user_password" | sudo -S adduser postgres
echo "$sudo_password" | sudo -S mkdir -p /mnt/data/postgres 
echo "$sudo_password" | sudo -S chown -R postgres:postgres /mnt/data/postgres
echo "$sudo_password" | sudo -S ln -s /usr/local/pgsql/bin/pg_ctl /usr/local/bin/pgsql_ctl
echo "$sudo_password" | sudo -S ln -s /usr/local/pgsql/bin/psql /usr/local/bin/psql
cd /mnt/data/postgres


# # 初始化并启动PostgreSQL数据库服务
echo "$sudo_password" | sudo -S -u postgres /usr/local/pgsql/bin/initdb -D /mnt/data/postgres
echo "$sudo_password" | sudo -S -u postgres pgsql_ctl start -D /mnt/data/postgres

# # 创建用于存储DNS数据的数据库
echo "$sudo_password" | sudo -S -u postgres psql -c "CREATE DATABASE DNS;"



# 安装BIND，并配置编译选项
cd ${project_dir}/ActiveDNS/Downloads/bind-9.11.0
# 指定安装的目标路径,开启了与 PostgreSQL 数据库的 DLZ 支持，禁用了 OpenSSL 的支持。
echo "$sudo_password" | sudo -S ./configure --prefix=/usr/local/bind/ --with-dlz-postgres --with-openssl=no
echo "$sudo_password" | sudo -S make 
echo "$sudo_password" | sudo -S make install
cd /usr/local/bind/etc/
# BIND 调用 rndc-confgen 工具生成一个 rndc.conf 配置文件，该文件用于配置 rndc，	rndc 是一个用于管理和控制 BIND 服务的命令行工具
echo "$sudo_password" | sudo -S touch rndc.conf named.conf rndc.key
echo "$sudo_password" | sudo -S sh -c '/usr/local/bind/sbin/rndc-confgen > rndc.conf'
echo "$sudo_password" | sudo -S sh -c 'cat rndc.conf >rndc.key'
echo "$sudo_password" | sudo -S sh -c 'tail -10 rndc.conf | head -9 | sed s/#\ //g > named.conf'
# 创建日志文件夹、完善配置文件
echo "$sudo_password" | sudo -S mkdir -p /usr/local/bind/var/logs
echo "$sudo_password" | sudo -S sh -c "cat ${project_dir}/ActiveDNS/Config/basis-named.conf >> /usr/local/bind/etc/named.conf"

# 数据库初始化、启动named服务
# 创建数据存储文件夹
echo "$sudo_password" | sudo -S mkdir -p /mnt/data/postgres/data
echo "$sudo_password" | sudo -S cp  ${project_dir}/ActiveDNS/Data/initial_data/v4_merge_result_without_2domains.csv /mnt/data/postgres/data
python3 ${project_dir}/ActiveDNS/Src/DNS_DATA_INIT.py
echo "$sudo_password" | sudo -S /usr/local/bind/sbin/named 
echo "\nThe BIND server is running normally!"

# 检查错误日志文件是否非空，若非空则输出错误信息
# if [ -s "$error_file" ]; then
#     echo "脚本执行过程中发生以下错误："
#     cat "$error_file"
# else
#     echo "脚本执行完毕，未发现错误。"
# fi

```
# 数据测量、数据库更新

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
```bash
#!/bin/sh

. $HOME/.bashrc

current_time=$(date +"%Y-%m-%d %H:%M:%S")
last_day=$(date -d "yesterday" "+%Y-%m-%d")

base_path="${PROJECT_DIR}/ActiveDNS/Data/${last_day}"
echo "current_time: $current_time\n"
echo $base_path


# 检查文件是否存在并执行Python脚本
execute_python_script() {
    script_file=$1
    output_file=$2

    if [ ! -f "$output_file" ]; then
        echo "Running $script_file..."
        python3 "$script_file"
        if [ $? -eq 0 ]; then
            echo "Python script executed successfully."
        else
            echo "Error: Python script failed."
            exit 1
        fi
    else
        echo "Skipping $script_file. Output file $output_file already exists."
    fi
}

# 依次执行Python脚本并检测输出文件是否存在
execute_python_script "${PROJECT_DIR}/ActiveDNS/Src/0_extend-log-xxh.py" ${base_path}"/extend_domain_ip_xxh.txt"
execute_python_script "${PROJECT_DIR}/ActiveDNS/Src/1_head_domain_ip.py" ${base_path}"/head_domain_ip.txt"
execute_python_script "${PROJECT_DIR}/ActiveDNS/Src/2_merge_head_domain_ip.py" ${base_path}"/head_domain_ip_merge.txt"
execute_python_script "${PROJECT_DIR}/ActiveDNS/Src/3_extend-log-otherdns_v3.py" ${base_path}"/extend_domain_ip_otherdns.txt"
execute_python_script "${PROJECT_DIR}/ActiveDNS/Src/4_merge-log-all.py" ${base_path}"/final_domain_ip_v4.txt"
execute_python_script "${PROJECT_DIR}/ActiveDNS/Src/5_ip_rtt.py" ${base_path}"/final_domain_sorted_ip_rtt_v4-all.txt"
execute_python_script "${PROJECT_DIR}/ActiveDNS/Src/6_merge_result.py" ${base_path}"/v4_merge_result.txt"
execute_python_script "${PROJECT_DIR}/ActiveDNS/Src/7_result2csv.py" ${base_path}"/v4_merge_result_without_2domains.csv"


echo "$SUDO_PASSWORD" | sudo -S mkdir -p /mnt/data/postgres/data/${last_day}
echo "$SUDO_PASSWORD" | sudo -S  sh -c 'cp  ${PROJECT_DIR}/ActiveDNS/Data/${last_day}/v4_merge_result_without_2domains.csv /mnt/data/postgres/data/${last_day}'
python3 ${PROJECT_DIR}/ActiveDNS/Src/Update_Database_Daily.py

# 所有脚本执行成功
current_time=$(date "+%Y-%m-%d %H:%M:%S")
echo "\n${current_time} All Python scripts executed successfully!\n\n\n"


```
