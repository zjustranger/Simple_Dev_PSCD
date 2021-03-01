import tkinter as tk
import os
from stock_status_change import stock_status_change

def stock_adjustment1(p_user):
    pic_dir = os.getcwd() + '\\' + 'pics' + '\\'
    sac_page = tk.Toplevel()
    sac_page.iconbitmap(pic_dir + 'doge.ico')
    sac_page.geometry('1200x700+350+150')
    sac_page.title('库存调整')
    sac_page.resizable(0, 0)

    # attach image
    canvas = tk.Canvas(sac_page, width=1200, height=700, highlightthickness=0, borderwidth=0)
    image_file = tk.PhotoImage(file=pic_dir + 'stock_adjustment1.gif')
    image = canvas.create_image(0, 0, anchor='nw', image=image_file)
    canvas.place(x=0, y=0, anchor='nw')

    # define general offset to adjust the button position
    x0, y0 = 0, 0

    # Serial No status change button
    def stock_status_change_choose():
        # sac_page.iconify()
        sac_page.destroy()
        stock_status_change(p_user)


    b1 = tk.Button(canvas, text='库存状态调整--序列号管理物料', width=25, font=('微软雅黑', 11, 'bold'), command=stock_status_change_choose)
    b1.place(x=180 + x0, y=210 + y0)

    label_user = tk.Label(canvas, text=' 当前登录用户：' + p_user + ' ',
                              font=('微软雅黑', 10, 'bold italic')).place(x=20, y=670, anchor='nw')
    sac_page.mainloop()


if __name__ == '__main__':
    stock_adjustment1('TEST')