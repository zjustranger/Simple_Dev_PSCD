import tkinter as tk
import os
import pandas as pd
import datetime
from tkinter import messagebox

cur_dir = os.getcwd()
data_dir = cur_dir + '\\' + 'data_files' + '\\'
datafile = data_dir + 'works.xlsx'

w = tk.Tk()
w.title('工作速记')
w.geometry('920x480+500+200')
w.resizable(0,0)
canvas = tk.Canvas(w, width=920, height=480, highlightthickness=0, borderwidth=0)
image_file = tk.PhotoImage(file=data_dir + 'bg.gif')
image = canvas.create_image(0, 0, anchor='nw', image=image_file)
canvas.place(x=0, y=0, anchor='nw')


v_add_date = tk.StringVar()
tk.Entry(canvas, textvariable = v_add_date, width = 10, font = ('微软雅黑', 13)).place(x=170, y=50)
v_add_date.set(datetime.datetime.now().strftime('%y') + 'W' + datetime.datetime.now().strftime('%V') + 'D' + datetime.datetime.now().strftime('%u'))

v_due_date = tk.StringVar()
tk.Entry(canvas, textvariable = v_due_date, width = 10, font = ('微软雅黑', 13)).place(x=530, y=50)

v_topic = tk.Text(canvas, height = 2, width = 80, font = ('微软雅黑', 13, 'bold'))
v_topic.place(x=53, y=122)
v_content = tk.Text(canvas, height = 6, width = 80, font = ('微软雅黑', 13, 'bold'))
v_content.place(x=53, y=215)

def submit():
    Sys_timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    Date = v_add_date.get()
    Category = ''
    Problem = v_topic.get('0.0', 'end')[:-1]
    Prio = ''
    Action = v_content.get('0.0', 'end')[:-1]
    Resp = ''
    Target = v_due_date.get()
    Status = 'DM'
    End = ''
    Remark = ''
    new = pd.DataFrame({'Sys_timestamp': Sys_timestamp, 'Date': Date, 'Category': Category, 'Problem/abnormality': Problem, 'Prio': Prio, 'Action': Action, 'Resp': Resp, 'Target date': Target, 'Status DMAIC': Status, 'End time': End, 'Remark': Remark}, index = [1])
    try:
        df = pd.read_excel(datafile)
        df = df.append(new, ignore_index = True)
        df.to_excel(datafile, index = False)
        tk.messagebox.showinfo('Info', '保存成功！')
    except Exception as e:
        tk.messagebox.showerror('Error', '文件读取/保存中出现异常，{}，{}'.format(type(e),e))
    # print(Sys_timestamp)
    # print(Date)
    # print(v_topic.get('0.0', 'end')[:-1])
    # print(v_content.get('0.0', 'end')[:-1])

tk.Button(canvas, text = 'Submit!', width = 10, borderwidth = 3, font = ('微软雅黑', 10, 'bold'), command = submit).place(x=750, y=400)

w.mainloop()