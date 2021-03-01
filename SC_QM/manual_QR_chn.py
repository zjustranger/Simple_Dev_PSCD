import tkinter as tk
from QRcode import manual_generate_qr_code_new
from tkinter import messagebox
import os
from DB_Connection import run_select_sql

def manual_qr(p_user):
    pic_dir = os.getcwd() + '\\' + 'pics' + '\\'
    m_qr = tk.Toplevel()
    m_qr.iconbitmap(pic_dir+'doge.ico')
    m_qr.geometry('600x733+600+150')
    m_qr.title('手动生成二维码')
    m_qr.resizable(0,0)

    # attach image
    canvas = tk.Canvas(m_qr, width=600, height=733, highlightthickness=0, borderwidth=0)
    image_file = tk.PhotoImage(file=pic_dir+'manual_qr_chn.gif')
    image = canvas.create_image(0, 0, anchor='nw', image=image_file)
    canvas.place(x=0, y=0, anchor='nw')

    x0, y0, dy = -30, -40, 45       # pqvnsmd
    font1 = ('微软雅黑', 15)
    width1 = 25

    e_p_content = tk.StringVar()
    e_p = tk.Entry(canvas, textvariable=e_p_content, width=width1, font=font1)
    e_p.place(x=260+x0, y=190+y0)

    e_q_content = tk.StringVar()
    e_q = tk.Entry(canvas, textvariable=e_q_content, width=width1, font=font1)
    e_q.place(x=260+x0, y=190+y0+dy)

    e_d_content = tk.StringVar()
    e_d = tk.Entry(canvas, textvariable=e_d_content, width=width1, font=font1)
    e_d.place(x=260+x0, y=190+y0+2*dy)

    # e_v_content = tk.StringVar()
    # e_v = tk.Entry(canvas, textvariable=e_v_content, width=width1, font=font1)
    # e_v.place(x=260+x0, y=190+y0+2*dy)

    e_s_content = tk.StringVar()
    e_s = tk.Entry(canvas, textvariable=e_s_content, width=width1, font=font1)
    e_s.place(x=260+x0, y=190+y0+5*dy)

    e_b_content = tk.StringVar()
    e_b = tk.Entry(canvas, textvariable=e_b_content, width=width1, font=font1)
    e_b.place(x=260+x0, y=190+y0+6*dy)

    e_n_content = tk.StringVar()
    e_n = tk.Entry(canvas, textvariable=e_n_content, width=width1, font=font1)
    e_n.place(x=260+x0, y=190+y0+7*dy)

    # e_m_content = tk.StringVar()
    # e_m = tk.Entry(canvas, textvariable=e_m_content, width=width1, font=font1)
    # e_m.place(x=260+x0, y=190+y0+6*dy)



    def generate():
        if e_p_content.get() and e_q_content.get():
            try:
                rs = run_select_sql("select part_descr, supplier_id from parts where partno = '{}'".format(e_p_content.get()))
                descr = rs[0][0]
                v = rs[0][1]
            except:
                descr = ''
                v = 'DUMMY'
            if e_s_content.get().replace(' ','').replace('\n',''):
                sn = e_s_content.get().replace(' ','').replace('\n','')
            else:
                rs = run_select_sql("select label_seq.nextval from dual")
                sn = 'SYS{}'.format(rs[0][0])

            manual_generate_qr_code_new(e_p_content.get(), e_q_content.get(), v, e_n_content.get(), sn, e_b_content.get(), '', e_d_content.get(), descr, p_user)
            tk.messagebox.showinfo('成功', '二维码成功生成，已保存在程序目录下的“newlabels”子目录')
        else:
            tk.messagebox.showerror('错误', '物料号、数量为必填字段！')

    b_generate = tk.Button(canvas, text = '生成二维码', font=('微软雅黑', 15, 'bold'), command = generate)
    b_generate.place(x=420, y= 630)

    label_user = tk.Label(canvas, text=' 当前登录用户：' + p_user + ' ',
                          font=('微软雅黑', 10, 'bold italic')).place(x=20, y=700, anchor='nw')

    m_qr.mainloop()


if __name__ == '__main__':
    manual_qr('TEST')
