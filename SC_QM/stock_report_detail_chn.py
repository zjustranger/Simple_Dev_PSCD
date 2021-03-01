import tkinter as tk
from tkintertable import TableCanvas, TableModel
import pandas as pd
from DB_Connection import run_select_sql
import os
import datetime
import subprocess

output_temp_dir = os.getcwd() + r'\temp\tempdata' + '\\'

def stock_detail(p_user):
    pic_dir = os.getcwd() + '\\' + 'pics' + '\\'
    stock_detail = tk.Toplevel()
    stock_detail.iconbitmap(pic_dir+'doge.ico')
    stock_detail.geometry('1600x900+160+50')
    stock_detail.title('库存详情查询')
    stock_detail.resizable(0,0)

    canvas = tk.Canvas(stock_detail, width = 1600, height = 900, highlightthickness=0, borderwidth=0)
    image_file = tk.PhotoImage(file=pic_dir+'stock_detail_chn.gif')
    image = canvas.create_image(0, 0, anchor='nw', image=image_file)
    canvas.place(x=0, y=0, anchor='nw')

    x0, y0 = 0, 2

    e_partno_content = tk.StringVar()
    e_partno = tk.Entry(canvas, textvariable=e_partno_content, width=10, font=('微软雅黑', 13))
    e_partno.place(x=130+x0, y=30+y0)

    e_warehouse_content = tk.StringVar()
    e_warehouse = tk.Entry(canvas, textvariable=e_warehouse_content, width=15, font=('微软雅黑', 13))
    e_warehouse.place(x=305 + x0, y=30 + y0)

    e_supplier_content = tk.StringVar()
    e_supplier = tk.Entry(canvas, textvariable=e_supplier_content, width=9, font=('微软雅黑', 13))
    e_supplier.place(x=595 + x0, y=30 + y0)

    def run_query():
        global df
        sql_conditions = ' '
        p_partno = e_partno_content.get()
        p_warehouse = e_warehouse_content.get()
        p_supplier = e_supplier_content.get()

        sql_common = '''
            select iv.partno, parts.part_descr, ls.loc_id, iv.loc_id, iv.qty, iv.serial_no, pk.batch_no, ss.inv_descr, pk.supplier_id, pk.dn, pk.parent_sn, pk.prod_date, pk.due_date from inventory iv left join parts on (iv.PARTNO = parts.partno) left join packages pk
            on (iv.PACKAGE_ID = pk.package_id and iv.SERIAL_NO = pk.SERIAL_NO) left join location_structure ls on (iv.loc_id = ls.subloc_id) left join stock_status ss on (pk.inv_type = ss.inv_type) where 1=1 {} order by iv.partno, ls.loc_id, iv.loc_id, iv.qty            
            '''

        if p_partno:
            sql_conditions += "and iv.partno = '{}'".format(p_partno)
        if p_warehouse:
            sql_conditions += "and ls.loc_id = '{}'".format(p_warehouse)
        if p_supplier:
            sql_conditions += "and pk.supplier_id = '{}'".format(p_supplier)

        rs = run_select_sql(sql_common.format(sql_conditions))
        try:
            df = pd.DataFrame(rs)
            df.columns = ['物料号', '物料描述', '仓库', '库存地点/区域', '数量', '序列号', '批次号', '库存状态', '供应商编码', '发运单号', '拆分自原标签序列号',
                           '生产日期', '过期日期']
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
        output_file_name = 'Temp_Stock_Detail_Report' + '_' + p_user + '_' + datetime.datetime.now().strftime(
            '%Y%m%d%H%M%S') + '.xlsx'
        writer = pd.ExcelWriter(output_temp_dir + output_file_name)
        df.to_excel(writer, sheet_name="库存详情", index=False)
        # adjust the column width. 中文2个字符宽度，英文1个字符宽度，根据标题行和内容自行确定每列宽度
        sheet_stock_detail = writer.sheets['库存详情']
        sheet_stock_detail.column_dimensions['A'].width = 12
        sheet_stock_detail.column_dimensions['B'].width = 20
        sheet_stock_detail.column_dimensions['C'].width = 20
        sheet_stock_detail.column_dimensions['D'].width = 20
        sheet_stock_detail.column_dimensions['E'].width = 20
        sheet_stock_detail.column_dimensions['F'].width = 14
        sheet_stock_detail.column_dimensions['G'].width = 20
        sheet_stock_detail.column_dimensions['H'].width = 20
        sheet_stock_detail.column_dimensions['I'].width = 20
        sheet_stock_detail.column_dimensions['J'].width = 20
        sheet_stock_detail.column_dimensions['K'].width = 20
        sheet_stock_detail.column_dimensions['L'].width = 20


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


    stock_detail.mainloop()


if __name__ == '__main__':
    stock_detail('TEST')