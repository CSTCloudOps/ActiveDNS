from concurrent.futures import ThreadPoolExecutor
import os
import time
import itertools
import datedays
from datetime import date, timedelta
from collections import Counter

project_dir = os.environ.get('PROJECT_DIR')

def get_domain_querynum(date, filename):
    domain_querynum = {}
    with open(file=f"{project_dir}/ActiveDNS/Data/" + date +"/" + filename, mode="r", encoding="utf-8") as f:
        content_str = f.read().rstrip('\n')
        content_list = content_str.split('\n')
        for item in content_list:
            item_list = item.split(": ")
            domain = item_list[0]
            querynum = eval(item_list[1])
            domain_querynum[domain] = querynum

    # return domain_list[0:1000]
    return domain_querynum


def get_domain_iplist(date, filename):
    domain_iplist = {}
    with open(file=f"{project_dir}/ActiveDNS/Data/" + date +"/" + filename, mode="r", encoding="utf-8") as f:
        content_str = f.read().rstrip('\n')
        content_list = content_str.split('\n')
        for item in content_list:
            item_list = item.split(": [")
            domain = item_list[0]
            ip_list = eval('[' + item_list[1])
            domain_iplist[domain] = ip_list

    # return domain_list[0:1000]
    return domain_iplist



# def get_date_list(start, end):
#     # 左开右闭
#     start_date = date.fromisoformat(start)
#     end_date = date.fromisoformat(end)

#     date_range = [
#         # end_date - timedelta(days=i)  # For date objects
#         (end_date - timedelta(days=i)).isoformat()  # For ISO-8601 strings
#         for i
#         in range((end_date - start_date).days)
#     ]
#     reverse_range = list(reversed(date_range))

#     return reverse_range



def merge(x, y):
    X, Y = Counter(x), Counter(y)
    return sorted(dict(X + Y).items(), key=lambda x: x[1], reverse=True)




def main(days=1):
    date = str(datedays.getyesterday(days))

    print(date)
    domain_querynum_rjy = get_domain_querynum(date, "domain_querynum.txt")
    domain_querynum_xxh = get_domain_querynum(date, "domain_querynum_xxh.txt")

    domain_ip_rjy = get_domain_iplist(date, "head_domain_ip.txt")
    domain_ip_xxh = get_domain_iplist(date, "extend_domain_ip_xxh.txt")


    merge_tuple = merge(domain_querynum_rjy, domain_querynum_xxh)

    head_domain_ip_merge = {}

    lenth = 100000
    if len(merge_tuple) < 100000:
        lenth = len(merge_tuple)

    for j in range(lenth):
        domain = merge_tuple[j][0]
        try:
            l1 = domain_ip_rjy[domain]
        except:
            l1 = []

        try:
            l2 = domain_ip_xxh[domain]
        except:
            l2 = []
        
        head_domain_ip_merge[domain] = list(set(l1 + l2))


    with open(file=f"{project_dir}/ActiveDNS/Data/" + date + "/domain_querynum_merge.txt", mode="w", encoding="utf-8") as f:
        for j in range(lenth):
            f.write(merge_tuple[j][0] + ": " + str(merge_tuple[j][1]) + '\n')


    with open(file=f"{project_dir}/ActiveDNS/Data/" + date + "/head_domain_ip_merge.txt", mode="w", encoding="utf-8") as f:
        for domain in head_domain_ip_merge:
            f.write(domain + ": " + str(head_domain_ip_merge[domain]) + '\n')


if __name__ == '__main__':
    start_time = time.time()
    main(1)
    end_time = time.time()