import pandas as pd

filename = 'REQ change vs Inventory change 0826.xlsx'

# read stock info
df_stock = pd.read_excel(filename, sheet_name = '0826库存')
df_stock = df_stock.fillna(0)
list_partno_stock = list(df_stock.iloc[:,0])

# change stock mapping to dict: partno -> start_stock
rows1, columns1 = df_stock.shape
dict_stock = {}
for i in range(rows1):
    dict_stock[df_stock.iloc[i,0]] = df_stock.iloc[i,2]

# read requirement
df_requirement = pd.read_excel(filename, sheet_name = '0826需求')
df_requirement = df_requirement.fillna(0)
list_partno_requirement = list(df_requirement.iloc[:,0])

# 将需求dataframe转成字典类型，用partno作为键，键值用需求数量构成的列表
rows2, columns2 = df_requirement.shape
dict_requirement = {}
for i in range(rows2):  #最后两行是blank和total，略去不取
    dict_requirement[df_requirement.iloc[i, 0]] = list(df_requirement.iloc[i, 1:columns2])    #最后两列是blank和total，略去不取

# read delivery
df_delivery = pd.read_excel(filename, sheet_name = '0826版到货情况')
df_delivery = df_delivery.fillna(0)
list_partno_delivery = list(df_delivery.iloc[:,0])

row3, columns3 = df_delivery.shape
dict_delivery = {}
for i in range(row3):
    dict_delivery[df_delivery.iloc[i, 0]] = list(df_delivery.iloc[i, 1:columns3])

title_columns = list(df_requirement.columns)
title_columns.pop(0)
title_columns = ['Partno', 'Start Stock'] + [i+'D7 Stock' for i in title_columns]

# collect all partnos
list_partno_temp = list_partno_stock + list_partno_requirement + list_partno_delivery
list_partno = list(set(list_partno_temp))
list_partno.sort()

data_initial = [[0]*len(title_columns)]*len(list_partno)    #initial MxN matrix
df_out = pd.DataFrame(data_initial)
df_out.columns = title_columns

# fill partno and start_stock one by one
for i in range(len(list_partno)):
    df_out.iloc[i, 0] = list_partno[i]
    try:
        df_out.iloc[i, 1] = dict_stock[list_partno[i]]
    except KeyError:
        df_out.iloc[i, 1] = 0

# start to calculate D7 remaining stock one by one
for j in range(len(title_columns)-2):
    for i in range(len(list_partno)):
        try:
            df_out.iloc[i, j+2] = df_out.iloc[i, j+1] + dict_delivery[df_out.iloc[i, 0]][j]
        except KeyError:
            df_out.iloc[i, j+2] = df_out.iloc[i, j+1]

        try:
            df_out.iloc[i, j+2] = df_out.iloc[i, j+2] - dict_requirement[df_out.iloc[i, 0]][j]
        except KeyError:
            pass

        if df_out.iloc[i, j+2] < 0:
            df_out.iloc[i, j+2] = 0

filename_new = filename.replace('.xlsx', '') + '_calculated.xlsx'
writer = pd.ExcelWriter(filename_new)
df_out.to_excel(writer, index=False)
writer.save()

