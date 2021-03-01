import tkinter as tk
from GR_1 import GR_1
from stock_movement import stock_movement
from report_direct_export import stock_report
from report_direct_export import stock_aging
from report_direct_export import transaction_history
from report_direct_export import shelf_life_report
from GI_1 import gi_1
from manual_QR import manual_qr
from stock_report_detail import tbd1

def fc_choose(p_user, p_hostname, p_ip):
    fc_page = tk.Tk()
    fc_page.geometry('600x350+600+300')
    fc_page.title('Function selection')
    fc_page.resizable(0,0)

    # attach image
    canvas = tk.Canvas(fc_page, width = 600, height = 350, highlightthickness = 0, borderwidth = 0)
    image_file = tk.PhotoImage(file='function.gif')
    image = canvas.create_image(0,0, anchor='nw', image=image_file)
    canvas.place(x = 0, y = 0, anchor = 'nw')

    # define general offset to adjust the button position
    x0 = 20
    y0 = 10

    # GR scanning button
    def gr_scanning():
        # fc_page.destroy()
        fc_page.iconify()
        GR_1(p_user, p_hostname, p_ip)


    b1 = tk.Button(canvas, text = 'GR Scanning', width = 18, font = ('Calibri', 10, 'bold'), command = gr_scanning)
    b1.place(x = 30+x0, y = 100+y0)

    # Stock movement button
    def stock_movement_choose():
        # fc_page.destroy()
        fc_page.iconify()
        stock_movement(p_user)

    b2 = tk.Button(canvas, text = 'Stock Movement', width = 18, font = ('Calibri', 10, 'bold'), command = stock_movement_choose)
    b2.place(x = 30+x0, y = 150+y0)

    # GI scanning button
    def gi_scanning():
        fc_page.iconify()
        gi_1(p_user)

    b3 = tk.Button(canvas, text = 'GI Scanning', width = 18, font = ('Calibri', 10, 'bold'), command = gi_scanning)
    b3.place(x = 30+x0, y = 200+y0)

    # Stock Adjustment
    def stock_adjustment():
        pass

    b4 = tk.Button(canvas, text = 'Stock Adjustment', width = 18, font = ('Calibri', 10, 'bold'), command = stock_adjustment)
    b4.place(x = 30+x0, y = 250+y0)

    # Real-time Stock Report
    def stock_report_choose():
        stock_report(p_user)

    b5 = tk.Button(canvas, text = 'Real-time Stock Report', width = 18, font = ('Calibri', 10, 'bold'), command = stock_report_choose)
    b5.place(x = 210+x0, y = 100+y0)


    # Stock Aging Report
    def stock_aging_report():
        stock_aging(p_user)

    b6 = tk.Button(canvas, text = 'Stock Aging Report', width = 18, font = ('Calibri', 10, 'bold'), command = stock_aging_report)
    b6.place(x = 210+x0, y = 150+y0)

    # Transaction History
    def transaction_history_choose():
        transaction_history(p_user)

    b7 = tk.Button(canvas, text = 'Transaction History', width = 18, font = ('Calibri', 10, 'bold'), command = transaction_history_choose)
    b7.place(x = 210+x0, y = 200+y0)

    # Shelf Life Report
    def shelf_life():
        shelf_life_report(p_user)

    b8 = tk.Button(canvas, text = 'Shelf Life Report', width = 18, font = ('Calibri', 10, 'bold'), command = shelf_life)
    b8.place(x = 210+x0, y = 250+y0)

    # # Reverse Operation
    # def reverse_operation():
    #     pass
    #
    # b9 = tk.Button(canvas, text = 'Reverse Operation', width = 18, font = ('Calibri', 10, 'bold'), command = reverse_operation)
    # b9.place(x = 390+x0, y = 200+y0)

    # Manully QR Generation
    def manually_qr_generation():
        fc_page.iconify()
        manual_qr(p_user)
    b9 = tk.Button(canvas, text='Manully QR Generation', width=18, font=('Calibri', 10, 'bold'), command=manually_qr_generation)
    b9.place(x=390 + x0, y=100 + y0)

    # TBD1
    def tbd_choose():
        fc_page.iconify()
        tbd1()
    b10 = tk.Button(canvas, text='TBD1', width=18, font=('Calibri', 10, 'bold'), command=tbd_choose)
    b10.place(x=390 + x0, y=150 + y0)

    # TBD2
    b11 = tk.Button(canvas, text='TBD2', width=18, font=('Calibri', 10, 'bold'), command=None)
    b11.place(x=390 + x0, y=200 + y0)

    # TBD3
    b12 = tk.Button(canvas, text='TBD3', width=18, font=('Calibri', 10, 'bold'), command=None)
    b12.place(x=390 + x0, y=250 + y0)


    label_user = tk.Label(canvas, text=' Current Login User: ' + p_user + ' ',
                          font=('Calibri', 10, 'bold italic')).place(x=20, y=320, anchor='nw')

    fc_page.mainloop()

if __name__ == '__main__':
    fc_choose('TEST', '5CG94599LK', '10.234.34.178')