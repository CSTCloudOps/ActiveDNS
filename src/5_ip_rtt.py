import socket
import time
from ping3 import ping, verbose_ping
from concurrent.futures import ThreadPoolExecutor
import datedays
from datetime import date, timedelta
import os

project_dir = os.environ.get('PROJECT_DIR')

def pings(ip_list):
    ips_rtt = dict()
    executor = ThreadPoolExecutor(max_workers=1024)
    futures = [executor.submit(ping, ip, timeout=1) for ip in ip_list]
    for index, future in enumerate(futures) :
        try:
            ips_rtt[ip_list[index]] = future.result()
        except Exception as e:
            try:
                print(e)
            except Exception as ee:
                pass
                # print("Cannot ping some IP.")
    return ips_rtt


def get_domain_ip(dir_path):
    time1 = time.time()
    ips = []
    domain_ipnum = {}
    domain_ips = {}
    cnt = 0
    with open(file=dir_path + "/final_domain_ip_v4.txt", mode="r", encoding="utf-8") as f:
        content_str = f.read().rstrip('\n')
        content_list = content_str.split('\n')
        print(len(content_list))
        # for item in content_list:
        for item in content_list:
            # if cnt > 10:
            #     break
            # cnt += 1
            item_list = item.split(": [")
            domain_name = item_list[0]
            ip_list = eval('[' + item_list[1])
            ips.extend(ip_list)

            domain_ipnum[domain_name] = len(ip_list)
            domain_ips[domain_name] = ip_list
    time2 = time.time()
    print("Processing list time: {time}".format(time=time2-time1))
    
    return ips, domain_ipnum, domain_ips


def get_date_list(start, end):
    
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
    date = str(datedays.getyesterday(days))


    dir_path = f"{project_dir}/ActiveDNS/data/" + date

    
    ip_rttlist = {}
    domain_ip_rtt = {}
    ip_list, domain_ipnum, domain_iplist = get_domain_ip(dir_path)
    print("length of ip_list: {length}".format(length=len(ip_list)))

    
    time1 = time.time()

    
    
    new_ip_list = list(set(ip_list))
    new_ip_list.sort(key=ip_list.index)
    print("length of new_ip_list: {length}".format(length=len(new_ip_list)))

    with open(file=dir_path + "/final_ip.txt", mode="w", encoding="utf-8") as f:
        for ip in new_ip_list:
            f.write(ip + '\n')

    time2 = time.time()
    print("remove duplicate ip time: {time}".format(time=time2-time1))

    for ip in new_ip_list:
        ip_rttlist[ip] = []
    # ping IP
    log_flag=0
    for i in range(0, 10):
        ips_rtt = pings(new_ip_list)

        time3 = time.time()
        print("ping ips time: {time}".format(time=time3-time2))

        
        if log_flag == 0:
            useful_ip = list(ips_rtt.keys())
            unuseful_ip = list(set(new_ip_list).difference(set(useful_ip)))

            with open(file=dir_path + "/unuseful_ip.txt", mode="w", encoding="utf-8") as f:
                for ip in unuseful_ip:
                    f.write(ip + '\n')
            log_flag = 1
            print(unuseful_ip)

        for ip in ips_rtt:
            ip_rttlist[ip].append(ips_rtt[ip])

        time4 = time.time()
        print("combine domain and its ips time: {time}".format(time=time4-time3))

    for domain in domain_iplist:
        domain_ip_rtt[domain] = {}
        for ip in domain_iplist[domain]:
            if ip not in unuseful_ip:
                if ip not in domain_ip_rtt[domain]:
                    domain_ip_rtt[domain][ip] = ip_rttlist[ip]


    with open(file=dir_path + "/final_domain_sorted_ip_rtt_v4-all.txt", mode="w", encoding="utf-8") as f:
        for domain in domain_ip_rtt:
            f.write(str(domain) + ', ' + str(domain_ip_rtt[domain]) + '\n')


if __name__ == '__main__':
    main()
