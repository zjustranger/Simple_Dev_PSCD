import tkinter as tk
from tkinter import ttk
import os
from time import sleep
from DB_Connection import get_sninfo_from_scanning
from DB_Connection import run_oracle_function
from tkinter import messagebox

def stock_status_change(p_user):
    pic_dir = os.getcwd() + '\\' + 'pics' + '\\'
    ssc_page = tk.Toplevel()
    ssc_page.iconbitmap(pic_dir + 'doge.ico')
    ssc_page.geometry('675x478+350+150')
    ssc_page.title('库存状态变更--序列号管理物料')
    ssc_page.resizable(0, 0)

    # attach image
    canvas = tk.Canvas(ssc_page, width=675, height=478, highlightthickness=0, borderwidth=0)
    image_file = tk.PhotoImage(file=pic_dir + 'stock_status_change.gif')
    image = canvas.create_image(0, 0, anchor='nw', image=image_file)
    canvas.place(x=0, y=0, anchor='nw')

    # entry for QR label
    label_content = tk.StringVar()
    e_label = tk.Entry(canvas, textvariable=label_content, width=42, font=('微软雅黑', 16))
    e_label.place(x = 130, y = 107)

    # define general offset to adjust the button position
    x0, y0, dy = 0, 0, 40
    bg, fg, wid = '#2b2b2b', '#FFFFFF', 40

    # labels to display scanning result.
    l_sn = tk.StringVar()
    tk.Label(canvas, textvariable = l_sn, bg=bg, fg=fg, anchor = 'w', width = wid, font=('微软雅黑', 12)).place(x=200+x0,y=200+y0+0*dy)
    l_partno = tk.StringVar()
    tk.Label(canvas, textvariable = l_partno, bg=bg, fg=fg, anchor = 'w', width = wid, font=('微软雅黑', 12)).place(x=200+x0,y=200+y0+1*dy)
    l_partdesc = tk.StringVar()
    tk.Label(canvas, textvariable=l_partdesc, bg=bg, fg=fg, anchor='w', width=wid, font=('微软雅黑', 12)).place(x=200+x0,y=200+y0+2*dy)
    l_status = tk.StringVar()
    tk.Label(canvas, textvariable=l_status, bg=bg, fg=fg, anchor='w', width=wid, font=('微软雅黑', 12)).place(x=200+x0,y=200+y0+3*dy)
    to_status = tk.StringVar()
    combobox_status = ttk.Combobox(canvas, width = 6, textvariable = to_status, font=('微软雅黑', 15))
    combobox_status.place(x=400, y=400)
    combobox_status['values'] = ['正常', '待检查', '待维修']

    def confirm():
        global p_sn
        go_next = tk.messagebox.askyesno('提示', '要更改状态为：{0}吗？'.format(to_status.get()))
        if go_next:
            ret = run_oracle_function('change_stock_status', [p_sn, to_status.get(), p_user])
            if ret == '0':
                tk.messagebox.showinfo('成功', '状态更新成功！')
            elif ret == '1':
                tk.messagebox.showerror('错误', '未读取到序列号信息')
            else:
                tk.messagebox.showerror('错误', '其他异常，联系管理员')
            l_sn.set('')
            l_partno.set('')
            l_partdesc.set('')
            l_status.set('')
            to_status.set('')
        else:
            pass
    tk.Button(canvas, text = '确定', width = 8, font=('微软雅黑', 11, 'bold'), command = confirm).place(x=520, y=401)

    def send_scanning(arg1):
        global p_sn, p_partno, p_descr, p_status
        p_sn, p_partno, p_descr, p_status = get_sninfo_from_scanning(e_label.get())
        l_sn.set(p_sn)
        l_partno.set(p_partno)
        l_partdesc.set(p_descr)
        l_status.set(p_status)
        sleep(0.2)
        label_content.set('')
    e_label.bind('<Return>', send_scanning)

    label_user = tk.Label(canvas, text=' 当前登录用户：' + p_user + ' ',
                              font=('微软雅黑', 10, 'bold italic')).place(x=20, y=440, anchor='nw')
    ssc_page.mainloop()


if __name__ == '__main__':
    stock_status_change('TEST')