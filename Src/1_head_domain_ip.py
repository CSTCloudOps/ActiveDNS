import requests
import time
import os
import datedays
from ping3 import ping, verbose_ping
from concurrent.futures import ThreadPoolExecutor
from datetime import date, timedelta

project_dir = os.environ.get('PROJECT_DIR')

def unix_time(date):
    timeArray = time.strptime(date, "%Y-%m-%d %H:%M:%S")
    timestamp = time.mktime(timeArray)
    return timestamp


def getTime_m(date):
    start_s = unix_time(date)
    start_ns = start_s * (10 ** 9)
    end_ns = (start_s + 60) * (10 ** 9)
    return start_ns, end_ns


def local_time(timestamp):
    time_local = time.localtime(timestamp)
    date = time.strftime("%Y-%m-%d %H:%M:%S", time_local)
    return date


def get_date_mkdir(days=1):
    year_month_day = str(datedays.getyesterday(days))
    dir_path = f"{project_dir}/ActiveDNS/Data/" + year_month_day
    if os.path.exists(dir_path):
        print("direction is already exist!")
        return year_month_day, dir_path
    os.makedirs(dir_path)
    return year_month_day, dir_path

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

def get_domains_ips(start, timelong=1440):
    dict_cnt = {"cnt": 0}
    dict_domain_ip_num = {}
    dict_domain_query = {}
    for i in range(0, timelong):
        # 计算一分钟的开始和结束时间, 左闭右开
        begin = start

        start_ns = i * 60 * (10 ** 9) + begin
        end_ns = 60 * (10 ** 9) + start_ns
        print(local_time(start_ns / (10 ** 9)))

        url = "http://223.193.36.79:33242/loki/api/v1/query_range?query={job=%22dns%22}&limit=5000000&start=" + f"{start_ns:.0f}" + "&end=" + f"{end_ns:.0f}"
        response = requests.get(url)

        # 从json数据中取出日志数据
        try:
            value = eval(response.text)["data"]["result"][0]["values"]
        except:
            print(local_time(start_ns / (10 ** 9)) + " no data!!!")
            continue

        # ["timeStamp", "x x 01-Nov-2022 07:58:29.354 x ip ..."]
        for query in value:
            # list_query 日志数据
            list_query = query[1].split()
            # 过滤怪异的行
            if len(list_query) >= 31 and list_query[4] == "client":
                name = list_query[1]
                domain = list_query[9]
                domain = domain.lower()
                response_type = list_query[12]

                # 过滤权威
                if name != "{name=cache_1}" and name != "{name=cache_2}" or list_query[30] != "Response:" or response_type == 'NXDOMAIN':
                    continue

                # 记录域名的访问次数时需要考虑cname，否则某些域名没有ip
                dict_cnt['cnt'] += 1
                if domain not in dict_domain_query:
                    dict_domain_query[domain] = 1
                else:
                    dict_domain_query[domain] += 1
                    
                for i in range(30, len(list_query)):
                    # if list_query[i] == 'A' or list_query[i] == 'AAAA':
                    if list_query[i] == 'A':
                        ip = list_query[i + 1].split(';')[0]

                        if domain not in dict_domain_ip_num:
                            dict_domain_ip_num[domain] = {ip: 1}
                        elif ip not in dict_domain_ip_num[domain]:
                            dict_domain_ip_num[domain][ip] = 1
                        else:
                            dict_domain_ip_num[domain][ip] += 1
        print(dict_cnt)
    return dict_domain_ip_num, dict_domain_query


def get_head_domain_ip(days=1, timelong=1440, dive_rate=10):
    year_month_day, dir_path = get_date_mkdir(days)
    try:
        date = year_month_day + " 00" + ":00:00"
    except:
        return
    start, end = getTime_m(date)

    dict_domain_ip_num, dict_domain_query = get_domains_ips(start, timelong)
    print(dict_domain_ip_num)
    
    list_sorted_domain_query = sorted(dict_domain_query.items(), key=lambda x: x[1], reverse=True)
    
    head_lenth = len(list_sorted_domain_query) // dive_rate
    if head_lenth < 100000 and head_lenth > 10000:
        head_lenth = 100000
    print("head lenth: {head}".format(head=head_lenth))
    
    head_domain = []
    for i in range(0, head_lenth):
        head_domain.append(list_sorted_domain_query[i][0])
    print(head_domain)
        
    head_domain_ip = {}
    for domain in head_domain:
        ip_list=[]
        try:
            ip_list.extend(dict_domain_ip_num[domain])
        except:
            ip_list = []
        finally:    
            head_domain_ip[domain] = ip_list
    
    
    
    with open(file=dir_path + "/head_domain_ip.txt", mode="w", encoding="utf-8") as f:
        for domain in head_domain_ip:
            f.write(domain + ': ' + str(head_domain_ip[domain]) + '\n') 
            
    with open(file=dir_path + "/domain_querynum.txt", mode="w", encoding="utf-8") as f:
        for i in range(head_lenth):
            f.write(list_sorted_domain_query[i][0] + ': ' + str(list_sorted_domain_query[i][1]) + '\n') 
            
  

if __name__ == '__main__':
    
    start_time = time.time()
    
    get_head_domain_ip(1)
    end_time = time.time()
    
    print("get data time:{time}".format(time=end_time-start_time))