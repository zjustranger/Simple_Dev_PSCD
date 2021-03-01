import pymysql
import pandas as pd
from sqlalchemy import create_engine
import datetime

class DF_to_Mysql_DB:
    def __init__(self):
        self.connect = create_engine('mysql+pymysql://root:Admin_polestar1@10.234.9.200:3306/RPT')

    def send_to_mysql(self, table_name, df):
        df.to_sql(name=table_name, con=self.connect, if_exists='replace', index=False)

class Mysql_Analysis:
    def __init__(self):
        self.db = pymysql.connect(host='10.234.9.200', port=3306, user ='root', password='Admin_polestar1', db='RPT')
        self.cursor = self.db.cursor()

    def execute_sql(self, sql_str):
        self.cursor.execute(sql_str)
        rows = self.cursor.fetchall()
        return rows

    def __del__(self):
        self.cursor.close()
        self.db.close()

# 进行分析，取需要的数据，生成统计结果
ana_conn = Mysql_Analysis()
# 抓取72小时内每张卡的最后一次刷卡记录，筛选出最后一次是刷进工厂的记录，并补上相应的员工信息
sql_ana_detail = '''
select lg.card_no, lg.last_grant_time, tp.logical_device, tp.lname, tp.fname, tp.company, tp.department from
(select card_no, max(event_time) last_grant_time from prowatch_data
where logical_device like 'PSCD%Gate%' and event_time > date_sub(CURRENT_TIMESTAMP(), interval '3 00:00:00' day_second) and status = 'Active'
group by card_no) lg left join prowatch_data tp on (lg.card_no = tp.card_no and lg.last_grant_time = tp.event_time) where lower(tp.logical_device) like '%in'
'''
rslt_data = ana_conn.execute_sql(sql_ana_detail)

last_refresh_time = ana_conn.execute_sql("select last_end FROM config_data_extraction where program = 'prowatch_data_increase_get'")
last_refresh_time = last_refresh_time[0][0]
last_refresh_time2 = last_refresh_time - datetime.timedelta(hours=8)

# 将数据转为DataFrame，整理后写入Mysql数据库
rslt_df_detail = pd.DataFrame(rslt_data)
rslt_df_detail.columns = ['Card_No','Enter_Timestamp','Enter_Location','LNAME','FNAME','Company','Department']
rslt_df_detail['Refresh_Timestamp'] = last_refresh_time
rslt_df_detail['Refresh_Timestamp2'] = last_refresh_time2

for i in range(len(rslt_df_detail)):
    rslt_df_detail.iloc[i,6] = rslt_df_detail.iloc[i,6].upper().replace('\n','').replace('\r','').replace(' ','')

write_conn = DF_to_Mysql_DB()
write_conn.send_to_mysql('in_plant_details', rslt_df_detail)

print(1)






