import pandas as pd
import cx_Oracle as cx
import tkinter as tk
import datetime
from tkinter import messagebox

# tns = cx.makedsn('npc.che.volvocars.net', 49957, sid = 'DPQ')
# db = cx.connect('cip_sys', 'cip_sys1', tns, encoding = "UTF-8", nencoding = "UTF-8")
# cur = db.cursor()
# cur.close()
# db.close()

w = tk.Tk()
w.geometry('450x80+400+300')
w.title("抓取过注册点记录，很危险，不要说是我做的。。。")
w.resizable(0, 0)

l1 = tk.Label(w, text = 'Date time:    格式为YYYY/MM/DD HH24:MI:SS', font = ('微软雅黑', 12, 'bold')).place(x=0, y=0)
l2 = tk.Label(w, text = '开始：', font = ('微软雅黑')).place(x=5, y=25)
l3 = tk.Label(w, text = '结束：', font = ('微软雅黑')).place(x=180, y=25)
t_start = tk.StringVar()
t_end = tk.StringVar()
e2 = tk.Entry(w, textvariable = t_start, width = 17, font = ('微软雅黑', 10)).place(x=5, y=50)
e3 = tk.Entry(w, textvariable = t_end, width = 17, font = ('微软雅黑', 10)).place(x=180, y=50)
t_start.set('2020/01/01 00:00:00')
t_end.set(datetime.datetime.now().strftime('%Y/%m/%d')+' 23:59:59')

sql = '''
select tcp715.tagid, tcp010.iincd, tcp010.oincd, TCP716.DBREG, tcp715.IBODY, tcp715.IMODELJ, tcp715.RBODY, tcp715.KSURF, tcp715.KKLEUR, tcp715.RVERFLEV, tcp715.FLOCK, tcp715.ifyon, tcp715.IBTGB, tcp715.KKOPORD, tcp715.IFAZE, tcp715.FBUFWAGEN, tcp715.KKLEURCC, tcp715.KKOPVAST from tcp716
left join tcp715 on tcp716.NIDTCP715 = tcp715.NIDTCP715 left join tcp010 on tcp716.nidtcp010 = tcp010.NIDTCP010
where tcp716.DBREG between to_date('{}','YYYY/MM/DD HH24:MI:SS') and to_date('{}','YYYY/MM/DD HH24:MI:SS') order by tcp716.DBREG desc
'''

def click():
    try:
        tns = cx.makedsn('npc.che.volvocars.net', 49957, sid='DPQ')
        db = cx.connect('cip_sys', 'cip_sys1', tns, encoding="UTF-8", nencoding="UTF-8")
        cur = db.cursor()
        sql_run = sql.format(t_start.get(), t_end.get())
        # print(sql_run)
        cur.execute(sql_run)
        rs = cur.fetchall()
        df = pd.DataFrame(rs)
        df.columns = ['TAGID','REG POINT','REG DESCR','REG TIME','BODY NUMBER','MODEL YEAR','BODY TYPE','KSURF','KKLEUR','RVERFLEV','FLOCK','FYON NUMBER','BTGB NUMBER','KKOPORD','IFAZE','FBUFWAGEN','KKLEURCC','KKOPVAST']
        filename = 'Reg_history_' + datetime.datetime.now().strftime('%Y%m%d%H%M%S') + '.xlsx'
        writer = pd.ExcelWriter(filename)
        df.to_excel(writer, index=False)
        writer.save()
        tk.messagebox.showinfo('Success', 'Generate excel file: {} successfully!'.format(filename))
    except:
        tk.messagebox.showerror('Error', 'Exception happens when getting data from database or generate excel file.')
    finally:
        cur.close()
        db.close()


b_click = tk.Button(w, text = '走起！', font = ('微软雅黑', 14, 'bold'), command = click)
b_click.place(x=350, y=30)

w.mainloop()























