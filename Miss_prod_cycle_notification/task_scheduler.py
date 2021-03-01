import os
import datetime
import pandas as pd
from EMAIL import Email
import cx_Oracle as cx

class DB_Connetion_CIP:
    def __init__(self):
        self.tns = cx.makedsn('npc.che.volvocars.net', 49957, sid='DPQ')
        self.db = cx.connect('cip_sys', 'cip_sys1', self.tns, encoding="UTF-8", nencoding="UTF-8")
        self.cur = self.db.cursor()
    def select(self, sql):
        self.cur.execute(sql)
        self.rs = self.cur.fetchall()
        return self.rs
    def __del__(self):
        self.cur.close()
        self.db.close()

class Threshold_Checker:
    def __init__(self, rg1, desc1, rg2, desc2, threshold, recipients):
        self.rg1 = rg1
        self.desc1 = desc1
        self.rg2 = rg2
        self.desc2 = desc2
        self.threshold = threshold
        self.recipients = recipients
    def get_details_from_DB(self):
        # 筛选出这两个注册点已经提示过的车辆
        sa = open('send_already.log')
        tmp = sa.read()
        tmp1 = tmp.split('\n')
        tmp2 = [i.split(',') for i in tmp1]
        self.car_already_sent = [i[2] for i in tmp2 if i[0] == str(self.rg1) and i[1] == str(self.rg2)]   #列表形式列出的对于这两个注册点已经提醒过的车辆
        # 组装成sql语句需要的字符串, 为了避免空字符串导致搜不出数据，添加一个不存在的body号0800000
        tmp3 = "'"+"','".join(self.car_already_sent)+"'"
        if tmp3 == "''":
            tmp3 = "'0800000'"
        sql_common = '''
        with reg_history as
        (select t5.ibody, t5.tagid , t2.ivmix, t0.iincd, t6.dbreg from tcp716 t6 left join tcp010 t0 on (t6.NIDTCP010 = t0.nidtcp010) left join tcp715 t5 on (t6.NIDTCP715 = t5.NIDTCP715) left join tcp712 t2 on (t5.IBODY = t2.ibody)
        where t0.iincd in ('{rg1}', '{rg2}') and t5.ibody > '1000000')
        select ibody, tagid, ivmix, dbreg from reg_history rh1 
        where iincd = '{rg1}' and dbreg < sysdate - {minutes}/1440 and ibody not in ({car})
        and not exists (select 1 from reg_history rh2 where rh1.ibody = rh2.ibody and rh2.iincd = '{rg2}')
        and dbreg = (select max(dbreg) from reg_history where ibody = rh1.ibody) order by ibody
        '''
        sql = sql_common.format(rg1=self.rg1,rg2=self.rg2,minutes=self.threshold,car=tmp3)
        # 连接数据库取数
        self.db = DB_Connetion_CIP()
        self.rs = self.db.select(sql)
    def logging_and_email(self):
        if self.rs != [] and str(self.recipients) != 'nan':
            add_log = ''
            email_content_main = ''
            for item in self.rs:
                body_number = item[0]
                tagid = item[1]
                mix_number = item[2]
                last_reg_time = item[3].strftime('%Y/%m/%d %H:%M:%S')
                sys_timestamp = datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')
                add_log_line = '{},{},{},{}\n'.format(self.rg1, self.rg2, body_number, sys_timestamp)
                add_log += add_log_line
                email_content_line = 'Body Number:{}, RFID Tagid:{}, Mix Number:{} 已经在{}过注册点{}（{}），长时间未到注册点{}（{}）。\n'.format(body_number, tagid, mix_number, last_reg_time, self.rg1, self.desc1.strip(), self.rg2, self.desc2.strip())
                email_content_main += email_content_line
            # 添加已经提醒过的车的信息到log文件，避免下次再发提醒
            logfile = open('send_already.log', 'a')
            print(add_log, end='',file=logfile)
            logfile.close()
            # 发送邮件
            email_title = '【工艺超时提醒】请相关同事注意此信息，并及时采取应对措施'
            email_content = '根据PE设置的规则，系统检查到有如下异常，发送提醒一次。\n\n' + email_content_main + '\n请相关部门同事注意此信息，并及时采取应对措施。' + '\n\n\n\n******此邮件由系统自动发出，请勿直接回复此邮件******'
            # print(email_content)
            email = Email(email_title, email_content, self.recipients)
            email.send_mail()





if __name__ == '__main__':
    cfg = pd.read_excel('config_notification.xlsx')
    rows, cols = cfg.shape

    for i in range(rows):
        ck = Threshold_Checker(cfg.iloc[i,0],cfg.iloc[i,1],cfg.iloc[i,2],cfg.iloc[i,3],cfg.iloc[i,4],cfg.iloc[i,5])
        ck.get_details_from_DB()
        ck.logging_and_email()














