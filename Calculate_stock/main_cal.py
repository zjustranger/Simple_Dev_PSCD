import pandas as pd
import tkinter as tk
from tkinter import messagebox

w = tk.Tk()
w.geometry('520x60+400+300')
w.title("计算库存可用天数")
w.resizable(0, 0)

l1 = tk.Label(w, text = '原始Excel文件名：', font = ('微软雅黑', 12, 'bold')).place(x=0, y=0)
filename = tk.StringVar()
filename.set('example.xlsx')
e1 = tk.Entry(w, textvariable = filename, width = 30, font = ('微软雅黑', 12)).place(x=150, y=1)
l2 = tk.Label(w, text = '需求Sheet名：', font = ('微软雅黑', 12, 'bold')).place(x=0, y=30)
requirement_sheet = tk.StringVar()
requirement_sheet.set('Sheet1')
e2 = tk.Entry(w, textvariable = requirement_sheet, width = 10, font = ('微软雅黑', 12)).place(x=110, y=31)
l3 = tk.Label(w, text = '库存Sheet名：', font = ('微软雅黑', 12, 'bold')).place(x=220, y=30)
stock_sheet = tk.StringVar()
stock_sheet.set('Sheet2')
e3 = tk.Entry(w, textvariable = stock_sheet, width = 10, font = ('微软雅黑', 12)).place(x=330, y=31)

def click():
    # 导入需求数据
    try:
        df_requirement = pd.read_excel(filename.get(), sheet_name = requirement_sheet.get())
    except:
        tk.messagebox.showerror('Error', 'Exception happens when getting requirement data.')
    df_requirement = df_requirement.fillna(0)
    list_partno_requirement = list(df_requirement.iloc[:,0])

    # 将需求dataframe转成字典类型，用partno作为键，键值用需求数量构成的列表
    rows, columns = df_requirement.shape
    dict_requirement = {}
    for i in range(rows-2):  #最后两行是blank和total，略去不取
        dict_requirement[df_requirement.iloc[i, 0]] = list(df_requirement.iloc[i, 1:columns-3])    #最后两列是blank和total，略去不取

    # 导入库存数据
    try:
        df_stock = pd.read_excel(filename.get(), sheet_name = stock_sheet.get())
    except:
        tk.messagebox.showerror('Error', 'Exception happens when getting stock data.')
    df_stock = df_stock.fillna(0)
    list_partno_stock = list(df_stock.iloc[:,0])

    # 将库存数据转成字典类型，通过partno查询开始库存
    rows1, columns1 = df_stock.shape
    dict_stock = {}
    for i in range(rows1):
        dict_stock[df_stock.iloc[i,0]] = df_stock.iloc[i,1]

    # 将两边的零件号进行汇总并去重，形成结果的零件列表
    list_partno_temp = list_partno_stock + list_partno_requirement
    # remove duplicated partnos
    list_partno_temp = list(set(list_partno_temp))
    # remove the partno's that not equal to int
    list_partno = [i for i in list_partno_temp if isinstance(i, int)]

    def cal_available_days(partno):
        try:
            total_stock = dict_stock[partno]
        except KeyError:    # 没有找到可用库存，直接返回可用0天
            return 0
        try:
            requirement_list = dict_requirement[partno]    # 有库存，没有找到需求，直接返回需求清单里面的最大天数
        except KeyError:
            return columns-4
        available_days = 0
        while total_stock > 0 and available_days < columns-4:
            total_stock -= requirement_list[available_days]
            available_days += 1
        return available_days

    available_day_list = []
    for i in list_partno:
        available_day_list.append([i, cal_available_days(i)])

    output_df = pd.DataFrame(available_day_list, columns = ['partno', 'available_days'])
    filename_new = filename.get().replace('.xlsx', '') + '_calculated.xlsx'
    writer = pd.ExcelWriter(filename_new)
    output_df.to_excel(writer, index=False)
    writer.save()
    tk.messagebox.showinfo('Success', 'Generate excel file: {} successfully!'.format(filename_new))

b_click = tk.Button(w, text = '计算', font = ('微软雅黑', 14, 'bold'), command = click)
b_click.place(x=450, y=8)

w.mainloop()