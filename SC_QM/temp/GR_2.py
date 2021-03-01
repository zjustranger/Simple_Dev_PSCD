import tkinter as tk
from DB_Connection import gr_scanning
from time import sleep


def GR_2(p_user, p_hostname, p_ip, p_loc_id):
    gr_2 = tk.Toplevel()
    gr_2.geometry('600x350+600+300')
    gr_2.title('GR Scanning')
    gr_2.resizable(0, 0)

    # attach image
    canvas = tk.Canvas(gr_2, width=600, height=350, highlightthickness=0, borderwidth=0)
    image_file = tk.PhotoImage(file='GR_2.gif')
    image = canvas.create_image(0, 0, anchor='nw', image=image_file)
    canvas.place(x=0, y=0, anchor='nw')

    l = tk.Label(canvas, text='Scanning Input:', font=('Calibri', 15)).place(x=40, y=120)
    label_content = tk.StringVar()
    e = tk.Entry(canvas, textvariable=label_content, width=50, font=('Calibri', 15))
    e.place(x=40, y=160)
    gr_result = tk.StringVar()
    l_result = tk.Label(canvas, textvariable = gr_result, font = ('Calibri', 12))
    l_result.place(x=40, y=200)

    def send_gr(arg1):
        # print(arg1)
        retVar = gr_scanning(label_content.get(), p_user, p_hostname, p_ip, p_loc_id)
        sleep(0.5)
        label_content.set('')
        if retVar == 0:
            l_result.config(fg = 'green')
            gr_result.set('GR Successfully!')
        elif retVar == 2:
            l_result.config(fg = 'red')
            gr_result.set('GR Failed: Part Number is invalid.')
        elif retVar == 3:
            l_result.config(fg = 'red')
            gr_result.set('GR Failed: No supplier info.')
        elif retVar == 4:
            l_result.config(fg = 'red')
            gr_result.set('GR Failed: Supplier and part number mismatch.')
        elif retVar == 5:
            l_result.config(fg = 'red')
            gr_result.set('GR Failed: Supplier master data not maintained.')
        elif retVar == 6:
            l_result.config(fg = 'red')
            gr_result.set('GR Failed: This part requires shelf life management but no any date info input.')
        elif retVar == 7:
            l_result.config(fg = 'red')
            gr_result.set('GR Failed: No Serial No.')
        elif retVar == 8:
            l_result.config(fg = 'red')
            gr_result.set('GR Failed: Duplicated Serial Number.')
        else:
            l_result.config(fg = 'red')
            gr_result.set('GR Failed: Other exception. Contact system administrator.')

    # b = tk.Button(canvas, text = 'Confirm', font = ('Calibri', 12), command = send_gr).place(x = 500, y = 160)
    e.bind('<Return>', send_gr)

    label_user = tk.Label(canvas, text=' Current Login User: ' + p_user + ' ',
                          font=('Calibri', 10, 'bold italic')).place(x=20, y=320, anchor='nw')

    gr_2.mainloop()


if __name__ == '__main__':
    GR_2('TEST', '5CG94599LK', '10.234.34.178', 'IT_TEMP_AREA_1')