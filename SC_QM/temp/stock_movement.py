import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import pandas as pd
from DB_Connection import run_select_sql
from DB_Connection import get_feedback_from_scanning
from DB_Connection import run_oracle_function
from time import sleep
from QRcode import generate_new_label_file


def stock_movement(p_user):
    stmv_page = tk.Toplevel()
    stmv_page.geometry('600x350+600+300')
    stmv_page.title('stock movement')
    stmv_page.resizable(0, 0)

    # attach image
    canvas = tk.Canvas(stmv_page, width=600, height=350, highlightthickness=0, borderwidth=0)
    image_file = tk.PhotoImage(file='stock_movement.gif')
    image = canvas.create_image(0, 0, anchor='nw', image=image_file)
    canvas.place(x=0, y=0, anchor='nw')

    # parameter to adjust location
    x0, y0 = 25, -5

    # scanning label and entry
    l1 = tk.Label(canvas, text='Scanning Input:', font=('Calibri', 11)).place(x=20+x0, y=20+y0)
    e_content = tk.StringVar()
    e = tk.Entry(canvas, textvariable=e_content, width=50, font=('Calibri', 11))
    e.place(x=150+x0, y=20+y0)
    l_show_content = tk.StringVar()
    l_show_content.set(p_user + ', Welcome! Please scan the QR code label.')
    l_show = tk.Label(canvas, textvariable=l_show_content, width = 69, justify = tk.LEFT, font=('Calibri', 10))
    l_show.place(x=20+x0, y=50+y0)

    def send_scanning(arg):
        global p_partno, p_qty, p_supplier, p_dn, p_sn, p_md, p_dd, p_loc_id, p_parent_sn
        p_partno, p_qty, p_supplier, p_dn, p_sn, p_md, p_dd, p_loc_id, p_parent_sn = get_feedback_from_scanning(e_content.get())
        show_package_info = ''
        if p_qty != 0:
            show_package_info = "Package's SN is: " + p_sn + ". Current Location: " + p_loc_id + ". Qty: " + str(p_qty) + '.'
            if p_parent_sn:
                show_package_info = show_package_info + '\nThis package is a child package split from ' + p_parent_sn + '.'
            l_show_content.set(show_package_info)
            l_show.config(fg = 'green')
            e_move_qty.set(p_qty)
        else:
            show_package_info = "Cannot find current package! \nCheck if it hasn't been received or has been issued?"
            l_show_content.set(show_package_info)
            l_show.config(fg = 'red')
        sleep(0.2)
        e_content.set('')

    e.bind('<Return>', send_scanning)

    # define 3 label and input qty entry
    label1 = tk.Label(canvas, text = 'Choose Warehouse', font = ('Calibri', 10)).place(x = 20+x0, y = 100+y0, anchor = 'nw')
    label2 = tk.Label(canvas, text = 'Choose GR Location', font = ('Calibri', 10)).place(x = 230+x0, y = 100+y0, anchor = 'nw')
    label3 = tk.Label(canvas, text = 'Move Qty', font = ('Calibri', 10)).place(x = 440+x0, y = 100+y0, anchor = 'nw')
    e_move_qty = tk.StringVar()
    e_move = tk.Entry(canvas, textvariable = e_move_qty, width = 9, font=('Calibri', 11))
    e_move.place(x=440+x0, y=124+y0)


    def refresh_location_list(arg1):
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
    combobox_WH.place(x = 20+x0, y = 125+y0, anchor = 'nw')
    combobox_WH['values'] = warehouse_list
    combobox_WH.bind('<<ComboboxSelected>>',refresh_location_list)

    location_choose = tk.StringVar()
    combobox_LO = ttk.Combobox(canvas, width = 30, textvariable = location_choose)
    combobox_LO.place(x = 230+x0, y = 125+y0, anchor = 'nw')

    def confirm_move():
        global p_partno, p_qty, p_supplier, p_dn, p_sn, p_md, p_dd, p_loc_id, p_parent_sn
        go_next = tk.messagebox.askyesno('Info','You choose to move to Warehouse: '+warehouse_choose.get()+' and Location: '+location_choose.get()+'. Are you sure?')
        if go_next:
            l_show_content.set("Moving in progress...")
            move_qty = eval(e_move_qty.get())
            if p_sn and p_loc_id and move_qty and location_choose.get() and p_user:
                if p_loc_id == location_choose.get():
                    tk.messagebox.showerror('ERROR!','Cannot move to the same location!')
                elif p_qty < move_qty or move_qty <= 0:
                    tk.messagebox.showerror('ERROR!', "Move qty error.")
                else:
                    retVar = run_oracle_function('stock_movement', [p_sn, move_qty, p_loc_id, location_choose.get(), p_user])
                    print(retVar)
                    if retVar == '0':
                        tk.messagebox.showinfo('Success!', 'Move successfully!')
                        l_show_content.set('Scan Next package')
                        e_content.set('')
                        e_move_qty.set('')
                        if move_qty < p_qty:
                            l_show_content.set('In this movement, a new child SN generated for the child package.Image file has been \ngenerated under \\newlables directory, print it and stick to new package.')
                            # split a new package, need add function here to notify user to print new label.
                            p_child_sn = run_oracle_function('get_new_generated_child_sn', [p_user])
                            generate_new_label_file(p_child_sn, p_partno, move_qty, p_user)
                            pass
                    else:
                        tk.messagebox.showerror('ERROR!','Move failed. Contact Administrator.')
            else:
                tk.messagebox.showerror('ERROR!','Goods Moving information is not complete')
        else:
            pass

    b = tk.Button(canvas, text = 'MOVE!', width = 15, font=('Calibri', 8), command = confirm_move).place(x= 450, y=300)


    label_user = tk.Label(canvas, text=' Current Login User: ' + p_user + ' ',
                              font=('Calibri', 10, 'bold italic')).place(x=20, y=320, anchor='nw')
    stmv_page.mainloop()


if __name__ == '__main__':
    stock_movement('TEST')
