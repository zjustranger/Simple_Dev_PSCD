'''
用户登录页面信息
'''
import tkinter as tk
from tkinter import messagebox
import datetime
import socket
from function_choose_page import fc_choose
from DB_Connection import run_select_sql
from DB_Connection import run_iud_sql

app_version = 'Ver.0.2'

hostname = socket.gethostname()
ip = socket.gethostbyname(hostname)

w_login = tk.Tk()
w_login.geometry('600x350+800+500')
w_login.title("PSCD Chemicals Shelf Life Management" + '__' + app_version)
w_login.resizable(0, 0)

# welcome image
canvas = tk.Canvas(w_login, width = 600, height = 350, highlightthickness = 0, borderwidth = 0)
image_file = tk.PhotoImage(file='welcome.gif')
image = canvas.create_image(0,0, anchor='nw', image=image_file)
canvas.place(x = 0, y = 0, anchor = 'nw')

# user_name & password labels and entries, define 2 vars to quick adjust the login set location
x0, y0 = 150, 0
l_user_name = tk.Label(canvas, text = 'Username:', font=('Calibri', 10)).place(x = 20+x0, y = 80+y0, anchor = 'nw')
var_user_name = tk.StringVar()
e_user_name = tk.Entry(canvas, width = 14, textvariable = var_user_name).place(x = 90+x0, y = 80+y0, anchor = 'nw')
l_password = tk.Label(canvas, text = 'Password:', font=('Calibri', 10)).place(x = 220+x0, y = 80+y0, anchor = 'nw')
var_password = tk.StringVar()
e_password = tk.Entry(canvas, width = 14, textvariable = var_password, show = '*').place(x = 290+x0, y = 80+y0, anchor = 'nw')

# login, signup, exit button
def usr_login():
    usr_name = var_user_name.get().upper()
    usr_password = var_password.get()
    if usr_name in usrs_info:
        if usr_password == usrs_info[usr_name]:
            tk.messagebox.showinfo(title='Welcome', message='How are you? ' + usr_name)
            w_login.destroy()
            fc_choose(usr_name, hostname, ip)
        else:
            tk.messagebox.showerror(message='Error, your password is wrong, try again.')
    else:
        is_sign_up = tk.messagebox.askyesno('Welcome',
                               'You have not signed up yet. Sign up today?')
        if is_sign_up:
            usr_signup()

def str_to_hex(s):
    return ''.join([hex(ord(c)).replace('0x', '') for c in s])

def usr_signup():
    def sign_to_userinfo():
        global usrs_info
        datecode = 'Polestar'+datetime.datetime.now().strftime('%Y%m%d')+new_name.get().upper()
        if new_invitation_code.get().upper() != str_to_hex(datecode).upper():
            tk.messagebox.showerror('Error', 'Sorry! your invitation code is not correct.')
        else:
            np = new_pwd.get()
            npf = new_pwd_confirm.get()
            nn = new_name.get().upper()
            if np != npf:
                tk.messagebox.showerror('Error', 'Password and confirm password must be the same!')
            elif nn in usrs_info:
                tk.messagebox.showerror('Error', 'The user already existed!')
            else:
                sql_insert = '''
                insert into user_password values ('{}','{}')
                '''.format(nn, np)
                ret = run_iud_sql(sql_insert)
                if ret == 'Error in database change operation!':
                    tk.messagebox.showerror('ERROR','Error in update database, Contact Administrator')
                else:
                    rs_user = run_select_sql('select * from user_password')
                    usrs_info = {i[0]: i[1] for i in rs_user}
                    tk.messagebox.showinfo('Welcome', 'You have successfully signed up!')
                    w_signup.destroy()

    w_signup = tk.Toplevel(w_login)
    w_signup.attributes("-toolwindow", 1)
    w_signup.wm_attributes("-topmost", 1)
    w_signup.geometry('350x210+800+600')
    w_signup.title('Sign up window')

    new_name = tk.StringVar()
    new_name.set('cdsid')
    tk.Label(w_signup, text='User name: ').place(x=10, y=10)
    entry_new_name = tk.Entry(w_signup, textvariable=new_name)
    entry_new_name.place(x=150, y=10)

    new_pwd = tk.StringVar()
    tk.Label(w_signup, text='Password: ').place(x=10, y=50)
    entry_usr_pwd = tk.Entry(w_signup, textvariable=new_pwd, show='*')
    entry_usr_pwd.place(x=150, y=50)

    new_pwd_confirm = tk.StringVar()
    tk.Label(w_signup, text='Confirm password: ').place(x=10, y=90)
    entry_usr_pwd_confirm = tk.Entry(w_signup, textvariable=new_pwd_confirm, show='*')
    entry_usr_pwd_confirm.place(x=150, y=90)

    new_invitation_code = tk.StringVar()
    tk.Label(w_signup, text = 'Invitation code: ').place(x=10, y=130)
    entry_invitation_code = tk.Entry(w_signup, textvariable = new_invitation_code)
    entry_invitation_code.place(x=150, y= 130)

    btn_comfirm_sign_up = tk.Button(w_signup, text='Sign up', command=sign_to_userinfo)
    btn_comfirm_sign_up.place(x=150, y=170)




x1 = 320
b_login = tk.Button(canvas, text = 'Log in', width = 10, font=('Calibri', 8), command = usr_login).place(x = 20+x1, y = 320, anchor = 'nw')
b_signup = tk.Button(canvas, text = 'Sign up', width = 10, font=('Calibri', 8), command = usr_signup).place(x = 140+x1, y = 320, anchor = 'nw')
# b_exit = tk.Button(canvas, text = 'Exit', width = 10, font=('Calibri', 8), command = ).place(x = 260+x1, y = 320, anchor = 'nw')

# find the newest app version, judge if this is the newest app version.
sql = '''
select vers_id from
(select * from app_versions order by release_date desc)
where rownum = 1
'''
rs_ver = run_select_sql(sql)

if app_version != rs_ver[0][0]:
    tk.messagebox.showerror('Error', '这不是最新的客户端，请从IT公盘下载最新客户端使用！')
    exit()

rs_user = run_select_sql('select * from user_password')
usrs_info = {i[0]:i[1] for i in rs_user}

w_login.mainloop()