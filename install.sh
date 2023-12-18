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
echo "$sudo_password" | sudo -S chmod +x ./configure
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
echo "$sudo_password" | sudo -S chmod +x ./configure
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







