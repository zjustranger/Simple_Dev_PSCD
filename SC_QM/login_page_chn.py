"""
用户登录页面信息
"""
import tkinter as tk
from tkinter import messagebox
import datetime
import socket
from function_choose_page_chn import fc_choose
from DB_Connection import run_select_sql
from DB_Connection import run_iud_sql
import os

app_version = 'Ver.1.1'

# 清理缓存文件
cur_dir = os.getcwd()
if not os.path.exists('temp'):
    os.mkdir('temp')
cur_dir_temp = cur_dir + '\\' + 'temp'
os.chdir(cur_dir_temp)
if os.path.exists('tempdata'):
    temp_dir = cur_dir_temp + '\\' + 'tempdata'
    os.chdir(temp_dir)
    for file in os.listdir():
        os.unlink(file)
else:
    os.mkdir('tempdata')
os.chdir(cur_dir)
pic_dir = cur_dir + '\\' + 'pics' + '\\'

hostname = socket.gethostname()
ip = socket.gethostbyname(hostname)

w_login = tk.Tk()
w_login.iconbitmap(pic_dir + 'doge.ico')
w_login.geometry('600x350+660+300')
w_login.title("PSCD危化品保质期管理系统" + '__' + app_version)
w_login.resizable(0, 0)

# welcome image
canvas = tk.Canvas(w_login, width=600, height=350, highlightthickness=0, borderwidth=0)
image_file = tk.PhotoImage(file=pic_dir + 'login.gif')
image = canvas.create_image(0, 0, anchor='nw', image=image_file)
canvas.place(x=0, y=0, anchor='nw')

# user_name & password labels and entries, define 2 vars to quick adjust the login set location
x0, y0 = 150, 0
var_user_name = tk.StringVar()
e_user_name = tk.Entry(canvas, width=14, textvariable=var_user_name)
e_user_name.place(x=90 + x0, y=80 + y0, anchor='nw')
var_password = tk.StringVar()
e_password = tk.Entry(canvas, width=14, textvariable=var_password, show='*')
e_password.place(x=290 + x0, y=80 + y0, anchor='nw')


# login, signup, exit button
def usr_login(*args):
    usr_name = var_user_name.get().upper()
    usr_password = var_password.get()
    if usr_name in usrs_info:
        if usr_password == usrs_info[usr_name]:
            tk.messagebox.showinfo(title='欢迎', message='别来无恙？' + usr_name)
            w_login.destroy()
            run_iud_sql("insert into login_history (username, hostname, ip) values ('{}', '{}', '{}')".format(usr_name,
                                                                                                              hostname,
                                                                                                              ip))
            fc_choose(usr_name, hostname, ip)
        else:
            tk.messagebox.showerror(title='错误', message='密码错误，再试试？')
    else:
        is_sign_up = tk.messagebox.askyesno('欢迎',
                                            '你的账号还没注册，要现在注册吗？')
        if is_sign_up:
            usr_signup()

e_user_name.bind('<Return>', usr_login)
e_password.bind('<Return>', usr_login)


def str_to_hex(s):
    return ''.join([hex(ord(c)).replace('0x', '') for c in s])


def usr_signup():
    def sign_to_userinfo():
        global usrs_info
        datecode = 'Polestar' + datetime.datetime.now().strftime('%Y%m%d') + new_name.get().upper()
        if new_invitation_code.get().upper() != str_to_hex(datecode).upper():
            tk.messagebox.showerror('错误', '邀请码不正确，联系管理员获取。')
        else:
            np = new_pwd.get()
            npf = new_pwd_confirm.get()
            nn = new_name.get().upper()
            if np != npf:
                tk.messagebox.showerror('错误', '密码和确认密码不一致！')
            elif nn in usrs_info:
                tk.messagebox.showerror('错误', '此用户已存在！')
            else:
                sql_insert = '''
                insert into user_password (username, password) values ('{}','{}')
                '''.format(nn, np)
                ret = run_iud_sql(sql_insert)
                if ret == ['Error in database change operation!']:
                    tk.messagebox.showerror('错误', '更新数据库异常，联系系统管理员。')
                else:
                    rs_user = run_select_sql('select username, password from user_password')
                    usrs_info = {i[0]: i[1] for i in rs_user}
                    tk.messagebox.showinfo('欢迎', '你已成功注册！')
                    w_signup.destroy()

    w_signup = tk.Toplevel(w_login)
    w_signup.attributes("-toolwindow", 1)
    w_signup.wm_attributes("-topmost", 1)
    w_signup.geometry('350x210+800+600')
    w_signup.title('注册窗口')

    new_name = tk.StringVar()
    new_name.set('chixiao.yang')
    tk.Label(w_signup, text='用户名：', font=('微软雅黑', 9)).place(x=10, y=10)
    entry_new_name = tk.Entry(w_signup, textvariable=new_name)
    entry_new_name.place(x=150, y=10)

    new_pwd = tk.StringVar()
    tk.Label(w_signup, text='密码：', font=('微软雅黑', 9)).place(x=10, y=50)
    entry_usr_pwd = tk.Entry(w_signup, textvariable=new_pwd, show='*')
    entry_usr_pwd.place(x=150, y=50)

    new_pwd_confirm = tk.StringVar()
    tk.Label(w_signup, text='确认密码：', font=('微软雅黑', 9)).place(x=10, y=90)
    entry_usr_pwd_confirm = tk.Entry(w_signup, textvariable=new_pwd_confirm, show='*')
    entry_usr_pwd_confirm.place(x=150, y=90)

    new_invitation_code = tk.StringVar()
    tk.Label(w_signup, text='邀请码：', font=('微软雅黑', 9)).place(x=10, y=130)
    entry_invitation_code = tk.Entry(w_signup, textvariable=new_invitation_code)
    entry_invitation_code.place(x=150, y=130)

    btn_comfirm_sign_up = tk.Button(w_signup, text='注册', width=8, font=('微软雅黑', 9, 'bold'), command=sign_to_userinfo)
    btn_comfirm_sign_up.place(x=150, y=170)


x1 = 320
b_login = tk.Button(canvas, text='登录', width=10, font=('微软雅黑', 9, 'bold'), command=usr_login).place(x=20 + x1, y=310,
                                                                                                    anchor='nw')
b_signup = tk.Button(canvas, text='注册', width=10, font=('微软雅黑', 9, 'bold'), command=usr_signup).place(x=140 + x1, y=310,
                                                                                                      anchor='nw')
# b_exit = tk.Button(canvas, text = 'Exit', width = 10, font=('Calibri', 8), command = ).place(x = 260+x1, y = 320,
# anchor = 'nw')

# find the newest app version, judge if this is the newest app version.
sql = '''
select vers_id from
(select * from app_versions order by release_date desc)
where rownum = 1
'''
rs_ver = run_select_sql(sql)

if app_version != rs_ver[0][0]:
    tk.messagebox.showerror('错误', '这不是最新的客户端，请从IT公盘下载最新客户端使用！')
    exit()

rs_user = run_select_sql('select username, password from user_password')
usrs_info = {i[0]: i[1] for i in rs_user}

w_login.mainloop()

'''
长相思，在长安。
络纬秋啼金井阑，微霜凄凄簟色寒。
孤灯不明思欲绝，卷帷望月空长叹。
美人如花隔云端！
上有青冥之长天，下有渌水之波澜。
天长路远魂飞苦，梦魂不到关山难。
长相思，摧心肝！
'''