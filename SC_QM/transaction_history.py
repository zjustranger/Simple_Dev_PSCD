import tkinter as tk
from tkintertable import TableCanvas, TableModel
import pandas as pd
from DB_Connection import run_select_sql
import os
import datetime
import subprocess

output_temp_dir = os.getcwd() + r'\temp\tempdata' + '\\'

def transaction_history(p_user):
    pic_dir = os.getcwd() + '\\' + 'pics' + '\\'
    tran_his = tk.Toplevel()
    tran_his.iconbitmap(pic_dir+'doge.ico')
    tran_his.geometry('1600x900+160+50')
    tran_his.title('事务历史记录查询')
    tran_his.resizable(0,0)

    canvas = tk.Canvas(tran_his, width = 1600, height = 900, highlightthickness=0, borderwidth=0)
    image_file = tk.PhotoImage(file=pic_dir+'transaction_history_chn.gif')
    image = canvas.create_image(0, 0, anchor='nw', image=image_file)
    canvas.place(x=0, y=0, anchor='nw')

    x0, y0 = 0, 2

    e_partno_content = tk.StringVar()
    e_partno = tk.Entry(canvas, textvariable=e_partno_content, width=10, font=('微软雅黑', 13))
    e_partno.place(x=130+x0, y=30+y0)

    e_batch_no = tk.StringVar()
    e_batch = tk.Entry(canvas, textvariable=e_batch_no, width=15, font=('微软雅黑', 13))
    e_batch.place(x=330 + x0, y=30 + y0)

    e_userid = tk.StringVar()
    e_user = tk.Entry(canvas, textvariable=e_userid, width=9, font=('微软雅黑', 13))
    e_user.place(x=595 + x0, y=30 + y0)

    def run_query():
        global df
        sql_conditions = ' '
        p_partno = e_partno_content.get()
        p_batch_no = e_batch_no.get()
        p_userid = e_userid.get()

        sql_common = '''
        select ts.partno, pa.part_descr, ts.qty, ts.location, ss.inv_descr, mt.TYPE_DESCR, ts.batch_no, ts.supplier_id, ts.dn, ts.userid, to_char(ts.sys_timestamp, 'YYYY/MM/DD HH24:MI:SS'), ts.serial_no from
        (select sys_timestamp, partno, qty, supplier_id, inv_type, movement_type, to_loc as location, userid, DN, serial_no, seq, batch_no from transactions where to_loc is not NULL
        union all
        select sys_timestamp, partno, -qty, supplier_id, inv_type, movement_type, from_loc as location, userid, DN, serial_no, seq, batch_no from transactions where from_loc is not NULL) ts
        left join movement_type mt on (ts.MOVEMENT_TYPE = mt.type_id) left join stock_status ss on (ts.inv_type = ss.inv_type) left join parts pa on (ts.partno = pa.partno)
        where 1 = 1 {}
        order by ts.seq, ts.qty
            '''

        if p_partno:
            sql_conditions += "and ts.partno = '{}'".format(p_partno.upper())
        if p_batch_no:
            sql_conditions += "and ts.batch_no = '{}'".format(p_batch_no.upper())
        if p_userid:
            sql_conditions += "and ts.userid = '{}'".format(p_userid.upper())

        rs = run_select_sql(sql_common.format(sql_conditions))
        try:
            df = pd.DataFrame(rs)
            df.columns = ['物料号', '物料描述', '数量', '库存地点/区域', '库存类型', '操作事务描述', '批次号', '供应商编码', '发运单号', '操作用户', '操作时间',
                          '序列号']
            tmodel.columnNames.clear()
            tmodel.data.clear()
            data = df.to_dict(orient='index')
            tmodel.importDict(data)
        except:
            tmodel.columnNames.clear()
            tmodel.data.clear()
            tmodel.importDict({0: {'没有查到记录！': None}})
        table.redraw()

    b_query = tk.Button(canvas, text = '查询', font=('微软雅黑', 12, 'bold'), command = run_query)
    b_query.place(x=1300+x0, y=30+y0)

    def excel_export():
        global df
        output_file_name = 'Temp_Transaction_History_Report' + '_' + p_user + '_' + datetime.datetime.now().strftime(
            '%Y%m%d%H%M%S') + '.xlsx'
        writer = pd.ExcelWriter(output_temp_dir + output_file_name)
        df.to_excel(writer, sheet_name="事务记录", index=False)
        # adjust the column width. 中文2个字符宽度，英文1个字符宽度，根据标题行和内容自行确定每列宽度
        sheet_transaction = writer.sheets['事务记录']
        sheet_transaction.column_dimensions['A'].width = 12
        sheet_transaction.column_dimensions['B'].width = 30
        sheet_transaction.column_dimensions['C'].width = 12
        sheet_transaction.column_dimensions['D'].width = 30
        sheet_transaction.column_dimensions['E'].width = 12
        sheet_transaction.column_dimensions['F'].width = 20
        sheet_transaction.column_dimensions['G'].width = 30
        sheet_transaction.column_dimensions['H'].width = 12
        sheet_transaction.column_dimensions['I'].width = 20
        sheet_transaction.column_dimensions['J'].width = 20
        sheet_transaction.column_dimensions['K'].width = 20
        sheet_transaction.column_dimensions['L'].width = 20


        try:
            writer.save()
        except Exception as e:
            tk.messagebox.showerror('错误', '保存excel出现异常：' + str(e))
            exit(2)

        # Normally at this step, excel file have been generated successfully. Open it.
        subprocess.Popen('"' + output_temp_dir + output_file_name + '"', shell=True)

    b_excel = tk.Button(canvas, text = '导出Excel', font=('微软雅黑', 12, 'bold'), command = excel_export)
    b_excel.place(x=1440+x0, y=30+y0)


    tframe = tk.Frame(canvas)
    tframe.place(x=50, y=80)
    tmodel = TableModel()
    # tmodel.importDict(data)

    table = TableCanvas(tframe, tmodel,
    cellwidth=175, cellbackgr='#CCCCCC', height= 770, width = 1500, col_positions = ['col2', 'col1', 'label'],
    thefont=('微软雅黑',10),rowheight=18, rowheaderwidth=-5, rows = 30, cols = 30, selectedcolor= '#CCCCCC', rowselectedcolor = '#CCCCCC',
    multipleselectioncolor = '#FFCCCC',autoresizecols = 1, read_only=0, entrybackgr = '#ff0000', grid_color = '#222222')
    table.show()

    #initialization
    tmodel.columnNames.clear()
    tmodel.data.clear()
    tmodel.importDict({0:{'点击查询按钮查询':None}})
    table.redraw()


    tran_his.mainloop()


if __name__ == '__main__':
    transaction_history('TEST')