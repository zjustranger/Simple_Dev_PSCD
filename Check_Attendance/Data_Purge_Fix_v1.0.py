import pandas as pd
import numpy as np
import os
import datetime
# import pymysql
from sqlalchemy import create_engine
from time import sleep
'''
===========Exit Code Defination===========
0: 正常运行结束
4: 没有找到符合的csv文件
1: 打开csv文件时遇到异常
2: 保存结果excel文件时遇到异常
5: 存储详情数据到数据库时遇到异常
6: 存储汇总数据到数据库时遇到异常
'''

csv_dir = r'\\chepsvw3004.che.volvocars.net\attendance_raw_csv_file'
list_file = os.listdir(csv_dir)
logfile = open("running.log", "a")
searching_string = 'volvo' + datetime.datetime.now().strftime('%Y-%m-%d')  # 构造文件名搜索字符串，默认形式为volvo+当前日期
for i in list_file[:]:
    if not i.startswith(searching_string):
        list_file.remove(i)

# 判断是否有符合的文本
if list_file == []:
    print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), "    ", u"Cannot find today's csv file!", file=logfile)
    exit(4)

# 获取所有当天的考勤原始csv的最近修改时间，选最新的那个（避免它发多个报表过来）
time_list = [datetime.datetime.fromtimestamp(os.path.getmtime(csv_dir + '\\' + i)) for i in list_file]

# 绑定文件名和最近修改时间，按倒序排序，找出最新的文件名
zipped = zip(time_list, list_file)
sort_zipped = sorted(zipped, key=lambda x: (x[0], x[1]), reverse=True)
result = zip(*sort_zipped)
sorted_time_list, sorted_file_list = [list(x) for x in result]
final_csv_file = sorted_file_list[0]
# final_csv_file = ''
print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), "    ", u"Find today's newest csv file:", final_csv_file,
      file=logfile)

# ==================格式化输入参数=================
filename = csv_dir + '\\' + final_csv_file  # 读取远程文件名
headline = 1  # ”excel原文件里的标题行行数“
headline = headline - 1
output_header = ['Timestamp', 'Event', 'CDSID', 'Department', 'Card Number', 'Logical Device', 'Last Name',
                 'First Name']  # 输出结果的标题行
read_columns = ['事件记录时间', '事件类型', 'CDSID', '人员部门', '人员卡号', '设备位置', '人员工号',
                '人员姓名']  # 原文件中的行对应到上面输出文件的行列表，一一对应，讲究顺序
# 构造可配置的字符串对，用于替换原始数据里的拼写错误，以及部门的合并显示,从replace.xlsx文件里读取
replace_departments = pd.read_excel("replace.xlsx", sheet_name = "replace_department").values    # 合并多个部门为某一个部门显示&修改部门名称, just as below
# replace_departments = np.array([
#     ['LEGAL', 'PR/PU/LEGAL'],
#     ['PURCHASING', 'PR/PU/LEGAL'],
#     ['CC', 'PR/PU/LEGAL'],
#     ['GMO', 'GMO/OD'],
#     ['OD', 'GMO/OD'],
#     ['PROJECT', 'PROJ/ME'],
#     ['ME', 'PROJ/ME']
# ])  # 合并多个部门为某一个部门显示&修改部门名称
replace_2 = pd.read_excel("replace.xlsx", sheet_name = "replace_stringpairs").values  # 修改拼写错误&修改部门名称
add_line = ['\n', '']
replace_stringpairs = np.insert(replace_2, 0, add_line, axis = 0)
# replace_stringpairs = np.array([
#     ['\n', ''],
#     ['FNANCE', 'FINANCE'],
#     ['PAINTING', 'PAINT']
# ])  # 修改拼写错误&修改部门名称


try:
    df = pd.read_csv(filename, header=headline, encoding='GBK')  # 读取原文件
except Exception as e:
    print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), "    ", u"Error in opening csv file:", "Error type is",
          type(e), ",Error code is", e, file=logfile)
    exit(1)
else:
    print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), "    ", u"Reading csv file successfully!", file=logfile)

# 选取原文件里需要处理的列
df = df.reindex(read_columns, axis=1)
data_raw = df.values

# 删除出门的记录
data1 = data_raw
del_row = []

