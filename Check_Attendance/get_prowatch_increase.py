import pymssql
import pymysql
import pandas as pd
from sqlalchemy import create_engine
import datetime

class Prowatch_DBConnection:
    def __init__(self):
        self.connection = pymssql.connect('JIASVW1192.jia.volvocars.net\DBSQLPWNTAP','APPLOCA','Volvo2020','HSC22')
        if self.connection:
            print('连接成功')
        self.cursor = self.connection.cursor()

    def execute_sql(self, sql_str):
        self.cursor.execute(sql_str)
        rows = self.cursor.fetchall()
        return rows

    def __del__(self):
        self.cursor.close()
        self.connection.close()

class DF_to_Mysql_DB:
    def __init__(self, df):
        self.connect = create_engine('mysql+pymysql://root:Admin_polestar1@10.234.9.200:3306/RPT')
        self.df = pd.DataFrame(df)

    def add_column_name(self, columns):
        self.df.columns = columns

    def send_to_mysql(self, table_name):
        self.df.to_sql(name=table_name, con=self.connect, if_exists='append', index=False)

class Mysql_Analysis:
    def __init__(self):
        self.db = pymysql.connect(host='10.234.9.200', port=3306, user ='root', password='Admin_polestar1', db='RPT')
        self.cursor = self.db.cursor()

    def execute_select_sql(self, sql_str):
        self.cursor.execute(sql_str)
        rows = self.cursor.fetchall()
        return rows

    def execute_idu_sql(self, sql_str):
        try:
            self.cursor.execute(sql_str)
            self.db.commit()
        except:
            self.db.rollback()

    def __del__(self):
        self.cursor.close()
        self.db.close()


# step0. 准备工作
logfile = open("running.log", "a")
print('*'*100, file=logfile)


# step1. 从mysql取出上次程序的执行时间
print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), "    ", u"Step 1. Getting the last running time from control table...", file=logfile)

last_run = Mysql_Analysis()
sql1 = "select date_format(last_end, '%Y%m%d %H:%i:%s'), date_format(last_start, '%Y%m%d %H:%i:%s') from config_data_extraction where program = 'prowatch_data_increase_get' "
rslt = last_run.execute_select_sql(sql1)
last_end, last_start = rslt[0]

print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), "    ", u"Get last running parameter successfully: last start:{}, last end:{}.".format(last_start, last_end), file=logfile)

# 确定这次抓数的时间范围
if last_end:
    new_start = last_end
elif last_start:
    new_start = last_start
else:
    exit(2)

new_end = datetime.datetime.now().strftime('%Y%m%d %H:%M:%S')

print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), "    ", u"Time range for data extraction this time has been defined: new_start:{}, new_end:{}".format(new_start, new_end), file=logfile)

# 将数据库表里比这次抓数开始时间晚的数据全部清掉，避免出现重复数据
print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), "    ", u"Deleting the data in table later than new start time, to prevent duplicated data...", file=logfile)

sql2 = "delete from prowatch_data where event_time > STR_TO_DATE('{}', '%Y%m%d %H:%i:%s')".format(new_start)
last_run.execute_idu_sql(sql2)

print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), "    ", u"Delete finished.", file=logfile)

# step2. 从Prowatch数据库里取这部分增量数据
# 由于需要用到between，将start的时间加0.5秒，Prowatch中刷卡数据精确到秒，所以加0.5秒可以避免刷到重复的数据
new_start_tmp = new_start + '.500'
sql3 = '''
select ft_evnt_dat, fc_logdevdescrp, fc_evnt_descrp, FC_LOCATION, FC_CARDNO, FC_LNAME, FC_FNAME, FC_COMP_NAME, FC_DEPARTMENT, FC_STAT_COD, FC_CDSID, FC_EMPLOYEENUMBER from ACSYSTEMPWEVENT
where FT_EVNT_DAT between convert(datetime, '{}', 101) and convert(datetime, '{}', 101) and upper(FC_LOGDEVDESCRP) like 'PSCD%' order by FT_EVNT_DAT
'''.format(new_start_tmp, new_end)

# 连接Prowatch数据库，取数据
print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), "    ", u"Step2. Connecting Prowatch database and getting incremental data...", file=logfile)

pro_conn = Prowatch_DBConnection()
transfer_data = pro_conn.execute_sql(sql3)

print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), "    ", u"Getting data successfully!", file=logfile)

# step3. 将增量数据写入到mysql数据库中
rpt_conn = DF_to_Mysql_DB(transfer_data)
rpt_conn.add_column_name(['event_time','logical_device','event_descr','location','card_no','lname','fname','company','department','status','cdsid','employee_no'])

print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), "    ", u"Step3. Connecting MySQL DB and insert incremental data into table...", file=logfile)

rpt_conn.send_to_mysql('prowatch_data')

print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), "    ", u"Inserted successfully.", file=logfile)

# step4. 更新控制表里的数值，将最后一次执行时间抓数范围更新进去
print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), "    ", u"Step4. Updating the control table, refresh the last start time and last end time for this job...", file=logfile)

sql4 = "update config_data_extraction set last_start = STR_TO_DATE('{}', '%Y%m%d %H:%i:%s'), last_end = STR_TO_DATE('{}', '%Y%m%d %H:%i:%s') where program = 'prowatch_data_increase_get'".format(new_start, new_end)
last_run.execute_idu_sql(sql4)

print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), "    ", u"Updated successfully!Last start time: {}, last end time:{}.".format(new_start, new_end), file=logfile)

logfile.close()
