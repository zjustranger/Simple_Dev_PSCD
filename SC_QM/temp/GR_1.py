import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from DB_Connection import run_select_sql
import pandas as pd
from GR_2 import GR_2

def GR_1(p_user, p_hostname, p_ip):
    gr_1 = tk.Toplevel()
    gr_1.geometry('600x350+600+300')
    gr_1.title('GR Scanning')
    gr_1.resizable(0,0)

    # attach image
    canvas = tk.Canvas(gr_1, width = 600, height = 350, highlightthickness = 0, borderwidth = 0)
    image_file = tk.PhotoImage(file='GR_1.gif')
    image = canvas.create_image(0,0, anchor='nw', image=image_file)
    canvas.place(x = 0, y = 0, anchor = 'nw')

    x0, y0 = 20, 50
    label1 = tk.Label(canvas, text = 'Choose Warehouse', font = ('Calibri', 10)).place(x = 20+x0, y = 80+y0, anchor = 'nw')
    label2 = tk.Label(canvas, text = 'Choose GR Location', font = ('Calibri', 10)).place(x = 270+x0, y = 80+y0, anchor = 'nw')

    def show_choose(arg1):
        tk.messagebox.showinfo(title='Welcome', message='You choose ' + warehouse_choose.get())

    def refresh_location_list(arg1):
        # if warehouse_choose.get() == 'IT_Office_Warehouse':
        #     combobox_LO['values'] = ['IT_TEMP_AREA_2','IT_Office_Rack01','IT_Office_Rack02']
        #     combobox_LO.current(0)
        # elif warehouse_choose.get() == 'IT_TCF_Warehouse':
        #     combobox_LO['values'] = ['IT_TEMP_AREA_1','IT_TCF_Rack01','IT_TCF_Rack02']
        #     combobox_LO.current(0)
        df2 = pd.DataFrame(rs2)
        location_list = list(df2[df2[0] == warehouse_choose.get()][1])
        combobox_LO['values'] = location_list
        combobox_LO.current(0)

    rs1 = run_select_sql("select loc_id from locations where loc_type = 'Warehouse'")
    df1 = pd.DataFrame(rs1)
    warehouse_list = list(df1[0])
    rs2 = run_select_sql("select loc_id, subloc_id from location_structure")

    warehouse_choose = tk.StringVar()
    combobox_WH = ttk.Combobox(canvas, width = 30, textvariable = warehouse_choose)
    combobox_WH.place(x = 20+x0, y = 110+y0, anchor = 'nw')
    combobox_WH['values'] = warehouse_list
    combobox_WH.bind('<<ComboboxSelected>>',refresh_location_list)

    location_choose = tk.StringVar()
    combobox_LO = ttk.Combobox(canvas, width = 30, textvariable = location_choose)
    combobox_LO.place(x = 270+x0, y = 110+y0, anchor = 'nw')
    # combobox_WH['values'] = ['IT_Office_Warehouse','IT_TCF_Warehouse']
    # combobox_WH.bind('<<ComboboxSelected>>',show_choose)

    def confirm_choose():
        go_next = tk.messagebox.askyesno('Info','You have choosed Warehouse: '+warehouse_choose.get()+' and Location: '+location_choose.get()+'. Are you sure?')
        if go_next == True:
            gr_1.destroy()
            GR_2(p_user, p_hostname, p_ip, location_choose.get())
        else:
            pass

    b = tk.Button(canvas, text = 'GO!', width = 15, font=('Calibri', 8), command = confirm_choose).place(x= 400, y=300)

    # b1 = tk.Button(GR_Main, width = 5, height = 2, text = 'GR', command = show_gr)
    # b1.config(justify = tk.LEFT)
    # b1.pack()
    label_user = tk.Label(canvas, text=' Current Login User: ' + p_user + ' ',
                          font=('Calibri', 10, 'bold italic')).place(x=20, y=320, anchor='nw')
    gr_1.mainloop()


if __name__ == '__main__':
    GR_1('TEST', '5CG94599LK', '10.234.34.178')
