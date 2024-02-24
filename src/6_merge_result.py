from concurrent.futures import ThreadPoolExecutor
import os
import time
import itertools
import datedays
from datetime import date, timedelta

project_dir = os.environ.get('PROJECT_DIR')

def get_before_result(year_month_day):
    domain_ip_rttlist = {}
    data_file=f"{project_dir}/ActiveDNS/data/" + year_month_day + "/v4_merge_result.txt"
    if not os.path.exists(data_file):
        return domain_ip_rttlist
    with open(file=f"{project_dir}/ActiveDNS/data/" + year_month_day + "/v4_merge_result.txt", mode="r", encoding="utf-8") as f:
        content_str = f.read().rstrip('\n')
        content_list = content_str.split('\n')
        for item in content_list:
            item_list = item.split(", {")
            domain = item_list[0]
            ip_rttlist_dict = eval('{' + item_list[1])
            domain_ip_rttlist[domain] = ip_rttlist_dict

    # return domain_list[0:1000]
    return domain_ip_rttlist

def get_now_result(year_month_day):
    domain_ip_rttlist = {}
    if not os.path.exists(f"{project_dir}/ActiveDNS/data/" + year_month_day + "/final_domain_sorted_ip_rtt_v4-all.txt"):
        return domain_ip_rttlist
    with open(file=f"{project_dir}/ActiveDNS/data/" + year_month_day + "/final_domain_sorted_ip_rtt_v4-all.txt", mode="r", encoding="utf-8") as f:
        content_str = f.read().rstrip('\n')
        content_list = content_str.split('\n')
        for item in content_list:
            item_list = item.split(", {")
            domain = item_list[0]
            ip_rttlist_dict = eval('{' + item_list[1])
            domain_ip_rttlist[domain] = ip_rttlist_dict

    # return domain_list[0:1000]
    return domain_ip_rttlist


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

    start = str(datedays.getyesterday(days+2))
    end = str(datedays.getyesterday(days))
    date_list = get_date_list(start, end)
    print(date_list)
    for i in range(1, len(date_list)):
        print(date_list[i])
        time1 = time.time()
        before_result = get_before_result(date_list[i-1])
        now_result = get_now_result(date_list[i])
        
        # final_result = now_result.copy()
        # final_result.update(before_result)
        final_result = before_result.copy()
        final_result.update(now_result)
        time2 = time.time()
        print(time2-time1)



        with open(file=f"{project_dir}/ActiveDNS/data/" + date_list[i] + "/v4_merge_result.txt", mode="w", encoding="utf-8") as f:
            for domain in final_result:
                f.write(domain + ", " + str(final_result[domain]) + '\n')


if __name__ == '__main__':
    main()