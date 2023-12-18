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

