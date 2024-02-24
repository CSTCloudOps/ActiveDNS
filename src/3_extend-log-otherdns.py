from concurrent.futures import ThreadPoolExecutor
import os
import time
import itertools
import datedays
from datetime import date, timedelta
import dns.resolver

project_dir = os.environ.get('PROJECT_DIR')

# def get_ip_list(domain, dns):
#     domain_ip = {}
#     ip_list = []
#     flag = True
#     while(flag):
#         len_before = len(ip_list)
#         result = os.popen('dig @' + dns + ' ' + domain + ' +short +time=1').readlines()
#         length_res = len(result)
#         if length_res == 0:
#             return None
#         else:
#             try:
#                 for item in result:
#                     if item[-2] == '.' or item[0] == ';':
#                         continue
#                     ip_list.append(item.rstrip('\n'))
#             except:
#                 # print("bad combination <dns domain>: " + dns + ' ' + domain)
#                 return None
#             ip_list = list(set(ip_list))
#             if len(ip_list) == len_before:
#                 flag = False
#     # print(ip_list)
#     domain_ip[domain] = ip_list
#     return domain_ip

def get_ip_list(domain, dns_server):
    resolver = dns.resolver.Resolver()
    resolver.nameservers = [dns_server]
    ip_set = set()
    new_ips_found = True

    while new_ips_found:
        try:
            new_ips_found = False
            answers = resolver.resolve(domain, 'A')
            for answer in answers:
                if answer.address not in ip_set:
                    new_ips_found = True
                    ip_set.add(answer.address)
        except Exception as e:
            break

    return {domain: list(ip_set)}
        
        
def get_domain(date):
    domain_list = []
    with open(file=f"{project_dir}/ActiveDNS/data/" + date + "/domain_querynum_merge.txt", mode="r", encoding="utf-8") as f:
        content_str = f.read().rstrip('\n')
        content_list = content_str.split('\n')
        cnt = 0
        for item in content_list:
            # if cnt > 10:
            #     break
            item_list = item.split(": ")
            domain = item_list[0]
            domain_list.append(domain)
            cnt += 1


    # return domain_list[0:1000]
    return domain_list

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
    time1 = time.time()
    dns_list = ["208.67.222.222", "8.8.8.8", "114.114.114.114", "114.114.115.115", "223.5.5.5", "223.6.6.6", "180.76.76.76", "119.29.29.29", "119.28.28.28", "101.226.4.6", "123.125.81.6", "140.207.198.6", "112.124.47.27", "114.215.126.16", "118.118.118.118", "1.2.4.8", "1.1.8.8"]

    date = str(datedays.getyesterday(days))

    domain_list = get_domain(date)
    # domain_list = ['www.baidu.com']

    dns_domain_tulpe = list(itertools.product(domain_list, dns_list))


    executor = ThreadPoolExecutor(max_workers=1024)
    results = executor.map(lambda x: get_ip_list(*x), dns_domain_tulpe)

    domain_ip_dict = {}

    for result in results:
        # print(result)
        if result == None:
            continue
        for domain in result:
            if domain not in domain_ip_dict:
                domain_ip_dict.update(result)
            domain_ip_dict[domain] = list(set(result[domain] + domain_ip_dict[domain]))
    # print(domain_ip_dict)

    time2 = time.time()
    print(time2 - time1)

    with open(file=f"{project_dir}/ActiveDNS/data/" + date + "/extend_domain_ip_otherdns.txt", mode="w", encoding="utf-8") as f:
        for domain in domain_ip_dict:
            f.write(domain + ': ' + str(domain_ip_dict[domain]) + '\n') 



if __name__ == '__main__':
    main()


