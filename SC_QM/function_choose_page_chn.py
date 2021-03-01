import tkinter as tk
from GR_1_chn import GR_1
from stock_movement_chn import stock_movement
from report_direct_export import stock_report
from report_direct_export import stock_aging
from GI_1_chn import gi_1
from manual_QR_chn import manual_qr
from stock_report_detail_chn import stock_detail
from goods_maintenance_chn import goods_maintenance
from location_structure_chn import location_structure
from stock_adjustment1 import stock_adjustment1
from transaction_history import transaction_history
from shelf_life_query import shelf_life_query
import os

def fc_choose(p_user, p_hostname, p_ip):
    pic_dir = os.getcwd() + '\\' + 'pics' + '\\'
    fc_page = tk.Tk()
    fc_page.iconbitmap(pic_dir+'doge.ico')
    fc_page.geometry('1200x700+350+150')
    fc_page.title('功能选择')
    fc_page.resizable(0,0)

    # attach image
    canvas = tk.Canvas(fc_page, width = 1200, height = 700, highlightthickness = 0, borderwidth = 0)
    image_file = tk.PhotoImage(file=pic_dir+'function_chn.gif')
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


    b1 = tk.Button(canvas, text = '入库扫描', width = 18, font = ('微软雅黑', 11, 'bold'), command = gr_scanning)
    b1.place(x = 125+x0, y = 200+y0)

    # Stock movement button
    def stock_movement_choose():
        # fc_page.destroy()
        fc_page.iconify()
        stock_movement(p_user)

    b2 = tk.Button(canvas, text = '库存移动', width = 18, font = ('微软雅黑', 11, 'bold'), command = stock_movement_choose)
    b2.place(x = 125+x0, y = 280+y0)

    # GI scanning button
    def gi_scanning():
        fc_page.iconify()
        gi_1(p_user)

    b3 = tk.Button(canvas, text = '出库扫描', width = 18, font = ('微软雅黑', 11, 'bold'), command = gi_scanning)
    b3.place(x = 125+x0, y = 360+y0)

    # Stock Adjustment
    def stock_adjustment():
        fc_page.iconify()
        stock_adjustment1(p_user)

    b4 = tk.Button(canvas, text = '库存调整（部分完成）', width = 18, font = ('微软雅黑', 11, 'bold'), command = stock_adjustment)
    b4.place(x = 125+x0, y = 440+y0)

    # stock_detail_UI
    def stock_detail_choose():
        fc_page.iconify()
        stock_detail(p_user)
    b5 = tk.Button(canvas, text='库存查询界面', width=18, font=('微软雅黑', 11, 'bold'), command=stock_detail_choose)
    b5.place(x= 483 + x0, y=200 + y0)

    # Transaction History
    def transaction_history_choose():
        fc_page.iconify()
        transaction_history(p_user)

    b6 = tk.Button(canvas, text = '事务历史查询', width = 18, font = ('微软雅黑', 11, 'bold'), command = transaction_history_choose)
    b6.place(x = 483+x0, y = 280+y0)

    # Shelf Life Report
    def shelf_life():
        fc_page.iconify()
        shelf_life_query(p_user)

    b7 = tk.Button(canvas, text = '保质期查询', width = 18, font = ('微软雅黑', 11, 'bold'), command = shelf_life)
    b7.place(x = 483+x0, y = 360+y0)

    # Real-time Stock Report
    def stock_report_choose():
        stock_report(p_user)

    b8 = tk.Button(canvas, text = '实时库存报表（导出）', width = 18, font = ('微软雅黑', 11, 'bold'), command = stock_report_choose)
    b8.place(x = 483+x0, y = 440+y0)


    # Stock Aging Report
    def stock_aging_report():
        stock_aging(p_user)

    b9 = tk.Button(canvas, text = '库龄报表（导出）', width = 18, font = ('微软雅黑', 11, 'bold'), command = stock_aging_report)
    b9.place(x = 483+x0, y = 520+y0)

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
    b10 = tk.Button(canvas, text='手动生成二维码', width=18, font=('微软雅黑', 11, 'bold'), command=manually_qr_generation)
    b10.place(x=838 + x0, y=200 + y0)


    # Goods Maintenance
    def goods_maintain():
        fc_page.iconify()
        goods_maintenance(p_user)
    b11 = tk.Button(canvas, text='物料属性维护', width=18, font=('微软雅黑', 11, 'bold'), command=goods_maintain)
    b11.place(x=838 + x0, y=280 + y0)

    # Location maintenance
    def location_structure_page():
        fc_page.iconify()
        location_structure(p_user)
    b12 = tk.Button(canvas, text='库位结构维护', width=18, font=('微软雅黑', 11, 'bold'), command=location_structure_page)
    b12.place(x=838 + x0, y=360 + y0)


    label_user = tk.Label(canvas, text=' 当前登录用户：' + p_user + ' ',
                          font=('微软雅黑', 10, 'bold italic')).place(x=20, y=670, anchor='nw')

    fc_page.mainloop()

if __name__ == '__main__':
    fc_choose('TEST', '5CG94599LK', '10.234.34.178')