import tkinter as tk
from tkintertable import TableCanvas, TableModel
import pandas as pd
from DB_Connection import run_select_sql

def tbd1():
    stock_detail = tk.Toplevel()
    stock_detail.geometry('1600x900+160+50')
    stock_detail.title('stock detail report')
    stock_detail.resizable(0, 0)

    canvas = tk.Canvas(stock_detail, width = 1600, height = 900, highlightthickness=0, borderwidth=0)
    image_file = tk.PhotoImage(file='stock_detail.gif')
    image = canvas.create_image(0, 0, anchor='nw', image=image_file)
    canvas.place(x=0, y=0, anchor='nw')

    x0, y0 = 0, 0

    l_partno = tk.Label(canvas, text='Part Number:', font=('Calibri', 13))
    l_partno.place(x=50+x0, y=30+y0)
    e_partno_content = tk.StringVar()
    e_partno = tk.Entry(canvas, textvariable=e_partno_content, width=10, font=('Calibri', 14))
    e_partno.place(x=170+x0, y=30+y0)

    def run_query():
        if e_partno_content.get() == None:
            pass
        else:
            p_partno = e_partno_content.get()

            sql_common = '''
                        select iv.partno, iv.loc_id, iv.qty, iv.serial_no, pk.supplier_id, pk.dn, pk.parent_sn, pk.prod_date, pk.valid_day, pk.due_date from inventory iv left join packages pk
                on (iv.PACKAGE_ID = pk.package_id and iv.SERIAL_NO = pk.SERIAL_NO) where 1=1 {} order by iv.partno, iv.loc_id, iv.qty
                '''
            sql_conditions = "and iv.partno like '{}'".format(e_partno_content.get())
            rs = run_select_sql(sql_common.format(sql_conditions))
            df = pd.DataFrame(rs)
            df.columns = ['Part Number', 'Location', 'Qty', 'Serial Number', 'Supplier', 'Dispatch Note', 'Parent SN',
                           'Production Date', 'Valid Day', 'Due Date']
            tmodel.columnNames.clear()
            tmodel.data.clear()
            data = df.to_dict(orient='index')
            tmodel.importDict(data)
            table.redraw()

    b_query = tk.Button(canvas, text = 'Query', font=('Calibri', 12, 'bold'), command = run_query)
    b_query.place(x=1300+x0, y=30+y0)

    def excel_export():
        pass
    b_excel = tk.Button(canvas, text = 'Export to Excel', font=('Calibri', 12, 'bold'), command = excel_export)
    b_excel.place(x=1440+x0, y=30+y0)


    tframe = tk.Frame(canvas)
    tframe.place(x=50, y=80)
    tmodel = TableModel()
    # tmodel.importDict(data)

    table = TableCanvas(tframe, tmodel,
    cellwidth=150, cellbackgr='#CCCCCC', height= 770, width = 1500, col_positions = ['col2', 'col1', 'label'],
    thefont=('Arial',10),rowheight=18, rowheaderwidth=-5, rows = 30, cols = 30, selectedcolor= '#CCCCCC', rowselectedcolor = '#CCCCCC',
    multipleselectioncolor = '#FFCCCC',autoresizecols = 1, read_only=1, entrybackgr = '#ff0000', grid_color = '#222222')
    table.show()

    stock_detail.mainloop()


if __name__ == '__main__':
    tbd1()