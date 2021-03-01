# -*- coding: <encoding name> -*- : # -*- coding: utf-8 -*-
import tkinter as tk
import os
from tkinter import ttk
from tkinter import messagebox
from DB_Connection import run_select_sql
import pandas as pd
from DB_Connection import run_oracle_function


def location_structure(p_user):
    pic_dir = os.getcwd() + '\\' + 'pics' + '\\'
    gm = tk.Toplevel()
    gm.iconbitmap(pic_dir + 'doge.ico')
    gm.geometry('675x900+600+50')
    gm.title('库位结构维护')
    gm.resizable(0, 0)

    # attach image
    canvas = tk.Canvas(gm, width=675, height=900, highlightthickness=0, borderwidth=0)
    image_file = tk.PhotoImage(file=pic_dir + 'location_structure_chn.gif')
    image = canvas.create_image(0, 0, anchor='nw', image=image_file)
    canvas.place(x=0, y=0, anchor='nw')

    e_loc_1 = tk.StringVar()
    tk.Entry(canvas, textvariable=e_loc_1, width=19, font=('微软雅黑', 12)).place(x=100, y=218)
    e_loc_descr1 = tk.StringVar()
    tk.Entry(canvas, textvariable=e_loc_descr1, width=29, font=('微软雅黑', 12)).place(x=135, y=250)
    e_loc_type1 = tk.StringVar()
    combobox_loc_type1 = ttk.Combobox(canvas, width=12, textvariable=e_loc_type1, font=('微软雅黑', 10))
    combobox_loc_type1.place(x=505, y=250)
    combobox_loc_type1['values'] = ['仓库', '库存区域', '库存地点']
    combobox_loc_type1.current(0)

    def search():
        rs = run_select_sql(
            "select loc_id, loc_type, loc_descr from locations where loc_id like '%{}%' and rownum = 1".format(
                e_loc_1.get()))
        try:
            rslt = [i if i != None else '' for i in rs[0]]  # change None to '' in result from sql
        except:
            rslt = ['', '', '']
        e_loc_1.set(rslt[0])
        if rslt[1] == 'Warehouse':
            combobox_loc_type1.current(0)
        elif rslt[1] == 'AREA':
            combobox_loc_type1.current(1)
        elif rslt[1] == 'STO':
            combobox_loc_type1.current(2)
        else:
            pass
        e_loc_descr1.set(rslt[2])

    tk.Button(canvas, text='查询', width=6, borderwidth=1, font=('微软雅黑', 9, 'bold'), command=search).place(x=280, y=218)

    def update():
        p_loc = e_loc_1.get()
        p_loc_descr = e_loc_descr1.get()
        dict = {'仓库': 'Warehouse', '库存区域': 'AREA', '库存地点': 'STO'}
        p_loc_type = dict.get(e_loc_type1.get(), 'unknown')
        ret = run_oracle_function('update_locations', [p_loc, p_loc_descr, p_loc_type, p_user])
        if ret == '0':
            tk.messagebox.showinfo('成功', '库位信息更新成功！')
        elif ret == '2':
            tk.messagebox.showerror('错误', '该位置已存在库位结构中，若要更改类型，先移除库位结构关系')
        else:
            tk.messagebox.showerror('错误', '发生其他异常，请检查重试或联系管理员')
        refresh_list()

    tk.Button(canvas, text='更新', width=6, borderwidth=1, font=('微软雅黑', 9, 'bold'), command=update).place(x=420, y=218)

    def new():
        p_loc = e_loc_1.get()
        p_loc_descr = e_loc_descr1.get()
        dict = {'仓库': 'Warehouse', '库存区域': 'AREA', '库存地点': 'STO'}
        p_loc_type = dict.get(e_loc_type1.get(), 'unknown')
        ret = run_oracle_function('create_locations', [p_loc, p_loc_descr, p_loc_type, p_user])
        if ret == '0':
            tk.messagebox.showinfo('成功', '库位信息添加成功！')
        elif ret == '2':
            tk.messagebox.showerror('错误', '该位置已存在！')
        else:
            tk.messagebox.showerror('错误', '发生其他异常，请检查重试或联系管理员')
        refresh_list()

    tk.Button(canvas, text='新建', width=6, borderwidth=1, font=('微软雅黑', 9, 'bold'), command=new).place(x=490, y=218)

    def delete():
        p_loc = e_loc_1.get()
        p_loc_descr = e_loc_descr1.get()
        dict = {'仓库': 'Warehouse', '库存区域': 'AREA', '库存地点': 'STO'}
        p_loc_type = dict.get(e_loc_type1.get(), 'unknown')
        ret = run_oracle_function('delete_locations', [p_loc, p_loc_descr, p_loc_type, p_user])
        if ret == '0':
            tk.messagebox.showinfo('成功', '库位信息删除成功！')
        elif ret == '2':
            tk.messagebox.showerror('错误', '该位置已存在库位结构中，若要删除，先移除库位结构关系')
        elif ret == '3':
            tk.messagebox.showerror('错误', '该位置上还有库存，不能直接删除库存地点')
        else:
            tk.messagebox.showerror('错误', '发生其他异常，请检查重试或联系管理员')
        refresh_list()

    tk.Button(canvas, text='删除', width=6, borderwidth=1, font=('微软雅黑', 9, 'bold'), command=delete).place(x=560, y=218)

    # 库位信息有更新或者新增后，均需要刷新当前的下拉列表，定义一个general的function
    def refresh_list():
        rs1 = run_select_sql("select loc_id from locations where loc_type = 'Warehouse' order by loc_id")
        warehouse_list = [i[0] for i in rs1]
        combobox_warehouse_2['values'] = warehouse_list
        combobox_warehouse_2.set('')
        combobox_warehouse_3['values'] = warehouse_list
        combobox_warehouse_3.set('')
        rs2 = run_select_sql("select loc_id from locations where loc_type in ('AREA','STO') order by loc_id")
        location_list = [i[0] for i in rs2]
        combobox_location_2['values'] = location_list
        combobox_location_2.set('')
        combobox_location_3.set('')

    # 第二组选择框和按钮
    e_warehouse_2 = tk.StringVar()
    combobox_warehouse_2 = ttk.Combobox(canvas, width=22, textvariable=e_warehouse_2, font=('微软雅黑', 12))
    combobox_warehouse_2.place(x=45, y=440)
    rs1 = run_select_sql("select loc_id from locations where loc_type = 'Warehouse' order by loc_id")
    warehouse_list = [i[0] for i in rs1]
    combobox_warehouse_2['values'] = warehouse_list
    e_location_2 = tk.StringVar()
    combobox_location_2 = ttk.Combobox(canvas, width=22, textvariable=e_location_2, font=('微软雅黑', 12))
    combobox_location_2.place(x=280, y=440)
    rs2 = run_select_sql("select loc_id from locations where loc_type in ('AREA','STO') order by loc_id")
    location_list = [i[0] for i in rs2]
    combobox_location_2['values'] = location_list

    def bind():
        p_loc = e_warehouse_2.get()
        p_subloc = e_location_2.get()
        ret = run_oracle_function('bind_locations', [p_loc, p_subloc, p_user])
        if ret == '0':
            tk.messagebox.showinfo('成功', '库位结构添加成功！')
        else:
            tk.messagebox.showerror('错误', '库存区域/地点{}已经存在于仓库{}下！'.format(p_subloc, ret))

    tk.Button(canvas, text='添加\n关联', width=6, height=2, borderwidth=1, font=('微软雅黑', 10, 'bold'), command=bind).place(
        x=560, y=418)

    # 第三组选择框和按钮
    def refresh_location_list3(arg1):
        rs = run_select_sql("select loc_id, subloc_id from location_structure order by loc_id, subloc_id")
        df = pd.DataFrame(rs)
        location_list = list(df[df[0] == e_warehouse_3.get()][1])
        combobox_location_3['values'] = location_list
        combobox_location_3.current(0)

    e_warehouse_3 = tk.StringVar()
    combobox_warehouse_3 = ttk.Combobox(canvas, width=22, textvariable=e_warehouse_3, font=('微软雅黑', 12))
    combobox_warehouse_3.place(x=45, y=640)
    rs1 = run_select_sql("select loc_id from locations where loc_type = 'Warehouse' order by loc_id")
    warehouse_list = [i[0] for i in rs1]
    combobox_warehouse_3['values'] = warehouse_list
    combobox_warehouse_3.bind('<<ComboboxSelected>>', refresh_location_list3)
    e_location_3 = tk.StringVar()
    combobox_location_3 = ttk.Combobox(canvas, width=22, textvariable=e_location_3, font=('微软雅黑', 12))
    combobox_location_3.place(x=280, y=640)

    def unbind():
        p_loc = e_warehouse_3.get()
        p_subloc = e_location_3.get()
        ret = run_oracle_function('unbind_locations', [p_loc, p_subloc, p_user])
        if ret == '0':
            tk.messagebox.showinfo('成功', '库位结构删除成功！')
        elif ret == '2':
            tk.messagebox.showerror('错误', '库存地点/区域下还有库存，不允许修改库位结构！')
        else:
            tk.messagebox.showerror('错误', '发生其他异常，请检查或联系系统管理员')

    tk.Button(canvas, text='删除\n关联', width=6, height=2, borderwidth=1, font=('微软雅黑', 10, 'bold'), command=unbind).place(
        x=560, y=618)

    label_user = tk.Label(canvas, text=' 当前登录用户：' + p_user + ' ',
                          font=('微软雅黑', 10, 'bold italic')).place(x=20, y=860, anchor='nw')
    gm.mainloop()


if __name__ == '__main__':
    location_structure('TEST')
