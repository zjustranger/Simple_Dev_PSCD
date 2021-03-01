import tkinter as tk
from QRcode import manual_generate_QR_code
from tkinter import messagebox

def manual_qr(p_user):
    m_qr = tk.Toplevel()
    m_qr.geometry('600x733+600+150')
    m_qr.title('Manual QR Generation')
    m_qr.resizable(0, 0)

    # attach image
    canvas = tk.Canvas(m_qr, width=600, height=733, highlightthickness=0, borderwidth=0)
    image_file = tk.PhotoImage(file='manual_qr.gif')
    image = canvas.create_image(0, 0, anchor='nw', image=image_file)
    canvas.place(x=0, y=0, anchor='nw')

    x0, y0 = 0, 0       # pqvnsmd

    l_p = tk.Label(canvas, text='{:20}'.format('Part Number:'), width = 20, font=('Calibri', 15)).place(x=40+x0, y=170+y0)
    e_p_content = tk.StringVar()
    e_p = tk.Entry(canvas, textvariable=e_p_content, width=26, font=('Calibri', 16))
    e_p.place(x=260+x0, y=170+y0)

    l_q = tk.Label(canvas, text='{:20}'.format('Quantity:'), width = 20, font=('Calibri', 15)).place(x=40+x0, y=220+y0)
    e_q_content = tk.StringVar()
    e_q = tk.Entry(canvas, textvariable=e_q_content, width=26, font=('Calibri', 16))
    e_q.place(x=260+x0, y=220+y0)

    l_v = tk.Label(canvas, text='{:20}'.format('Supplier:'), width = 20, font=('Calibri', 15)).place(x=40+x0, y=270+y0)
    e_v_content = tk.StringVar()
    e_v = tk.Entry(canvas, textvariable=e_v_content, width=26, font=('Calibri', 16))
    e_v.place(x=260+x0, y=270+y0)

    l_n = tk.Label(canvas, text='{:20}'.format('Dispatch Note:'), width = 20, font=('Calibri', 15)).place(x=40+x0, y=320+y0)
    e_n_content = tk.StringVar()
    e_n = tk.Entry(canvas, textvariable=e_n_content, width=26, font=('Calibri', 16))
    e_n.place(x=260+x0, y=320+y0)

    l_s = tk.Label(canvas, text='{:20}'.format('Serial Number:'), width = 20, font=('Calibri', 15)).place(x=40+x0, y=370+y0)
    e_s_content = tk.StringVar()
    e_s = tk.Entry(canvas, textvariable=e_s_content, width=26, font=('Calibri', 16))
    e_s.place(x=260+x0, y=370+y0)

    l_m = tk.Label(canvas, text='{:20}'.format('Manufacturing Date:'), width = 20, font=('Calibri', 15)).place(x=40+x0, y=420+y0)
    e_m_content = tk.StringVar()
    e_m = tk.Entry(canvas, textvariable=e_m_content, width=26, font=('Calibri', 16))
    e_m.place(x=260+x0, y=420+y0)

    l_d = tk.Label(canvas, text='{:20}'.format('Due Date:'), width = 20, font=('Calibri', 15)).place(x=40+x0, y=470+y0)
    e_d_content = tk.StringVar()
    e_d = tk.Entry(canvas, textvariable=e_d_content, width=26, font=('Calibri', 16))
    e_d.place(x=260+x0, y=470+y0)

    def generate():
        if e_p_content.get() and e_s_content.get() and e_q_content.get():
            manual_generate_QR_code(e_p_content.get(), e_q_content.get(), e_v_content.get(), e_n_content.get(), e_s_content.get(), e_m_content.get(), e_d_content.get(), p_user)
            tk.messagebox.showinfo('Success', 'QR label generated successfully under \\newlabels directory.')
        else:
            tk.messagebox.showerror('Error', 'Error. Part number, serial number, qty are mandatory fields.')

    b_generate = tk.Button(canvas, text = 'Generate', font=('Calibri', 15), command = generate)
    b_generate.place(x=420, y= 590)

    label_user = tk.Label(canvas, text=' Current Login User: ' + p_user + ' ',
                          font=('Calibri', 12, 'bold italic')).place(x=20, y=700, anchor='nw')

    m_qr.mainloop()


if __name__ == '__main__':
    manual_qr('TEST')
