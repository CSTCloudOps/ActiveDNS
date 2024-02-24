from concurrent.futures import ThreadPoolExecutor
import os
import time
import itertools
import datedays
from datetime import date, timedelta

project_dir = os.environ.get('PROJECT_DIR')

def get_original_domain_iplist(date):
    domain_iplist = {}
    if not os.path.exists(f"{project_dir}/ActiveDNS/data/" + date + "/head_domain_ip_merge.txt"):
        return domain_iplist
    with open(file=f"{project_dir}/ActiveDNS/data/" + date + "/head_domain_ip_merge.txt", mode="r", encoding="utf-8") as f:
        content_str = f.read().rstrip('\n')
        content_list = content_str.split('\n')
        for item in content_list:
            item_list = item.split(": [")
            domain = item_list[0]
            ip_list = eval('[' + item_list[1])
            domain_iplist[domain] = ip_list

    return domain_iplist


def get_extend_domain_iplist_otherdns(date):
    domain_iplist = {}
    if not os.path.exists(f"{project_dir}/ActiveDNS/data/" + date + "/extend_domain_ip_otherdns.txt"):
        return domain_iplist
    with open(file=f"{project_dir}/ActiveDNS/data/" + date + "/extend_domain_ip_otherdns.txt", mode="r", encoding="utf-8") as f:
        content_str = f.read().rstrip('\n')
        content_list = content_str.split('\n')
        for item in content_list:
            item_list = item.split(": [")
            domain = item_list[0]
            ip_list = eval('[' + item_list[1])
            domain_iplist[domain] = ip_list

    return domain_iplist

def get_extend_domain_iplist_history(date):
    domain_iplist = {}
    if not os.path.exists(f"{project_dir}/ActiveDNS/data/" + date + "/final_domain_ip_v4.txt"):
        return domain_iplist
    with open(file=f"{project_dir}/ActiveDNS/data/" + date + "/final_domain_ip_v4.txt", mode="r", encoding="utf-8") as f:
        content_str = f.read().rstrip('\n')
        content_list = content_str.split('\n')
        for item in content_list:
            item_list = item.split(": [")
            domain = item_list[0]
            ip_list = eval('[' + item_list[1])
            domain_iplist[domain] = ip_list

    return domain_iplist

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
    # print(date_list)
    for i in range(1, len(date_list)):
        print(date_list[i])
        original_domain_iplist = get_original_domain_iplist(date_list[i])
        extend_domain_iplist_otherdns = get_extend_domain_iplist_otherdns(date_list[i])
        extend_domain_iplist_history = get_extend_domain_iplist_history(date_list[i-1])


        final_domain_iplist = {}
        for domain in original_domain_iplist:
            final_list = []
            original_iplist = original_domain_iplist[domain]
            try:
                extend_iplist_xxh = extend_domain_iplist_xxh[domain]
            except:
                extend_iplist_xxh = []

            try:
                extend_iplist_otherdns = extend_domain_iplist_otherdns[domain]
            except:
                extend_iplist_otherdns = []

            try:
                extend_iplist_history = extend_domain_iplist_history[domain]
            except:
                extend_iplist_history = []


            final_list = list(set(original_iplist + extend_iplist_xxh + extend_iplist_otherdns + extend_iplist_history))
            final_domain_iplist[domain] = final_list


        with open(file=f"{project_dir}/ActiveDNS/data/" + date_list[i] + "/final_domain_ip_v4.txt", mode="w", encoding="utf-8") as f:
            for domain in final_domain_iplist:
                f.write(domain + ": " + str(final_domain_iplist[domain]) + '\n')


if __name__ == '__main__':
    main()