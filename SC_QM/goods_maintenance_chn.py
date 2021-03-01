# -*- coding: <encoding name> -*- : # -*- coding: utf-8 -*-
import tkinter as tk
import os
from tkinter import ttk
from tkinter import messagebox
from DB_Connection import run_select_sql
from DB_Connection import run_oracle_function

def goods_maintenance(p_user):
    pic_dir = os.getcwd() + '\\' + 'pics' + '\\'
    gm = tk.Toplevel()
    gm.iconbitmap(pic_dir + 'doge.ico')
    gm.geometry('675x900+600+50')
    gm.title('物料属性维护')
    gm.resizable(0, 0)

    # attach image
    canvas = tk.Canvas(gm, width=675, height=900, highlightthickness=0, borderwidth=0)
    image_file = tk.PhotoImage(file=pic_dir + 'goods_maintenance_chn.gif')
    image = canvas.create_image(0, 0, anchor='nw', image=image_file)
    canvas.place(x=0, y=0, anchor='nw')


    e_partno_input = tk.StringVar()
    tk.Entry(canvas, textvariable=e_partno_input, width=10, font=('微软雅黑', 14)).place(x=100, y=77)

    def search():
        rs = run_select_sql("select partno, part_descr, min_qty, max_qty, valid_day, supplier_id, invalid_flag, chem_flag, unit, serial_flag from parts where partno like upper('%{}%') and rownum = 1".format(e_partno_input.get()))
        try:
            rslt = [i if i != None else '' for i in rs[0]]  # change None to '' in result from sql
            e_partno.set(rslt[0])
            e_descr.set(rslt[1])
            e_min.set(rslt[2])
            e_max.set(rslt[3])
            e_warrenty.set(rslt[4])
            e_supplier.set(rslt[5])
            # 根据invalid flag和chemical flag的内容，改变选项
            if rslt[6] == 'X':
                e_invalid.set(1)
            else:
                e_invalid.set(0)
            if rslt[7] == 'X':
                e_shelf.set(1)
            else:
                e_shelf.set(0)
            # 根据单位，改变当前单位选项
            if rslt[8] == '其他':
                combobox_unit.current(0)
            elif rslt[8] == '个':
                combobox_unit.current(1)
            elif rslt[8] == '瓶':
                combobox_unit.current(2)
            elif rslt[8] == '桶':
                combobox_unit.current(3)
            else:
                pass
            # 改变serial flag的值
            if rslt[9] == 'X':
                e_serial.set(1)
            else:
                e_serial.set(0)
        except:
            e_partno.set('')
            e_descr.set('')
            e_min.set('')
            e_max.set('')
            e_warrenty.set('')
            e_supplier.set('')
            e_invalid.set(0)
            e_shelf.set(0)
            combobox_unit.current(1)
            e_serial.set(0)
        # print(rs)
        # print(rslt)
    tk.Button(canvas, text = '查找', width = 8, borderwidth = 3, font=('微软雅黑', 10, 'bold'), command = search).place(x=222, y=75)

    def update():
        p_partno = e_partno.get()
        p_descr = e_descr.get()
        p_unit = e_unit.get()
        p_min = e_min.get()
        p_max = e_max.get()
        p_warrenty = e_warrenty.get()
        p_supplier = e_supplier.get()
        p_invalid = e_invalid.get()
        p_shelf = e_shelf.get()
        p_serial = e_serial.get()
        ret = run_oracle_function('update_parts', [p_partno, p_descr, p_unit, p_min, p_max, p_warrenty, p_supplier, p_invalid, p_shelf, p_serial, p_user])
        if ret == '0':
            tk.messagebox.showinfo('成功','物料信息更新成功！')
        elif ret == '2':
            tk.messagebox.showerror('错误', '物料号不存在')
        elif ret == '3':
            tk.messagebox.showerror('错误', '物料要求保质期管理，必须输入保质期（天数）')
        else:
            tk.messagebox.showerror('错误', '发生其他异常，请检查重试或者联系管理员')

    tk.Button(canvas, text = '更新', width = 8, borderwidth = 3, font=('微软雅黑', 10, 'bold'), command = update).place(x=422, y=75)

    def new():
        p_partno = e_partno.get()
        p_descr = e_descr.get()
        p_unit = e_unit.get()
        p_min = e_min.get()
        p_max = e_max.get()
        p_warrenty = e_warrenty.get()
        p_supplier = e_supplier.get()
        p_invalid = e_invalid.get()
        p_shelf = e_shelf.get()
        p_serial = e_serial.get()
        ret = run_oracle_function('create_parts',
                                  [p_partno, p_descr, p_unit, p_min, p_max, p_warrenty, p_supplier, p_invalid, p_shelf, p_serial,
                                   p_user])
        if ret == '0':
            tk.messagebox.showinfo('成功','新物料创建成功！')
        elif ret == '2':
            tk.messagebox.showerror('错误', '物料号已存在')
        elif ret == '3':
            tk.messagebox.showerror('错误', '物料要求保质期管理，必须输入保质期（天数）')
        else:
            tk.messagebox.showerror('错误', '发生其他异常，联系系统管理员')

    tk.Button(canvas, text = '新增', width = 8, borderwidth = 3, font=('微软雅黑', 10, 'bold'), command = new).place(x=552, y=75)

    x0, y0, y_sep, wid = 0, 0, 36, 20

    e_partno = tk.StringVar()
    tk.Entry(canvas, textvariable=e_partno, width=wid, font=('微软雅黑', 12)).place(x=160+x0, y=132+y0)
    e_descr = tk.StringVar()
    tk.Entry(canvas, textvariable=e_descr, width=wid, font=('微软雅黑', 12)).place(x=160+x0, y=132+y0+1*y_sep)
    e_unit = tk.StringVar()
    combobox_unit = ttk.Combobox(canvas, width = wid, textvariable = e_unit, font=('微软雅黑', 10))
    combobox_unit.place(x=160+x0, y=132+y0+2*y_sep)
    combobox_unit['values'] = ['其他', '个', '瓶', '桶']
    combobox_unit.current(1)
    e_min = tk.StringVar()
    tk.Entry(canvas, textvariable=e_min, width=wid, font=('微软雅黑', 12)).place(x=160+x0, y=132+y0+3*y_sep)
    e_max = tk.StringVar()
    tk.Entry(canvas, textvariable=e_max, width=wid, font=('微软雅黑', 12)).place(x=160+x0, y=132+y0+4*y_sep)
    e_shelf = tk.IntVar()
    tk.Checkbutton(canvas, variable=e_shelf).place(x=160 + x0, y=132 + y0 + 5 * y_sep)
    e_shelf.set(1) # add by Chauncey in version 0.5, default set the shelf life management flag.
    e_warrenty = tk.StringVar()
    tk.Entry(canvas, textvariable=e_warrenty, width=wid, font=('微软雅黑', 12)).place(x=160+x0, y=132+y0+6*y_sep)
    e_supplier = tk.StringVar()
    tk.Entry(canvas, textvariable=e_supplier, width=wid, font=('微软雅黑', 12)).place(x=160+x0, y=132+y0+7*y_sep)
    e_serial = tk.IntVar()
    tk.Checkbutton(canvas, variable=e_serial).place(x=160 + x0, y=132 + y0 + 8 * y_sep)
    e_invalid = tk.IntVar()
    tk.Checkbutton(canvas, variable = e_invalid).place(x=160+x0, y=132+y0+9*y_sep)


    label_user = tk.Label(canvas, text=' 当前登录用户：' + p_user + ' ',
                          font=('微软雅黑', 10, 'bold italic')).place(x=20, y=860, anchor='nw')
    gm.mainloop()

if __name__ == '__main__':
    goods_maintenance('TEST')