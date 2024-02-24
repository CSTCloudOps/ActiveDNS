#!/bin/sh

. $HOME/.bashrc

current_time=$(date +"%Y-%m-%d %H:%M:%S")
last_day=$(date -d "yesterday" "+%Y-%m-%d")

base_path="${PROJECT_DIR}/ActiveDNS/data/${last_day}"
echo "current_time: $current_time\n"
echo $base_path


# Check if the file exists and execute the Python script
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

# Execute the Python script in turn and check if the output file exists
execute_python_script "${PROJECT_DIR}/ActiveDNS/src/0_extend-log.py" ${base_path}"/extend_domain_ip_xxh.txt"
execute_python_script "${PROJECT_DIR}/ActiveDNS/src/1_head_domain_ip.py" ${base_path}"/head_domain_ip.txt"
execute_python_script "${PROJECT_DIR}/ActiveDNS/src/2_merge_head_domain_ip.py" ${base_path}"/head_domain_ip_merge.txt"
execute_python_script "${PROJECT_DIR}/ActiveDNS/src/3_extend-log-otherdns_v3.py" ${base_path}"/extend_domain_ip_otherdns.txt"
execute_python_script "${PROJECT_DIR}/ActiveDNS/src/4_merge-log-all.py" ${base_path}"/final_domain_ip_v4.txt"
execute_python_script "${PROJECT_DIR}/ActiveDNS/src/5_ip_rtt.py" ${base_path}"/final_domain_sorted_ip_rtt_v4-all.txt"
execute_python_script "${PROJECT_DIR}/ActiveDNS/src/6_merge_result.py" ${base_path}"/v4_merge_result.txt"
execute_python_script "${PROJECT_DIR}/ActiveDNS/src/7_result2csv.py" ${base_path}"/v4_merge_result_without_2domains.csv"


echo "$SUDO_PASSWORD" | sudo -S mkdir -p /mnt/data/postgres/data/${last_day}
echo "$SUDO_PASSWORD" | sudo -S  sh -c 'cp  ${PROJECT_DIR}/ActiveDNS/data/${last_day}/v4_merge_result_without_2domains.csv /mnt/data/postgres/data/${last_day}'
python3 ${PROJECT_DIR}/ActiveDNS/src/Update_Database_Daily.py

# All scripts executed successfully
current_time=$(date "+%Y-%m-%d %H:%M:%S")
echo "\n${current_time} All Python scripts executed successfully!\n\n\n"

