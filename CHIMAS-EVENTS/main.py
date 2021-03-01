import os
import pandas as pd
import cx_Oracle as cx
import tkinter as tk
from tkintertable import TableCanvas, TableModel
import datetime
import subprocess
from tkinter import messagebox

def run_select_sql(sql):
    tns = cx.makedsn('chepsvol1011.che.volvocars.net', 1521, service_name = 'dpomps1p_pri')
    db = cx.connect('pschimas', 'chimas123', tns, encoding = "UTF-8", nencoding = "UTF-8")
    cur = db.cursor()
    try:
        cur.execute(sql)
        rs = cur.fetchall()
        return rs
    except:
        return ['Error in select!']
    finally:
        cur.close()
        db.close()

def run_query():
    global df
    sql_conditions = ' '
    p_partno = e_partno.get()
    p_event = e_event.get()
    p_from = e_from.get()
    p_to = e_to.get()

    sql_common = '''
    select mt.EVENT_TYPE, mt.event_reason, pk.ODETTE_SEQ_NO, mt.from_loc, mt.FROM_LOC_TYPE, mt.to_loc, mt.to_loc_type, mf.partno, mf.qty, std_prices.std_price, mf.event_stamp, mf.oper from material_flow_int mf 
left join material_trans_int mt on (mf.FROM_LOC = mt.from_loc and mf.FROM_LOC_TYPE	= mt.FROM_LOC_TYPE and mf.TO_LOC = mt.to_loc and mf.TO_LOC_TYPE	= mt.TO_LOC_TYPE and mf.partno = mt.partno and mf.event_stamp = mt.event_stamp)
left join (select package_id, odette_seq_no from packages union all select package_id, odette_seq_no from prod_packages) pk on (mf.package_id = pk.package_id)
left join (select partno, std_price from standard_prices sp where from_day = (select max(from_day) from standard_prices where partno = sp.partno)) std_prices on mf.partno = std_prices.partno
where 1=1 {} order by event_stamp desc
    '''

    if p_partno:
        sql_conditions += "and mf.partno = '{}' ".format(p_partno)
    if p_event:
        sql_conditions += "and mt.event_type = '{}' ".format(p_event)
    if p_from:
        sql_conditions += "and mf.event_stamp >= '{}' ".format(p_from)
    if p_to:
        sql_conditions += "and mf.event_stamp <= '{}' ".format(p_to)

    rs = run_select_sql(sql_common.format(sql_conditions))
    try:
        df = pd.DataFrame(rs)
        df.columns = ['Event_type', 'Event_reason', 'Odette_seq_no', 'From_loc', 'From_loc_type', 'To_loc', 'To_loc_type', 'Partno', 'Qty', 'Standard_price', 'Event_stamp',
                      'Operator']
        tmodel.columnNames.clear()
        tmodel.data.clear()
        data = df.to_dict(orient='index')
        tmodel.importDict(data)
    except:
        tmodel.columnNames.clear()
        tmodel.data.clear()
        tmodel.importDict({0: {'没有查到记录！': None}})
    table.redraw()

def excel_export():
    global df
    output_file_name = 'Temp_Transaction_History_Report' + '_' + datetime.datetime.now().strftime(
        '%Y%m%d%H%M%S') + '.xlsx'
    writer = pd.ExcelWriter(output_file_name)
    df.to_excel(writer, sheet_name="事务记录", index=False)
    # adjust the column width. 中文2个字符宽度，英文1个字符宽度，根据标题行和内容自行确定每列宽度
    sheet_transaction = writer.sheets['事务记录']
    sheet_transaction.column_dimensions['A'].width = 12
    sheet_transaction.column_dimensions['B'].width = 14
    sheet_transaction.column_dimensions['C'].width = 16
    sheet_transaction.column_dimensions['D'].width = 14
    sheet_transaction.column_dimensions['E'].width = 16
    sheet_transaction.column_dimensions['F'].width = 14
    sheet_transaction.column_dimensions['G'].width = 14
    sheet_transaction.column_dimensions['H'].width = 10
    sheet_transaction.column_dimensions['I'].width = 8
    sheet_transaction.column_dimensions['J'].width = 16
    sheet_transaction.column_dimensions['K'].width = 18
    sheet_transaction.column_dimensions['L'].width = 14


    try:
        tk.messagebox.showinfo('info','Excel will be opened automatically, please wait.')
        writer.save()
    except Exception as e:
        tk.messagebox.showerror('错误', '保存excel出现异常：' + str(e))
        exit(2)

    # Normally at this step, excel file have been generated successfully. Open it.
    subprocess.Popen('"' + output_file_name + '"', shell=True)


w = tk.Tk()
w.geometry('1200x700+50+50')
w.title('PSCD Chimas事务历史查询')
w.resizable(0, 0)

canvas = tk.Canvas(w, bg='#AAAAAA', width=1200, height=700, highlightthickness=0, borderwidth=0)
canvas.place(x=0, y=0, anchor='nw')

tk.Label(canvas, bg='#AAAAAA', font=('微软雅黑', 12, 'bold'), text='Event Type:').place(x=5,y=5)
e_event = tk.StringVar()
tk.Entry(canvas, textvariable=e_event, width=3, font=('微软雅黑', 12)).place(x=105,y=6)

tk.Label(canvas, bg='#AAAAAA', font=('微软雅黑', 12, 'bold'), text='Partno:').place(x=138,y=5)
e_partno = tk.StringVar()
tk.Entry(canvas, textvariable=e_partno, width=10, font=('微软雅黑', 12)).place(x=206,y=6)

tk.Label(canvas, bg='#AAAAAA', font=('微软雅黑', 12, 'bold'), text='From Day:').place(x=305,y=5)
e_from = tk.StringVar()
tk.Entry(canvas, textvariable=e_from, width=10, font=('微软雅黑', 12)).place(x=400,y=6)

tk.Label(canvas, bg='#AAAAAA', font=('微软雅黑', 12, 'bold'), text='To Day:').place(x=500,y=5)
e_to = tk.StringVar()
tk.Entry(canvas, textvariable=e_to, width=10, font=('微软雅黑', 12)).place(x=570,y=6)

onemonthago=(datetime.datetime.now()+datetime.timedelta(days=-30)).strftime('%Y%m%d')
e_from.set(onemonthago)
today=datetime.datetime.now().strftime('%Y%m%d')
e_to.set(today)

tk.Button(canvas, text = 'Query', font=('微软雅黑', 10, 'bold'), command = run_query).place(x=1000, y=5)

tk.Button(canvas, text = 'Export to Excel', font=('微软雅黑', 10, 'bold'), command = excel_export).place(x=1070, y=5)

tframe = tk.Frame(canvas)
tframe.place(x=8, y=40)
tmodel = TableModel()
# tmodel.importDict(data)

table = TableCanvas(tframe, tmodel,
                    cellwidth=140, cellbackgr='#CCCCCC', height=610, width=1170,
                    col_positions=['col2', 'col1', 'label'],
                    thefont=('微软雅黑', 10), rowheight=18, rowheaderwidth=-5, rows=30, cols=30,
                    selectedcolor='#CCCCCC', rowselectedcolor='#CCCCCC',
                    multipleselectioncolor='#FFCCCC', autoresizecols=1, read_only=0, entrybackgr='#ff0000',
                    grid_color='#222222')
table.show()

# initialization
tmodel.columnNames.clear()
tmodel.data.clear()
tmodel.importDict({0: {'点击查询按钮查询': None}})
table.redraw()


w.mainloop()



