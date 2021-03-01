import pandas as pd
import datetime
from sqlalchemy import create_engine


# 标定需要读取的文件名和sheet名
logfile = open("running.log", "a")
print('*'*100, file=logfile)
file_dir = r'\\chesnc0803.che.volvocars.net\PROJ2\6765-SHR-VCC08700\16 Energy Consumption Data'
read_filename = file_dir + '\\' + '洁净室和化学品库温湿度记录.xlsx'
# sheetname_today = datetime.datetime.now().strftime('%Y%m%d')    #sheetname为当天的时间yyyymmdd，用这行
sheetname_today = (datetime.datetime.now()+datetime.timedelta(days=-1)).strftime('%Y%m%d')    #sheetname为前一天，用这行
# sheetname_today = '20200921'    #补数据，手动修改，用这行
headline = 27
headline = headline - 1


try:
    df = pd.read_excel(read_filename, sheet_name=sheetname_today, header = headline)
    row_max, col_max = df.shape
except:
    print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), "    ", "Cannot find today's sheet name!", file=logfile)
    exit(1)
else:
    print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), "    ", "Finding today's sheet name:{}".format(sheetname_today), file=logfile)

# 防错，找到第一个记录仪记录的数据开始的列数，不采用固定值
start_col = 0
while start_col < col_max:
    if df.iloc[0, start_col] == '温度':
        break
    start_col += 1

if start_col == col_max:
    print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), "    ", "data or format abnormal, cannot find start cell.", file=logfile)
    exit(2)

# 根据开始的列，构造抓数的mask
col_mask_a = [i+start_col for i in [0,1,2]]
col_mask_b = [i+start_col for i in [4,5,6]]
col_mask_c = [i+start_col for i in [8,9,10]]
col_mask_d = [i+start_col for i in [12,13,14]]

if max(col_mask_d) > col_max:
    print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), "    ", "data not complete or format abnormal", file=logfile)
    exit(3)


# 开始创建并写进数据库
connect = create_engine('mysql+pymysql://root:Admin_polestar1@10.234.9.200:3306/RPT')

start_row = 1

try:
    df_a = df.iloc[start_row:, col_mask_a]
    df_a = df_a.dropna(axis=0)
    df_a['device_name'] = 'TH_Sensor_A'
    df_a.columns = ['temperature', 'humidity', 'record_time', 'device_name']
    df_a.to_sql(name = 'th_record', con = connect, if_exists = 'append', index = False)
except:
    print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), "    ", "Sensor A data writing failed!", file=logfile)
else:
    print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), "    ", "Sensor A data writing successfully!", file=logfile)

try:
    df_b = df.iloc[start_row:, col_mask_b]
    df_b = df_b.dropna(axis=0)
    df_b['device_name'] = 'TH_Sensor_B'
    df_b.columns = ['temperature', 'humidity', 'record_time', 'device_name']
    df_b.to_sql(name='th_record', con=connect, if_exists='append', index=False)
except:
    print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), "    ", "Sensor B data writing failed!", file=logfile)
else:
    print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), "    ", "Sensor B data writing successfully!", file=logfile)

try:
    df_c = df.iloc[start_row:, col_mask_c]
    df_c = df_c.dropna(axis=0)
    df_c['device_name'] = 'TH_Sensor_C'
    df_c.columns = ['temperature', 'humidity', 'record_time', 'device_name']
    df_c.to_sql(name='th_record', con=connect, if_exists='append', index=False)
except:
    print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), "    ", "Sensor C data writing failed!", file=logfile)
else:
    print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), "    ", "Sensor C data writing successfully!", file=logfile)

try:
    df_d = df.iloc[start_row:, col_mask_d]
    df_d = df_d.dropna(axis=0)
    df_d['device_name'] = 'TH_Sensor_D'
    df_d.columns = ['temperature', 'humidity', 'record_time', 'device_name']
    df_d.to_sql(name='th_record', con=connect, if_exists='append', index=False)
except:
    print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), "    ", "Sensor D data writing failed!", file=logfile)
else:
    print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), "    ", "Sensor D data writing successfully!", file=logfile)

logfile.close()