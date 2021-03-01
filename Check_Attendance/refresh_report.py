import pymysql
import pandas as pd
from pyecharts import Bar

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

# 将数据转为DataFrame，统计分析汇总后写入excel
rslt_df_detail = pd.DataFrame(rslt_data)
rslt_df_detail.columns = ['卡号','进厂时间','进厂位置','姓','名','公司','部门']


sql_ana_summary = '''
select company, department, count(1) as number from
(select lg.card_no, lg.last_grant_time, tp.logical_device, tp.lname, tp.fname, tp.company, tp.department from
(select card_no, max(event_time) last_grant_time from prowatch_data
where logical_device like 'PSCD%Gate%' and event_time > date_sub(CURRENT_TIMESTAMP(), interval '3 00:00:00' day_second) and status = 'Active'
group by card_no) lg left join prowatch_data tp on (lg.card_no = tp.card_no and lg.last_grant_time = tp.event_time) where lower(tp.logical_device) like '%in') rslt
group by company, department order by company, department
'''
rslt_data = ana_conn.execute_sql(sql_ana_summary)
rslt_df_summary = pd.DataFrame(rslt_data)
rslt_df_summary.columns = ['公司','部门','在厂人数']


# 数据写入Excel表格
writer = pd.ExcelWriter('new_data.xlsx')
rslt_df_detail.to_excel(writer, sheet_name="Detail Information", index=False)
rslt_df_summary.to_excel(writer, sheet_name="Summary", index=False)
writer.save()


# Draw echarts
# df_draw = rslt_df_summary[rslt_df_summary['公司']=='pscd']
# df_draw2 = rslt_df_summary[rslt_df_summary['公司']=='PSCD Supplie']
#
# df_draw = df_draw.fillna('Blank')
# df_draw2 = df_draw2.fillna('Blank')
list_company = list(set(rslt_df_summary.iloc[:,0]))
list_company.sort()
list_department = list(set(rslt_df_summary.iloc[:,1]))
list_department.sort()
data = [[] for i in range(len(list_company))]

for department in list_department:
    for i, company in enumerate(list_company):
        try:
            data[i].append(rslt_df_summary[rslt_df_summary['公司']==company][rslt_df_summary['部门']==department].iloc[0,2])
        except IndexError:
            data[i].append(0)

# l = lambda x: '\n'.join(x)
# list_department = [l(i) for i in list_department]

last_refresh_time = ana_conn.execute_sql("select last_end FROM config_data_extraction where program = 'prowatch_data_increase_get'")
last_refresh_time = last_refresh_time[0][0]
subtitle = 'Last Refresh: {}. The total qty for each company is:'.format(last_refresh_time.strftime('%Y-%m-%d %H:%M:%S'))
for i, company in enumerate(list_company):
    subtitle += '   {}:{}'.format(company, sum(data[i]))

bar = Bar('PSCD厂内人员分析实时图 总人数: {}'.format(rslt_df_summary['在厂人数'].sum()), subtitle,
          width=1400, height = 1400, subtitle_color='#666', title_text_size=22, subtitle_text_size=14)
for i, company in enumerate(list_company):
    bar.add(company, list_department, data[i], is_stack=True, is_convert=True)

bar.render(r'\\chesnc0803.che.volvocars.net\PROJ2\6765-SHR-VCC08800\66.Local Report\real_people.html')
