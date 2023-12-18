#!/bin/bash

# 安装 cron
echo "$SUDO_PASSWORD" | sudo -S apt install cron -y

# 添加定时任务到 crontab
(crontab -l ; echo "0 0 * * * export PROJECT_DIR=${PROJECT_DIR} && ${PROJECT_DIR}/ActiveDNS/measure.sh > ${PROJECT_DIR}/ActiveDNS/Log/measure.log") | crontab -
(crontab -l ; echo "*/10 * * * * export PROJECT_DIR=${PROJECT_DIR} && python3 ${PROJECT_DIR}/ActiveDNS/Src/Monitor_ip.py > ${PROJECT_DIR}/ActiveDNS/Log/Monitor_ip.log") | crontab -
echo "Scheduled task has been set up successfully!"