# 第6列为Logical Device，通过最后是in还是out判断，把出门的记录删掉
for i in range(len(data1)):
    if data1[i, 5].endswith('out'):
        del_row.append(i)

data2 = np.delete(data1, del_row, 0)

# 按照时间排序，时间位于第一列
data3 = data2[data2[:, 0].argsort()]

# 去重，把重复的Card Number去掉，等于只保留第一次进入的记录，Card位于第5列
del_row2 = []
for i in range(len(data3)):
    if list(data3[0:i + 1, 4]).count(data3[i, 4]) != 1:
        del_row2.append(i)
data4 = np.delete(data3, del_row2, 0)

# 整理数据，先把所有字符串转成大写，再按照替换的字符对把拼写错误的依次处理
data5 = data4
for i in range(len(data5)):
    for j in range(len(data5[0, :])):
        if isinstance(data5[i, j], str):
            data5[i, j] = data5[i, j].upper()
            for k in replace_stringpairs:
                data5[i, j] = data5[i, j].replace(k[0], k[1])

# 导出结果，df_out是详细记录，df_out2是统计数据
df_out = pd.DataFrame(data5, columns=output_header)

# 按照合并部门的配置，合并并统计人数
df_temp = df_out['Department'].value_counts()
list1 = list(df_temp.index)
list2 = list(df_temp.values)
df2 = pd.DataFrame(np.array([list1, list2]).T, columns=['Department', 'Count'])  # 原始部门统计结果
value2 = df2.values
# 按照合并部门的配置，合并并统计人数
for i in range(len(value2)):
    for j in replace_departments:
        if value2[i, 0] == j[0]:
            value2[i, 0] = j[1]
# 替换完成后，重新构造DataFrame，对部门进行统计
df3 = pd.DataFrame(value2, columns=['Department', 'Count'])
df3['Count'] = df3['Count'].apply(pd.to_numeric)
df4 = df3.groupby('Department').sum()
list3 = list(df4.index)
list4 = list(df4.values[:, 0])
df5 = pd.DataFrame(np.array([list3, list4]).T, columns=['Department', 'Count'])
df5['Count'] = df5['Count'].apply(pd.to_numeric)
df_out2 = df5.sort_values(by='Count', ascending=False)


# 把统计的详情和汇总结果写入excel
writer = pd.ExcelWriter(csv_dir + "\\" + 'Attendance_Today.xlsx')
df_out.to_excel(writer, sheet_name="Detail Information", index=False)
df_out2.to_excel(writer, sheet_name="Statistics", index=False)
try:
    writer.save()
except Exception as e:
    print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), "    ", u"Error in saving csv file:", "Error type is",
          type(e), ",Error code is", e, file=logfile)
    exit(2)
else:
    print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), "    ", u"successfully saving result attendance excel file.", file=logfile)


# 把统计的详情和汇总结果写入mysql数据库
connect = create_engine('mysql+pymysql://root:Admin_polestar1@10.234.9.200:3306/RPT')
# 写入详情信息，写入前需要先把DataFrame的列名按照数据库表的列名进行修改
df_out.columns = ['Timestamp', 'Event','CDSID','Department','CardNo','LogiDev','LNAME','FNAME']
try:
    df_out.to_sql(name = 'attendance_daily_detail', con = connect, if_exists = 'append', index = False)
except Exception as e:
    print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), "    ", u"Error in saving detail info into database table: attend_daily_detail", "Error type is",
          type(e), ",Error code is", e, file=logfile)
    exit(5)
else:
    print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), "    ", u"Successfully insert detail information into database table!", file=logfile)
# 写入汇总结果，写入前需要先添加一列attend_date，把当前的日期以YYYYMMDD字符形式写入列中
df_out2 = df_out2.reindex(['Department','Count','Attend_date'], axis = 1)
df_out2['Attend_date'] = datetime.datetime.now().strftime('%Y%m%d')
try:
    df_out2.to_sql(name = 'attendance_daily_sum', con = connect, if_exists = 'append', index = False)
except Exception as e:
    print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), "    ", u"Error in saving detail info into database table: attend_daily_sum", "Error type is",
          type(e), ",Error code is", e, file=logfile)
    exit(6)
else:
    print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), "    ", u"Successfully insert summary information into database table!", file=logfile)



# 关闭log文件，结束程序
print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++", file = logfile)
logfile.close()
sleep(2)
pass
