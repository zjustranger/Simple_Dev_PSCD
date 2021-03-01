import os
import datetime
from DB_Connection import run_select_sql
from DB_Connection import run_iud_sql
from EMAIL import Email
import pandas as pd
from time import sleep

output_temp_dir = os.getcwd() + r'\temp\tempdata' + '\\'


class Job_instance:
    def __init__(self, logfile, job_name, sql_run=None, email_title=None, email_content=None, last_start=None,
                 excel_columns=None):
        self.job_name = job_name
        self.sql_run = sql_run
        self.email_title = email_title
        self.email_content = email_content
        self.last_start = last_start
        self.excel_columns = excel_columns

    def show(self):
        print('*' * 100, file=logfile)
        print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), "    ",
              'A Job: {} was called this time! Previous run time is {}.'.format(self.job_name, self.last_start),
              file=logfile)

    def run(self):
        sql1 = "update job_config set is_running = 'Y' where job_name = '{}'".format(self.job_name)
        run_iud_sql(sql1)
        print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), "    ",
              'Step1. Set the job: {} status to running, prevent duplicated running job.'.format(self.job_name),
              file=logfile)
        rs = run_select_sql("select job_seq.nextval from dual")
        job_seq = rs[0][0]
        sql2 = "insert into job_logs (job_id, job_name, start_time, active) values ('{}', '{}', sysdate, 'Y')".format(
            job_seq, self.job_name)
        run_iud_sql(sql2)
        print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), "    ",
              'Insert records into job_logs table successfully.', file=logfile)
        # get data
        rs1 = run_select_sql(self.sql_run)
        try:
            df = pd.DataFrame(rs1)
            df.columns = self.excel_columns.split(',')
            file_name = 'Job' + self.job_name + '_' + datetime.datetime.now().strftime('%Y%m%d%H%M%S') + '.xlsx'
            output_file_name = output_temp_dir + file_name
            writer = pd.ExcelWriter(output_file_name)
            df.to_excel(writer, index=False)
            writer.save()
            print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), "    ",
                  'Step2. Get the data for job: {} successfully and generate excel file successfully.'.format(
                      self.job_name),
                  file=logfile)
            # try to get email receiver list and send email.
            sql_email = "select receiver from job_emails where job_name = '{}' and active = 'Y'".format(self.job_name)
            rs2 = run_select_sql(sql_email)
            receivers = ';'.join([i[0] for i in rs2])
            email_instance = Email(self.email_title, self.email_content, receivers, output_file_name, file_name)
            email_instance.send_mail()
        except:
            pass
        sql3 = "update job_logs set finish_time = sysdate, active = 'N' where job_id = '{}'".format(job_seq)
        run_iud_sql(sql3)
        sql4 = "update job_config set is_running = 'N' where job_name = '{}'".format(self.job_name)
        run_iud_sql(sql4)
        print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), "    ",
              'Step4. Set the job: {} status to finished, waiting for next running.'.format(self.job_name),
              file=logfile)


while datetime.datetime.now().strftime('%H:%M:%S') < '16:30:00':
    try:
        logfile = open("job_scheduler.log", "a")

        '''
        First step, get the job details that should be run.
        the sql combined 2 conditions: 
        1. find the job list with conditions: active status: Y & not in running status & has past its start time today
        2. find the last running records for this job. if now - last run time > job interval setting, then should call a new job.
        '''

        sql_to_get_jobs = '''
    select jc.job_name, jc.sql_run, jc.EMAIL_TITLE, jc.email_content, jl.last_start, jc.report_column_names from job_config jc left join (select job_name, max(start_time) last_start from job_logs where start_time > trunc(sysdate) group by job_name) jl 
    on (jc.JOB_NAME = jl.JOB_NAME) where jc.start_time < to_char(sysdate, 'HH24:MI:SS') and jc.IS_RUNNING = 'N' and jc.active = 'Y' and ((sysdate - jl.last_start)*24*60 > jc.JOB_INTERVAL_MINUTES or jl.last_start is NULL)
        '''

        rs = run_select_sql(sql_to_get_jobs)

        if rs:
            for job in rs:
                run_job = Job_instance(logfile, job[0], job[1], job[2], job[3], job[4], job[5])
                run_job.show()
                run_job.run()
        else:
            print('*' * 100, file=logfile)
            print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), "    ", 'No jobs should be called.', file=logfile)

        logfile.close()
        print("finished at", datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        sleep(60)
    except Exception as e:
        print("have exception at", datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), type(e), e)
        sleep(300)

