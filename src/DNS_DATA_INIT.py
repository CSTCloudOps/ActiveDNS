import psycopg2
import time
import datedays
import numpy as np
import os
from datetime import date, timedelta

class DB:

    def __init__(self,host,port,user,password,db):
        self.conn=psycopg2.connect(host=host, port=port, user=user, password=password, database=db)
        self.cur=self.conn.cursor()

    def __del__(self):
        self.cur.close()
        self.conn.close()

    def table_exists(self, table_name):
        self.cur.execute("SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = %s)", (table_name,))
        table_exists = self.cur.fetchone()[0]
        return table_exists

    def query(self,sql):
        self.cur.execute(sql)
        return self.cur.fetchall()

    def execu(self,sql):
        try:
            self.cur.execute(sql)
            self.conn.commit()
#             print("good")
        except Exception as e:
            self.conn.rollback()
            print(str(e))

def main(days=1):
    time1 = time.time()

    project_dir = os.environ.get('PROJECT_DIR')

    db=DB('127.0.0.1', 5432, 'postgres', '', 'dns')

    delet_backup = 'drop table dns_records_copy;'
    delet_table = 'drop table dns_records;'

    create_backup = 'CREATE TABLE if not exists dns_records_copy(zone text,host text,ttl integer,type text,mx_priority integer,data text,resp_person text,serial integer,refresh integer,retry integer,expire integer,minimum integer,rtt FLOAT,score1 FLOAT,score2 FLOAT,domain_query_time integer,ip_update_time integer);'
    create_table = 'CREATE TABLE if not exists dns_records(id SERIAL primary key,zone text,host text,ttl integer,type text,mx_priority integer,data text,resp_person text,serial integer,refresh integer,retry integer,expire integer,minimum integer,rtt FLOAT,score1 FLOAT,score2 FLOAT,domain_query_time integer,ip_update_time integer);'
    
    unique_index_backup = 'alter table dns_records_copy add constraint domain_ip_copy unique(zone, data);'
    unique_index_table = 'alter table dns_records add constraint domain_ip unique(zone, data);'
    # 检查表是否存在
    table_name = "dns_records"  
    table_exist=db.table_exists(table_name)
    if table_exist:
        db.execu(delet_backup)
        db.execu(delet_table)

    db.execu(create_backup)
    db.execu(create_table)

    db.execu(unique_index_backup)
    db.execu(unique_index_table)

    # year_month_day = '2023-11-12'
    year_month_day = str(datedays.getyesterday(days))
    # csv_path = "/mnt/data/postgres/data/" + year_month_day + "/merge_result.csv"
    csv_path = "/mnt/data/postgres/data/v4_merge_result_without_2domains.csv"
    # csv_path = f"{project_dir}/ActiveDNS/Data/initial_data/v4_merge_result_without_2domains.csv"
    copy = 'copy dns_records_copy (zone, host, ttl, type, mx_priority, data, resp_person, serial, refresh, retry, expire, minimum, rtt, score1, score2, domain_query_time, ip_update_time) FROM \'{csv_path}\' DELIMITER \',\' CSV HEADER;'.format(csv_path=csv_path)   
    upsert = 'INSERT INTO dns_records (zone, host, ttl, type, mx_priority, data, resp_person, serial, refresh, retry, expire, minimum, rtt, score1, score2, domain_query_time, ip_update_time) \
SELECT zone, host, ttl, type, mx_priority, data, resp_person, serial, refresh, retry, expire, minimum, rtt, score1, score2, domain_query_time, ip_update_time \
FROM dns_records_copy \
ON CONFLICT (zone, data) DO UPDATE \
SET rtt = EXCLUDED.rtt, score1 = EXCLUDED.score1, score2=EXCLUDED.score2,ip_update_time=EXCLUDED.ip_update_time;'
    # print(upsert)
    # print(copy)

    print('copying')
    # print(copy)
    db.execu(copy)
    print('upserting')
    db.execu(upsert)
    time2 = time.time()
    print(time2-time1)
    print(f"{year_month_day} Data update completed!")


if __name__ == '__main__':
    main()