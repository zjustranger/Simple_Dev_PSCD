import pymssql
import pandas as pd
from sqlalchemy import create_engine
import datetime
import sqlite3
from common_fuctions import load_config
from EMAIL import Email

class Sqlite_Analysis:
    def __init__(self, filename = 'ARCHIVE.DB'):
        self.conn = sqlite3.connect(filename)
        self.cursor = self.conn.cursor()

    def execute_select_sql(self, sql_str):
        self.cursor.execute(sql_str)
        rows = self.cursor.fetchall()
        return rows

    def execute_idu_sql(self, sql_str):
        try:
            self.cursor.execute(sql_str)
            self.conn.commit()
        except:
            self.conn.rollback()

    def __del__(self):
        self.cursor.close()
        self.conn.close()

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

class DF_to_Sqlite_DB:
    def __init__(self, df):
        self.connect = create_engine('sqlite:///ARCHIVE.DB')
        self.df = pd.DataFrame(df)

    def add_column_name(self, columns):
        self.df.columns = columns

    def send_to_sqlite(self, table_name, if_exists='append'):
        self.df.to_sql(name=table_name, con=self.connect, if_exists=if_exists, index=False)


if __name__ == '__main__':


    try:
        # step0. 准备工作
        logfile = open("running.log", "a")
        print('*' * 100, file=logfile)
        conf_dict = load_config()
        if conf_dict['Fix_Data']:
            fix_data = True
        else:
            fix_data = False
        mapping_file = conf_dict['Mapping_Filename']
        output_csv_file = conf_dict['Output_Excel']
        email_receiver = conf_dict['Email_Receiver']

        # step1. 从sqlite取出上次程序的执行时间，如果是fix数据，则直接取配置的日期
        if fix_data:
            print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), "    ",
                  u"Step 1. Finding parameter to get special data...", file=logfile)
            new_start = conf_dict['Fix_Datetime_From']
            new_end = conf_dict['Fix_Datetime_To']
            print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), "    ",
                  u"Time range for data extraction this time has been defined: new_start:{}, new_end:{}".format(new_start,
                                                                                                                new_end),
                  file=logfile)
        else:
            print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), "    ",
                  u"Step 1. Getting the last running time from control table...", file=logfile)

            last_run = Sqlite_Analysis()
            sql1 = "select last_end, last_start from config_data_extraction where program = 'HR_AUTO'"
            rslt = last_run.execute_select_sql(sql1)
            last_end, last_start = rslt[0]

            print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), "    ",
                  u"Get last running parameter successfully: last start:{}, last end:{}.".format(last_start, last_end),
                  file=logfile)

            # 确定这次抓数的时间范围
            if last_end:
                new_start = last_end
            elif last_start:
                new_start = last_start
            else:
                exit(2)

            new_end = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), "    ",
                  u"Time range for data extraction this time has been defined: new_start:{}, new_end:{}".format(new_start,
                                                                                                                new_end),
                  file=logfile)

            # 将数据库表里比这次抓数开始时间晚的数据全部清掉，避免出现重复数据
            print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), "    ",
                  u"Deleting the data in table later than new start time, to prevent duplicated data...", file=logfile)

            sql2 = "delete from attendance_records where event_time >= DATETIME('{}')".format(new_start)
            last_run.execute_idu_sql(sql2)

            print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), "    ", u"Delete finished.", file=logfile)

        # step2. 从Prowatch数据库里取这部分数据
        sql3 = '''
        select ft_evnt_dat, fc_logdevdescrp, fc_evnt_descrp, FC_LOCATION, FC_CARDNO, FC_LNAME, FC_FNAME, FC_COMP_NAME, FC_DEPARTMENT, FC_STAT_COD, FC_CDSID, FC_EMPLOYEENUMBER from ACSYSTEMPWEVENT
        where FT_EVNT_DAT between convert(datetime, '{}', 101) and convert(datetime, '{}', 101) and upper(FC_LOGDEVDESCRP) like '%PSCD%ATTEND%' order by FT_EVNT_DAT
        '''.format(new_start, new_end)

        # 连接Prowatch数据库，取数据
        print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), "    ",
              u"Step2. Connecting Prowatch database and getting data...", file=logfile)

        pro_conn = Prowatch_DBConnection()
        transfer_data = pro_conn.execute_sql(sql3)

        print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), "    ", u"Getting data successfully!", file=logfile)

        # step3. 将增量数据写入到sqlite数据库中，如果是修复数据，则替换临时表temp_data的数据
        try:
            rpt_conn = DF_to_Sqlite_DB(transfer_data)
            rpt_conn.add_column_name(
                ['event_time', 'logical_device', 'event_descr', 'location', 'card_no', 'lname', 'fname', 'company',
                 'department', 'status', 'cdsid', 'employee_no'])

            print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), "    ",
                  u"Step3. Connecting Sqlite DB and insert data into table...", file=logfile)

            if fix_data:
                rpt_conn.send_to_sqlite('temp_data', 'replace')
            else:
                rpt_conn.send_to_sqlite('attendance_records')
                rpt_conn.send_to_sqlite('temp_data', 'replace')

            print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), "    ", u"Inserted successfully.", file=logfile)
        except ValueError:
            print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), "    ",
                  u"Step3. No data found in this time period, skip to insert into sqlite DB.", file=logfile)

        # step4. 读取卡号信息和workday_id的匹配关系到数据库，用于整理生成csv file的数据
        mapping_conn = DF_to_Sqlite_DB(pd.read_excel(mapping_file))
        mapping_conn.send_to_sqlite('id_mapping', 'replace')
        print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), "    ",
              u"Step4. Read card number and workday id mapping relationship successfully. now prepare to generate output excel", file=logfile)

        # 准备抓取数据
        ana_sql = """
        select rslt1.attend_time, rslt1.logical_device, id_mapping.workday_id, rslt1.check_type, rslt1.lname, rslt1.fname, rslt1.cdsid, rslt1.department, rslt1.card_no, rslt1.company, rslt1.employee_no from
        (select datetime(event_time) as attend_time, logical_device, case when lower(logical_device) like '%in' then 'IN' when lower(logical_device) like '%out' then 'OUT' else '' end as check_type, lname, fname, cdsid, department,  card_no, company, employee_no
        from temp_data
        where lower(company) = 'pscd' and event_time BETWEEN datetime('{}') and datetime('{}')) rslt1
        left join id_mapping on (rslt1.card_no = id_mapping.card_no)
        order by attend_time
        """.format(new_start, new_end)

        exp_run = Sqlite_Analysis()
        exp_data = exp_run.execute_select_sql(ana_sql)
        exp_df = pd.DataFrame(exp_data)
        exp_df = exp_df.replace('\n','',regex=True).replace('\r','',regex=True)
        try:
            exp_df.columns = ['attend_time','logical_device','workday_id','check_type','lname','fname','cdsid','department','card_no','company','employee_no']
            num_rows = exp_df.shape[0]
        except ValueError:
            exp_df = pd.DataFrame([['']*11,])
            exp_df.columns = ['attend_time','logical_device','workday_id','check_type','lname','fname','cdsid','department','card_no','company','employee_no']
            num_rows = 0
        exp_df.to_csv(output_csv_file, index=False)

        print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), "    ",
              u"Generate file successfully! This run {} lines are generated.".format(num_rows),
              file=logfile)


        # step5. 更新控制表里的数值，将最后一次执行时间抓数范围更新进去。如果是修复数据则调过这步
        if fix_data:
            print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), "    ",
                  u"Step5. Fix data, no need to update the control table. skip this step.",
                  file=logfile)
        else:
            print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), "    ",
                  u"Step5. Updating the control table, refresh the last start time and last end time for this job...",
                  file=logfile)

            sql5 = "update config_data_extraction set last_start = DATETIME('{}'), last_end = DATETIME('{}') where program = 'HR_AUTO'".format(
                new_start, new_end)
            last_run.execute_idu_sql(sql5)

            print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), "    ",
                  u"Updated successfully!Last start time: {}, last end time:{}.".format(new_start, new_end), file=logfile)

        email_content = 'HR Attendance Generated Successfully!\nThis run send attendace check data between {} and {}, {} lines in total.'.format(new_start, new_end, num_rows)
        sender = Email('HR Attendance Generated Successfully!', email_content, email_receiver, output_csv_file, 'DEMO.csv')
        sender.send_mail()
        print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), "    ",
              u"Email sent successfully!",
              file=logfile)

        logfile.close()
    except:
        email_content = 'ERROR! HR Attendance Generated Failed!\nPlease Check the program.'
        sender = Email('ERROR! HR Attendance Generated Failed!', email_content, email_receiver)
        sender.send_mail()


