import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import pandas as pd
from DB_Connection import run_select_sql
from DB_Connection import get_feedback_from_scanning
from DB_Connection import run_oracle_function
from time import sleep
from QRcode import generate_new_label_file
import os


def stock_movement(p_user):
    pic_dir = os.getcwd() + '\\' + 'pics' + '\\'
    stmv_page = tk.Toplevel()
    stmv_page.iconbitmap(pic_dir + 'doge.ico')
    stmv_page.geometry('1200x700+350+150')
    stmv_page.title('库存移动')
    stmv_page.resizable(0, 0)

    # attach image
    canvas = tk.Canvas(stmv_page, width=1200, height=700, highlightthickness=0, borderwidth=0)
    image_file = tk.PhotoImage(file=pic_dir + 'stock_movement_chn.gif')
    image = canvas.create_image(0, 0, anchor='nw', image=image_file)
    canvas.place(x=0, y=0, anchor='nw')

    # parameter to adjust location
    x0, y0 = 25, -5

    # scanning label and entry
    e_content = tk.StringVar()
    e = tk.Entry(canvas, textvariable=e_content, width=75, font=('微软雅黑', 16))
    e.place(x=230+x0, y=125+y0)
    l_show_content = tk.StringVar()
    l_show_content.set(p_user + '，欢迎！扫描需要移动的包装二维码')
    l_show = tk.Label(canvas, textvariable=l_show_content, width = 74, justify = tk.LEFT, font=('微软雅黑', 15, 'bold'))
    l_show.place(x=90+x0, y=170+y0)

    def send_scanning(arg):
        global p_partno, p_qty, p_supplier, p_dn, p_sn, p_bn, p_md, p_dd, p_loc_id, p_parent_sn
        p_partno, p_qty, p_supplier, p_dn, p_sn, p_bn, p_md, p_dd, p_loc_id, p_parent_sn = get_feedback_from_scanning(e_content.get())
        show_package_info = ''
        if p_qty != 0:
            show_package_info = "包装序列号：{}。包装批次号：{}。当前位于：{}。数量：{}。".format(p_sn, p_bn, p_loc_id, str(p_qty))
            if p_parent_sn:
                show_package_info = show_package_info + '\n这是一个子包装，拆分自' + p_parent_sn + '。'
            l_show_content.set(show_package_info)
            l_show.config(fg = 'green')
            e_move_qty.set(p_qty)
        else:
            show_package_info = "找不到这个包装！\n它是不是还没入库或者已经出库完成了？"
            l_show_content.set(show_package_info)
            l_show.config(fg = 'red')
        sleep(0.2)
        e_content.set('')

    e.bind('<Return>', send_scanning)

    # define 3 label and input qty entry
    e_move_qty = tk.StringVar()
    e_move = tk.Entry(canvas, textvariable = e_move_qty, width = 15, font=('Calibri', 15))
    e_move.place(x=905+x0, y=330+y0)


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
    combobox_WH = ttk.Combobox(canvas, width = 25, font = ('微软雅黑', 15), textvariable = warehouse_choose)
    combobox_WH.place(x = 90+x0, y = 330+y0, anchor = 'nw')
    combobox_WH['values'] = warehouse_list
    combobox_WH.bind('<<ComboboxSelected>>',refresh_location_list)

    location_choose = tk.StringVar()
    combobox_LO = ttk.Combobox(canvas, width = 25, font = ('微软雅黑', 15), textvariable = location_choose)
    combobox_LO.place(x = 425+x0, y = 330+y0, anchor = 'nw')

    def confirm_move():
        global p_partno, p_qty, p_supplier, p_dn, p_sn, p_md, p_dd, p_loc_id, p_parent_sn
        go_next = tk.messagebox.askyesno('提示','移动至仓库：'+warehouse_choose.get()+'，库位：'+location_choose.get()+'，继续？')
        if go_next:
            l_show_content.set("正在移动...")
            move_qty = eval(e_move_qty.get())
            if p_sn and p_loc_id and move_qty and location_choose.get() and p_user:
                if p_loc_id == location_choose.get():
                    tk.messagebox.showerror('错误','不能移至相同的库位')
                elif p_qty < move_qty or move_qty <= 0:
                    tk.messagebox.showerror('错误', "移动数量异常")
                else:
                    retVar = run_oracle_function('stock_movement', [p_sn, move_qty, p_loc_id, location_choose.get(), p_user])
                    print(retVar)
                    if retVar == '0':
                        tk.messagebox.showinfo('成功', '移动完毕！')
                        l_show_content.set('扫描下一个需要移动的包装')
                        e_content.set('')
                        e_move_qty.set('')
                        if move_qty < p_qty:
                            l_show_content.set('在这次移动中，产生了一个子包装并生成了一个新的批次号。\n新生成的二维码标签放至在\\newlables目录下，请打印并贴给子包装。')
                            # split a new package, need add function here to notify user to print new label.
                            p_child_sn = run_oracle_function('get_new_generated_child_sn', [p_user])
                            generate_new_label_file(p_child_sn, p_partno, move_qty, p_dd, p_user)
                            pass
                        e.focus_set()
                        e.icursor(0)
                        stmv_page.lift()
                    else:
                        tk.messagebox.showerror('错误','移动失败，联系系统管理员！')
            else:
                tk.messagebox.showerror('错误','库存移动信息不完整！')
        else:
            pass

    b = tk.Button(canvas, text = '移动！', width = 15, font=('微软雅黑', 11, 'bold'), command = confirm_move).place(x= 950, y=600)


    label_user = tk.Label(canvas, text=' 当前登录用户：' + p_user + ' ',
                          font=('微软雅黑', 10, 'bold italic')).place(x=20, y=650, anchor='nw')
    stmv_page.mainloop()


if __name__ == '__main__':
    stock_movement('TEST')
