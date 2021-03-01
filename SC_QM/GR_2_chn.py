import tkinter as tk
from DB_Connection import gr_scanning
from time import sleep
import os

def GR_2(p_user, p_hostname, p_ip, p_loc_id):
    pic_dir = os.getcwd() + '\\' + 'pics' + '\\'
    gr_2 = tk.Toplevel()
    gr_2.iconbitmap(pic_dir + 'doge.ico')
    gr_2.geometry('1200x700+350+150')
    gr_2.title('入库扫描')
    gr_2.resizable(0, 0)

    # attach image
    canvas = tk.Canvas(gr_2, width=1200, height=700, highlightthickness=0, borderwidth=0)
    image_file = tk.PhotoImage(file=pic_dir + 'GR_2_chn.gif')
    image = canvas.create_image(0, 0, anchor='nw', image=image_file)
    canvas.place(x=0, y=0, anchor='nw')

    label_content = tk.StringVar()
    e = tk.Entry(canvas, textvariable=label_content, width=90, font=('Calibri', 16))
    e.place(x=83, y=180)
    e.focus_set()
    gr_result = tk.StringVar()
    l_result = tk.Label(canvas, textvariable = gr_result, font = ('微软雅黑', 15, 'bold'))
    l_result.place(x=83, y=220)

    def send_gr(arg1):
        # print(arg1)
        retVar = gr_scanning(label_content.get(), p_user, p_hostname, p_ip, p_loc_id)
        sleep(0.5)
        label_content.set('')
        if retVar == 0:
            l_result.config(fg = 'green')
            gr_result.set('入库成功！')
        elif retVar == 2:
            l_result.config(fg = 'red')
            gr_result.set('入库失败：物料号异常。')
        elif retVar == 3:
            l_result.config(fg = 'red')
            gr_result.set('入库失败：没有供应商信息。')
        elif retVar == 4:
            l_result.config(fg = 'red')
            gr_result.set('入库失败：物料号和供应商信息不匹配。')
        elif retVar == 5:
            l_result.config(fg = 'red')
            gr_result.set('入库失败：此供应商信息未维护。')
        elif retVar == 6:
            l_result.config(fg = 'red')
            gr_result.set('入库失败：此物料要求保质期管理，但标签没有任何有效日期信息。')
        elif retVar == 7:
            l_result.config(fg = 'red')
            gr_result.set('入库失败：标签没有序列号信息。')
        elif retVar == 8:
            l_result.config(fg = 'red')
            gr_result.set('入库失败：重复的标签序列号，已经完成扫描入库。')
        elif retVar == 9:
            l_result.config(fg = 'red')
            gr_result.set('入库失败：物料要求序列号管理，只能以单个数量收货，标签数量不为1。')
        else:
            l_result.config(fg = 'red')
            gr_result.set('入库失败：其他异常，联系系统管理员。')

    # b = tk.Button(canvas, text = 'Confirm', font = ('Calibri', 12), command = send_gr).place(x = 500, y = 160)
    e.bind('<Return>', send_gr)
    e.focus_set()

    label_user = tk.Label(canvas, text=' 当前登录用户：' + p_user + ' ',
                          font=('微软雅黑', 10, 'bold italic')).place(x=20, y=650, anchor='nw')

    gr_2.mainloop()


if __name__ == '__main__':
    GR_2('TEST', '5CG94599LK', '10.234.34.178', 'IT_TEMP_AREA_1')