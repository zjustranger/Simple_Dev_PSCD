import tkinter as tk
from time import sleep
from tkinter import messagebox
from DB_Connection import get_feedback_from_scanning
from DB_Connection import get_best_suggestion_package
from DB_Connection import run_oracle_function
import os

def gi_1(p_user):
    pic_dir = os.getcwd() + '\\' + 'pics' + '\\'
    gi_1 = tk.Toplevel()
    gi_1.iconbitmap(pic_dir+'doge.ico')
    gi_1.geometry('1200x700+350+150')
    gi_1.title('出库扫描')
    gi_1.resizable(0,0)

    # attach image
    canvas = tk.Canvas(gi_1, width = 1200, height = 700, highlightthickness = 0, borderwidth = 0)
    image_file = tk.PhotoImage(file=pic_dir+'GI_1_chn.gif')
    image = canvas.create_image(0,0, anchor='nw', image=image_file)
    canvas.place(x = 0, y = 0, anchor = 'nw')

    label_content = tk.StringVar()
    e = tk.Entry(canvas, textvariable=label_content, width=84, font=('Calibri', 16))
    e.place(x=230, y=168)

    def send_scanning(arg):
        global p_partno, p_qty, p_supplier, p_dn, p_sn, p_bn, p_md, p_dd, p_loc_id, p_parent_sn
        p_partno, p_qty, p_supplier, p_dn, p_sn, p_bn, p_md, p_dd, p_loc_id, p_parent_sn = get_feedback_from_scanning(
            label_content.get())
        show_package_info = ''
        if p_qty != 0:
            show_package_info = "包装序列号：{}。批次号：{}。处于库存位置：{}。数量：{}。\n默认出库数量已设置为包装总数量。其他信息和建议如下：".format(p_sn, p_bn, p_loc_id, p_qty)
            if p_parent_sn:
                show_package_info = show_package_info + '\n此包装是一个子包，拆分自' + p_parent_sn + '。'

            try:
                p_match_code, p_chem_flag, p_best_sn, p_out_loc, p_out_qty, p_out_dd = get_best_suggestion_package(p_sn)
            except:
                p_match_code = 1

            # add comments here.
            if p_match_code == 0:
                show_package_info = show_package_info + '\n这个包装是最优出库选择了！'
            elif p_match_code == 2:
                show_package_info = show_package_info + '\n这个物料号不做保质期管理，但是存在更小的包装：{0}\n位于库位：{1}，数量为：{2}。可以考虑先出这个包装。'.format(p_best_sn, p_out_loc, p_out_qty)
            elif p_match_code == 3:
                show_package_info = show_package_info + '\n这个物料号不做保质期管理，但是存在更早入库的包装：{0}\n位于库位：{1}。数量为：{2}。可以考虑先出这个包装。'.format(p_best_sn, p_out_loc, p_out_qty)
            elif p_match_code == 6:
                show_package_info = show_package_info + '\n这个物料号要求保质期管理，存在更早过期的包装：{0}\n位于库位：{1}。数量为：{2}。可以考虑先出这个包装。'.format(p_best_sn, p_out_loc, p_out_qty)
            elif p_match_code == 7:
                show_package_info = show_package_info + '\n这个物料号要求保质期管理，存在更早入库的包装：{0} \n位于库位：{1}。数量为：{2}。可以考虑先出这个包装。'.format(p_best_sn, p_out_loc, p_out_qty)
            elif p_match_code == 8:
                show_package_info = show_package_info + '\n这个物料号要求保质期管理，存在更小的包装：{0} \n位于库位：{1}。数量为：{2}。可以考虑先出这个包装。'.format(p_best_sn, p_out_loc, p_out_qty)
            elif p_match_code == 9:
                show_package_info = show_package_info + '\n这个包装状态异常，不能出库。'
            else:
                show_package_info = show_package_info + '\n在系统查找最优出库包装时发生异常，无法提供建议。'

            l_show_content.set(show_package_info)
            l_show.config(fg='green')
            e_issue_qty.set(p_qty)
        else:
            show_package_info = "没有找到当前包装信息！\n它是不是还没收货入库或者已经全部出库完成了？"
            l_show_content.set(show_package_info)
            l_show.config(fg='red')
        sleep(0.2)
        label_content.set('')


    e.bind('<Return>', send_scanning)

    l_show_content = tk.StringVar()
    l_show_content.set(p_user + '，欢迎！现在扫描二维码，获取包装信息。')
    l_show = tk.Label(canvas, textvariable=l_show_content, width = 86, justify = tk.LEFT, font=('微软雅黑', 15, 'bold'))
    l_show.place(x=40, y=280)

    x0, y0 = 80, -80
    e_issue_qty = tk.StringVar()
    e_issue = tk.Entry(canvas, textvariable = e_issue_qty, width = 12, font=('Calibri', 16))
    e_issue.place(x=800+x0, y=660+y0)

    def confirm_issue():
        global p_sn, p_partno, p_qty
        issue_qty = eval(e_issue_qty.get())
        go_next = tk.messagebox.askyesno('提示',
                                         '你选择了出库包装：{0}，物料号为：{1}，数量为：{2}'.format(p_sn, p_partno, issue_qty) + '。确定出库？')
        if go_next:
            l_show_content.set("正在出库...")
            if p_sn and issue_qty and p_user:
                if issue_qty > p_qty or issue_qty <= 0:
                    tk.messagebox.showerror('错误', "出库数量不正确。")
                else:
                    retVar = run_oracle_function('goods_issue',
                                                 [p_sn, issue_qty, p_user])
                    print(retVar)
                    if retVar == '0':
                        tk.messagebox.showinfo('成功', '出库操作完成！')
                        l_show_content.set('扫描下一个需要出库的包装二维码')
                        label_content.set('')
                        e_issue_qty.set('')
                    else:
                        tk.messagebox.showerror('错误', '出库异常。联系系统管理员。')
            else:
                tk.messagebox.showerror('错误', '出库信息不完整！')
        else:
            pass


    b = tk.Button(canvas, text = '出库', width = 10, font=('微软雅黑', 10, 'bold'), command = confirm_issue).place(x= 950+x0, y=660+y0)

    label_user = tk.Label(canvas, text=' 当前登录用户：' + p_user + ' ',
                          font=('微软雅黑', 10, 'bold italic')).place(x=20, y=650, anchor='nw')
    gi_1.mainloop()


if __name__ == '__main__':
    gi_1('TEST')