import pandas as pd
import os
import datetime
from time import sleep
# import openpyxl
# import numpy as np

# 目前不用挂载盘了，直接用远程目录来确定输入数据和输出数据访问的公盘位置 # 挂载物流的公盘为本地K盘，用于后续的数据处理
remote_dir = r'\\chesnm0201.che.volvocars.net\PROJ2\6765-SHR-VCC08200\Production Plan & Order\Production Plan'
remote_output_dir = r'\\chesnm0201.che.volvocars.net\PROJ2\6765-SHR-VCC08800\66.Local Report'
# os.system('subst K: "'+remote_dir+'"')
# os.chdir('K:\\')
# os.system('dir')

list_file = os.listdir(remote_dir)
# 删除不是以‘P514 Production plan’开头的文件
for i in list_file[:]:
    if not i.startswith('P514 Production Plan'):
        list_file.remove(i)

# 获取所有生产报表的最近修改时间
time_list = [datetime.datetime.fromtimestamp(os.path.getmtime(remote_dir+'\\'+i)) for i in list_file]

# 绑定文件名和最近修改时间，按倒序排序，找出最新的文件名
zipped = zip(time_list, list_file)
sort_zipped = sorted(zipped, key=lambda x:(x[0],x[1]), reverse=True)
result = zip(*sort_zipped)
sorted_time_list, sorted_file_list = [list(x) for x in result]
newestproductionplan = sorted_file_list[0]

logfile = open("purge.log","a")
print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), "    ", u"Get the latest original production plan file:", sorted_file_list[0], u", last modified:", sorted_time_list[0], file = logfile)
print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), "    ", u"Now purging the production plan raw data and processing...", file = logfile)


# 构造需要访问的物流生产计划文件位置，以及输出处理后的文件所在位置
def_file = remote_dir + '\\' + newestproductionplan
# def_file = 'C:\\files backup\\daily files\\tech documents\\Self-Dev\\purge_prod_plan\\P514 Production plan.xlsx'
def_outfile = remote_output_dir + '\\' + 'newplan.xlsx'     # 新文件命名为newplan.xlsx
# def_outfile = 'C:\\files backup\\daily files\\tech documents\\Self-Dev\\purge_prod_plan\\1.xlsx'
df1 = pd.read_excel(def_file)    # get all raw data from excel
data1 = df1.values    # transfer dataframe to array

'''
===============================================================================================================
原数据中，A shop under body on line PGM位于第4行，B shop mix PGM位于第18行，TCF pretrim on line PGM位于第20行；
需要取的标题列为第1列，2020年01月01日至2020年12月31日位于第4列至第369列；
下面开始构造取数的行列。并将需要的数据取到data2变量中
-- changed on 06/18, using column names to find the rows to be fetched... Due to Jessie may change the format unceremoniously
'''
rawcolnames = list(df1.iloc[:,1])
col1 = rawcolnames.index('Under body on line PGM')
col2 = rawcolnames.index('B Shop Mix   PGM')
col3 = rawcolnames.index('TCF Pre trim On line PGM')

row_mask = [col1,col2,col3]
col_mask = list(range(4,373))+list(range(374,736))
col_mask = [1]+col_mask

data2 = data1[row_mask][:,col_mask]

# 给数据补上标题行，标题行第一列为Category，从第二列开始为连续的日期，从2020/01/01到2021/12/31
def get_date_list(begin_date, end_date):
    date_list = [x.strftime('%Y/%m/%d') for x in list(pd.date_range(start = begin_date, end = end_date))]
    return date_list

title = get_date_list('2020/01/01','2021/12/31')
title = ['Category'] + title

# 标题行和数据拼起来
temp = data2.tolist()
temp.insert(0, title)

# 输出到excel里
df2 = pd.DataFrame(temp)
print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), "    ", u"Finish processing, now exporting...", file = logfile)
df2.to_excel(def_outfile,encoding='utf-8',header=False,index=False)
print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), "    ", u"Exported to the share disks.", file = logfile)
print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++", file = logfile)

logfile.close()
sleep(1)
# os.system('pause')
# # 取消挂载K盘
# os.system('subst K: /D')