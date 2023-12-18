import time,os
from ping3 import ping, verbose_ping
from concurrent.futures import ThreadPoolExecutor
import datedays
from datetime import date, timedelta, datetime
import dns.resolver
import psycopg2

project_dir = os.environ.get('PROJECT_DIR')

class DB:

    def __init__(self,host,port,user,password,db):
        self.conn=psycopg2.connect(host=host, port=port, user=user, password=password, database=db)
        self.cur=self.conn.cursor()

    def __del__(self):
        self.cur.close()
        self.conn.close()

    def query(self,sql):
        self.cur.execute(sql)
        return self.cur.fetchall()

    def execu(self,sql):
        try:
            self.cur.execute(sql)
            self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            print(str(e))

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


def get_useful_ip(dir_path):
    time1 = time.time()
    ips = []

    cnt = 0
    with open(file=dir_path + "/final_ip.txt", mode="r", encoding="utf-8") as f:
        content_str = f.read().rstrip('\n')
        content_list = content_str.split('\n')
        print(len(content_list))
        # for item in content_list:
        for ip in content_list:
            # if cnt > 10:
            #     break
            # cnt += 1
            ips.append(ip)
    time2 = time.time()
    print("Processing list time: {time}".format(time=time2-time1))
    
    return ips



def get_unuseful_ip(dir_path):
    time1 = time.time()
    ips = []

    cnt = 0
    with open(file=dir_path + "/unuseful_ip.txt", mode="r", encoding="utf-8") as f:
        content_str = f.read().rstrip('\n')
        content_list = content_str.split('\n')
        print(len(content_list))
        # for item in content_list:
        for ip in content_list:
            # if cnt > 10:
            #     break
            # cnt += 1
            ips.append(ip)
    time2 = time.time()
    print("Processing list time: {time}".format(time=time2-time1))
    
    return ips


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


def main(days=1):
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    dns_list = ["208.67.222.222", "8.8.8.8", "114.114.114.114", "114.114.115.115", "223.5.5.5", "223.6.6.6", "180.76.76.76", "119.29.29.29", "119.28.28.28", "101.226.4.6", "123.125.81.6", "140.207.198.6", "112.124.47.27", "114.215.126.16", "118.118.118.118", "1.2.4.8", "1.1.8.8"]
    date=str(datedays.getyesterday(days))
    dir_path = f"{project_dir}/ActiveDNS/Data/" + date
    file1=dir_path + "/unuseful_ip.txt"
    file2=dir_path + "/final_ip.txt"
    if not os.path.exists(dir_path) or not os.path.exists(file1) or not os.path.exists(file2):
        date=str(datedays.getyesterday(2))
        dir_path = f"{project_dir}/ActiveDNS/Data/" + date
        file1=dir_path + "/unuseful_ip.txt"
        file2=dir_path + "/final_ip.txt"
        if not os.path.exists(dir_path) or not os.path.exists(file1) or not os.path.exists(file2):
            print(f"{current_time} No IP available for update!")
            return 0;
    print(f"{current_time} Updating the IPs of {date}!")
    origin_ip_list = get_useful_ip(dir_path)
    unuseful_ip_list = get_unuseful_ip(dir_path)
    new_ip_list = list(set(origin_ip_list) - set(unuseful_ip_list))

    print("length of ip_list: {length}".format(length=len(new_ip_list)))

    
    time_start = time.time()


    # ping IP
    ips_rtt = pings(new_ip_list)

    print("ping ips time: {time}".format(time=time.time()-time_start))

    # 筛选出ping不了的IP
    # useful_ip = list(ips_rtt.keys())
    # unuseful_ip = list(set(new_ip_list).difference(set(useful_ip)))
    # with open(file=dir_path + "/unuseful_ip.txt", mode="w", encoding="utf-8") as f:
    #     for ip in unuseful_ip:
    #         f.write(ip + '\n')
    useful_ip = list(ips_rtt.keys())
    new_unuseful_ip = list(set(new_ip_list).difference(set(useful_ip)))
    print(len(new_unuseful_ip))

    # new_unuseful_ip = ["220.181.38.150"]


    db=DB('127.0.0.1', 5432, 'postgres', '', 'dns')
    zone_index = "CREATE INDEX zone_index ON dns_records (zone);"
    ip_index = "CREATE INDEX ip_index ON dns_records (data);"
    db.execu(zone_index)
    db.execu(ip_index)
    domain_list = []
    for ip in new_unuseful_ip:
        query = "select zone from dns_records where data=\'{data}\';".format(data=ip)
        query_result = db.query(query)
        print(query_result)
        delete = "DELETE FROM dns_records WHERE data=\'{data}\';".format(data=ip)
        # db.execu(delete)

        for item in query_result:
            domain = item[0]
            domain_list.append(domain)
            query_cnt_zone = "SELECT COUNT(*) FROM dns_records WHERE zone = \'{domain}\';".format(domain=domain)
            cnt_zone = db.query(query_cnt_zone)
            # print(cnt_zone[0][0])
            if cnt_zone[0][0] == 0:
                ip_list = get_ip_list(domain, dns_list)
                ips_rtt = pings(ip_list)
                for ip in ips_rtt:
                    if ips_rtt[ip]:
                        insert_table_domain_ip_word = "INSERT INTO dns_records (zone,host,type,data,ttl,retry,rtt,score1,score2,domain_query_time,ip_update_time) VALUES (\'{zone}\',\'{host}\',\'{type}\',\'{data}\',{ttl},{retry},{rtt},{score1},{score2},{time},{time});".format(zone=domain, host='@', type='A', data=ip, ttl=80, retry=10, rtt=ips_rtt[ip], score1=ips_rtt[ip], score2=ips_rtt[ip], time=int(time.time()))
                        db.execu(insert_table_domain_ip_word)


    with open(file=dir_path + "/changed_domain.txt", mode="w", encoding="utf-8") as f: 
        for domain in domain_list:    
            f.write(domain + '\n') 
    print(f"{current_time} IP update completed!")


if __name__ == '__main__':
    main()
