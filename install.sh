#!/bin/bash

#Enabling "exit on error" mode
set -e

exec 2>&1

## Enter the password required for administrator privileges
read -p "Enter current user's password: " sudo_password

# Enter the current project directory
read -p "Please enter the directory where the current project is located: " project_dir

# Setting a password for the new user postgres
read -p "Please set a password for the new user postgres: " new_user_password

# Prompts the user to enter the name of the database to be created
read -p "Please enter the name of the database to be created" db_name

# Prompts the user to enter the name of the data table to be created
read -p "Please enter the table name of the database to be created" db_table_name

echo "export PROJECT_DIR=\"$project_dir\"" >> ~/.bashrc

echo "export SUDO_PASSWORD=\"$sudo_password\"" >> ~/.bashrc

echo "export DB_NAME=\"$db_name\"" >> ~/.bashrc

echo "export DB_TaBLE_NAME=\"$db_table_name\"" >> ~/.bashrc

source ~/.bashrc


# Updating and upgrading the software packages used by the current system
echo "$sudo_password" | sudo -S apt update -y
echo "$sudo_password" | sudo -S apt upgrade -y

# Installation of dependent libraries and development packages required by DLZ
echo "$sudo_password" | sudo -S apt install -y curl
echo "$sudo_password" | sudo -S apt install -y libreadline-dev
echo "$sudo_password" | sudo -S apt install -y gcc make pkg-config libuv1 libuv1-dev libssl-dev libcap-dev libxml2-dev 
echo "$sudo_password" | sudo -S apt install -y python3-pip libpq-dev

# Install PostgreSQL, initialize and start the PostgreSQL database service with the newly created user postgres
cd ${project_dir}/ActiveDNS/downloads
tar -zxvf postgresql-15.2.tar.gz
cd ${project_dir}/ActiveDNS/downloads/postgresql-15.2
echo "$sudo_password" | sudo -S chmod +x ./configure
echo "$sudo_password" | sudo -S ./configure
echo "$sudo_password" | sudo -S make 
echo "$sudo_password" | sudo -S make install

# Create a new user postgres and authorize the data folder

# Use the 'adduser' command to create a user and pass the password
echo -e "$sudo_password\n$new_user_password\n$new_user_password" | sudo -S adduser postgres
echo "$sudo_password" | sudo -S mkdir -p /mnt/data/postgres 
echo "$sudo_password" | sudo -S chown -R postgres:postgres /mnt/data/postgres
echo "$sudo_password" | sudo -S ln -s /usr/local/pgsql/bin/pg_ctl /usr/local/bin/pgsql_ctl
echo "$sudo_password" | sudo -S ln -s /usr/local/pgsql/bin/psql /usr/local/bin/psql
cd /mnt/data/postgres


# # Initializing and Starting the PostgreSQL Database Service
echo "$sudo_password" | sudo -S -u postgres /usr/local/pgsql/bin/initdb -D /mnt/data/postgres
echo "$sudo_password" | sudo -S -u postgres pgsql_ctl start -D /mnt/data/postgres

# # Create a database for storing DNS data (!)
echo "$sudo_password" | sudo -S -u postgres psql -c "CREATE DATABASE ${db_name};"



# Install BIND and configure compilation options
cd ${project_dir}/ActiveDNS/downloads
tar -zxvf bind-9.11.0.tar.gz
cd ${project_dir}/ActiveDNS/downloads/bind-9.11.0
echo "$sudo_password" | sudo -S chmod +x ./configure

# Specifies the target path for the installation, enables DLZ support for PostgreSQL databases, and disables OpenSSL support.
echo "$sudo_password" | sudo -S ./configure --prefix=/usr/local/bind/ --with-dlz-postgres --with-openssl=no
echo "$sudo_password" | sudo -S make 
echo "$sudo_password" | sudo -S make install
cd /usr/local/bind/etc/

# BIND invokes the rndc-confgen utility to generate an rndc.conf configuration file
echo "$sudo_password" | sudo -S touch rndc.conf named.conf rndc.key
echo "$sudo_password" | sudo -S sh -c '/usr/local/bind/sbin/rndc-confgen > rndc.conf'
echo "$sudo_password" | sudo -S sh -c 'cat rndc.conf >rndc.key'
echo "$sudo_password" | sudo -S sh -c 'tail -10 rndc.conf | head -9 | sed s/#\ //g > named.conf'

# Create log folders, refine configuration files
echo "$sudo_password" | sudo -S mkdir -p /usr/local/bind/var/logs

## Replace database name, data table name in configuration file with user input (!)
echo "$sudo_password" | sudo -S sh -c 'sed -i "s/\bdns\b/$db_name/g" ${project_dir}/ActiveDNS/config/basis-named.conf'
echo "$sudo_password" | sudo -S sh -c 'sed -i "s/\bdns_records\b/$db_table_name/g" ${project_dir}/ActiveDNS/config/basis-named.conf'

echo "$sudo_password" | sudo -S sh -c "cat ${project_dir}/ActiveDNS/config/basis-named.conf >> /usr/local/bind/etc/named.conf"

# Database initialization, starting the named service
# Creating a data storage folder
echo "$sudo_password" | sudo -S mkdir -p /mnt/data/postgres/data
echo "$sudo_password" | sudo -S cp  ${project_dir}/ActiveDNS/data/initial_data/v4_merge_result_without_2domains.csv /mnt/data/postgres/data
#(!) python3 ${project_dir}/ActiveDNS/Src/DNS_DATA_INIT.py
echo "$sudo_password" | sudo -S /usr/local/bind/sbin/named 
echo "\nThe BIND server is running normally!"









