#!/bin/bash

# Install cron
echo "$SUDO_PASSWORD" | sudo -S apt install cron -y

# Adding timed tasks to crontab
(crontab -l ; echo "0 0 * * * export PROJECT_DIR=${PROJECT_DIR} && ${PROJECT_DIR}/ActiveDNS/measure.sh > ${PROJECT_DIR}/ActiveDNS/log/measure.log") | crontab -
(crontab -l ; echo "*/10 * * * * export PROJECT_DIR=${PROJECT_DIR} && python3 ${PROJECT_DIR}/ActiveDNS/src/Monitor_ip.py > ${PROJECT_DIR}/ActiveDNS/log/Monitor_ip.log") | crontab -
echo "Scheduled task has been set up successfully!"



