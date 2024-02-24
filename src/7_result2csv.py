import csv
import time
from datetime import date, timedelta
import numpy as np
import datedays
import os

project_dir = os.environ.get('PROJECT_DIR')

def read_data(year_month_day):
    domain_ips_rttlist = {}
    dir_path = f"{project_dir}/ActiveDNS/data/" + year_month_day 
    with open(file=dir_path + "/v4_merge_result.txt", mode="r", encoding="utf-8") as f:
        content_str = f.read().rstrip('\n')
        content_list = content_str.split('\n')
        for item in content_list:
            item_list = item.split(", {")
            domain_name = item_list[0]
            # print(domain_name)
            domain_ips_rttlist[domain_name] = {}

            flag=True
            dict_ip_rtt_list = eval('{' + item_list[1])
            copy = dict_ip_rtt_list.copy()
            cnt_ip = len(copy)
            for ip in copy:
                for i in range(0, len(copy[ip])):
                    if copy[ip][i] is False:
                        del dict_ip_rtt_list[ip]
                        break
                    if copy[ip][i] is None:
                        dict_ip_rtt_list[ip][i] = 1.0
                        continue
            
            for ip in dict_ip_rtt_list:
                if dict_ip_rtt_list[ip] == []:
                    continue
                result_list = []
                no_rtt = 0
                rtt_list = dict_ip_rtt_list[ip].copy()
                for rtt in rtt_list:
                    if rtt == 1.0:
                        rtt_list.remove(1.0)
                        no_rtt += 1
                if no_rtt == len(dict_ip_rtt_list[ip]):
                    rtt_list = dict_ip_rtt_list[ip]
                min_rtt = min(rtt_list)
                arr_rtt = np.array(rtt_list)
                var = np.var(arr_rtt)
                std_deviation = np.sqrt(var)
                score1 = (0.7 * min_rtt + 0.1 * std_deviation) * (1 + no_rtt/10)
                score2 = (0.8 * min_rtt + 0.1 * std_deviation) * (1 + no_rtt/10)
                result_list.append(min_rtt)
                result_list.append(score1)
                result_list.append(score2)
                
                if ip not in domain_ips_rttlist[domain_name]:
                    domain_ips_rttlist[domain_name][ip] = result_list
            
    return domain_ips_rttlist

def write_data(domain_ips_rttlist, year_month_day):
    data_header = ['zone', 'host', 'ttl', 'type', 'mx_priority', 'data', 'resp_person', 'serial', 'refresh', 'retry', 'expire', 'minimum', 'rtt', 'score1', 'score2', 'domain_query_time', 'ip_update_time']

    dir_path = f"{project_dir}/ActiveDNS/data/" + year_month_day
    with open(file=dir_path + "/v4_merge_result_without_2domains.csv", mode="w", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(data_header)

        for domain in domain_ips_rttlist:
            if len(domain.split('.')) == 2:
                continue
            for ip in domain_ips_rttlist[domain]:
                result_list = []
                result_list.append(domain)
                result_list.append('@')
                result_list.append(int(80))
                result_list.append('A')
                result_list.append(None)
                result_list.append(ip)
                result_list.append(None)
                result_list.append(None)
                result_list.append(None)
                result_list.append(10)
                result_list.append(None)
                result_list.append(None)
                result_list.append(domain_ips_rttlist[domain][ip][0])
                result_list.append(domain_ips_rttlist[domain][ip][1])
                result_list.append(domain_ips_rttlist[domain][ip][2])
                result_list.append(int(time.time()))
                result_list.append(int(time.time()))

                writer.writerow(result_list)

def get_date_list(start, end):
    # 左开右闭
    start_date = date.fromisoformat(start)
    end_date = date.fromisoformat(end)

    date_range = [
        # end_date - timedelta(days=i)  # For date objects
        (end_date - timedelta(days=i)).isoformat()  # For ISO-8601 strings
        for i
        in range((end_date - start_date).days)
    ]
    reverse_range = list(reversed(date_range))

    return reverse_range

def main(days=1):
    year_month_day = str(datedays.getyesterday(days))


    print(year_month_day)
    time1 = time.time()
    write_data(read_data(year_month_day), year_month_day)
    time2 = time.time()
    print(time2-time1)



if __name__ == '__main__':
    main()
