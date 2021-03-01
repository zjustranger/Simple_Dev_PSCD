import tkinter as tk
from tkintertable import TableCanvas, TableModel
import pandas as pd
from DB_Connection import run_select_sql
import os
import datetime
import subprocess

output_temp_dir = os.getcwd() + r'\temp\tempdata' + '\\'

def shelf_life_query(p_user):
    pic_dir = os.getcwd() + '\\' + 'pics' + '\\'
    shelf_life = tk.Toplevel()
    shelf_life.iconbitmap(pic_dir+'doge.ico')
    shelf_life.geometry('1600x900+160+50')
    shelf_life.title('保质期查询')
    shelf_life.resizable(0,0)

    canvas = tk.Canvas(shelf_life, width = 1600, height = 900, highlightthickness=0, borderwidth=0)
    image_file = tk.PhotoImage(file=pic_dir+'shelf_life.gif')
    image = canvas.create_image(0, 0, anchor='nw', image=image_file)
    canvas.place(x=0, y=0, anchor='nw')

    x0, y0 = 0, 2

    e_partno_content = tk.StringVar()
    e_partno = tk.Entry(canvas, textvariable=e_partno_content, width=10, font=('微软雅黑', 13))
    e_partno.place(x=130+x0, y=30+y0)

    e_batch_no = tk.StringVar()
    e_batch = tk.Entry(canvas, textvariable=e_batch_no, width=15, font=('微软雅黑', 13))
    e_batch.place(x=330 + x0, y=30 + y0)

    e_valid = tk.StringVar()
    e_valid_less = tk.Entry(canvas, textvariable=e_valid, width=9, font=('微软雅黑', 13))
    e_valid_less.place(x=695 + x0, y=30 + y0)

    def run_query():
        global df
        sql_conditions = ' '
        p_partno = e_partno_content.get()
        p_batch_no = e_batch_no.get()
        p_valid = e_valid.get()

        sql_common = '''
        select partno, part_descr, loc_id, qty, inv_descr, batch_no, due_date, remaining, serial_no, supplier_id, dn, prod_date, report_date from
        (select pk.partno, pa.part_descr, iv.loc_id, pk.qty, ss.inv_descr, pk.batch_no, substr(pk.due_date,1,4)||'/'||substr(pk.due_date,5,2)||'/'||substr(pk.due_date,7,2) due_date,
        round(to_date(pk.due_date, 'YYYYMMDD') - sysdate + 1, 1) remaining, pk.serial_no, pk.supplier_id, pk.dn, substr(pk.prod_date,1,4)||'/'||substr(pk.prod_date,5,2)||'/'||substr(pk.prod_date,7,2) prod_date, to_char(sysdate, 'YYYY/MM/DD HH24:MI:SS') report_date
        from packages pk left join parts pa on (pk.partno = pa.partno) left join inventory iv on (pk.serial_no = iv.serial_no and pk.qty = iv.qty) left join stock_status ss on (pk.inv_type = ss.inv_type))
        where 1=1 {} order by partno, loc_id
            '''

        if p_partno:
            sql_conditions += "and partno = '{}'".format(p_partno.upper())
        if p_batch_no:
            sql_conditions += "and batch_no = '{}'".format(p_batch_no.upper())
        if p_valid:
            sql_conditions += "and remaining <= '{}'".format(p_valid)

        rs = run_select_sql(sql_common.format(sql_conditions))
        try:
            df = pd.DataFrame(rs)
            df.columns = ['物料号', '物料描述', '库存地点/区域', '数量', '库存类型', '批次号', '过期日期', '剩余有效期天数', '序列号', '供应商编号', '发运单号',
                          '生产日期', '报表生成时间']
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
        output_file_name = 'Temp_Shelf_Life_Report' + '_' + p_user + '_' + datetime.datetime.now().strftime(
            '%Y%m%d%H%M%S') + '.xlsx'
        writer = pd.ExcelWriter(output_temp_dir + output_file_name)
        df.to_excel(writer, sheet_name="保质期查询", index=False)
        # adjust the column width. 中文2个字符宽度，英文1个字符宽度，根据标题行和内容自行确定每列宽度
        sheet_shelf = writer.sheets['保质期查询']
        sheet_shelf.column_dimensions['A'].width = 12
        sheet_shelf.column_dimensions['B'].width = 30
        sheet_shelf.column_dimensions['C'].width = 30
        sheet_shelf.column_dimensions['D'].width = 12
        sheet_shelf.column_dimensions['E'].width = 12
        sheet_shelf.column_dimensions['F'].width = 30
        sheet_shelf.column_dimensions['G'].width = 12
        sheet_shelf.column_dimensions['H'].width = 20
        sheet_shelf.column_dimensions['I'].width = 20
        sheet_shelf.column_dimensions['J'].width = 20
        sheet_shelf.column_dimensions['K'].width = 20
        sheet_shelf.column_dimensions['L'].width = 12
        sheet_shelf.column_dimensions['M'].width = 20

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


    shelf_life.mainloop()


if __name__ == '__main__':
    shelf_life_query('TEST')