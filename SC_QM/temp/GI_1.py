import tkinter as tk
from time import sleep
from tkinter import messagebox
from DB_Connection import get_feedback_from_scanning
from DB_Connection import get_best_suggestion_package
from DB_Connection import run_oracle_function

def gi_1(p_user):
    gi_1 = tk.Toplevel()
    gi_1.geometry('1200x700+400+150')
    gi_1.title('GI Scanning')
    gi_1.resizable(0, 0)

    # attach image
    canvas = tk.Canvas(gi_1, width=1200, height=700, highlightthickness=0, borderwidth=0)
    image_file = tk.PhotoImage(file='GI_1.gif')
    image = canvas.create_image(0, 0, anchor='nw', image=image_file)
    canvas.place(x=0, y=0, anchor='nw')

    l = tk.Label(canvas, text='Scanning Input:', font=('Calibri', 15)).place(x=40, y=190)
    label_content = tk.StringVar()
    e = tk.Entry(canvas, textvariable=label_content, width=80, font=('Calibri', 16))
    e.place(x=190, y=190)

    def send_scanning(arg):
        global p_partno, p_qty, p_supplier, p_dn, p_sn, p_md, p_dd, p_loc_id, p_parent_sn
        p_partno, p_qty, p_supplier, p_dn, p_sn, p_md, p_dd, p_loc_id, p_parent_sn = get_feedback_from_scanning(
            label_content.get())
        show_package_info = ''
        if p_qty != 0:
            show_package_info = "Package's SN is: " + p_sn + ". Current Location: " + p_loc_id + ". Qty: " + str(
                p_qty) + '.' + '\nDefalut issue qty is set as the package qty. Suggestion as below:'
            if p_parent_sn:
                show_package_info = show_package_info + '\nThis package is a child package split from ' + p_parent_sn + '.'

            try:
                p_match_code, p_chem_flag, p_best_sn, p_out_loc, p_out_qty, p_out_dd = get_best_suggestion_package(p_sn)
            except:
                p_match_code = 1

            # add comments here.
            if p_match_code == 0:
                show_package_info = show_package_info + '\nYou have choosed the best package to be issued for this part number!'
            elif p_match_code == 2:
                show_package_info = show_package_info + '\nThis part number without shelf life management, but exists smaller package: {0} \nat location: {1}, qty: {2}. May Consider to issue it firstly.'.format(p_best_sn, p_out_loc, p_out_qty)
            elif p_match_code == 3:
                show_package_info = show_package_info + '\nThis part number without shelf life management, but exists earlier GR package: {0} \nat location: {1}, qty: {2}. May Consider to issue it firstly.'.format(p_best_sn, p_out_loc, p_out_qty)
            elif p_match_code == 6:
                show_package_info = show_package_info + '\nThis part number has shelf life management, exists package may past due earlier: {0} \nat location: {1}, qty: {2}. May Consider to issue it firstly.'.format(p_best_sn, p_out_loc, p_out_qty)
            elif p_match_code == 7:
                show_package_info = show_package_info + '\nThis part number has shelf life management, exists package GR earlier: {0} \nat location: {1}, qty: {2}. May Consider to issue it firstly.'.format(p_best_sn, p_out_loc, p_out_qty)
            elif p_match_code == 8:
                show_package_info = show_package_info + '\nThis part number has shelf life management, exists smaller package: {0} \nat location: {1}, qty: {2}. May Consider to issue it firstly.'.format(p_best_sn, p_out_loc, p_out_qty)
            else:
                show_package_info = show_package_info + '\nException happened in finding best SN.'

            l_show_content.set(show_package_info)
            l_show.config(fg='green')
            e_issue_qty.set(p_qty)
        else:
            show_package_info = "Cannot find current package! \nCheck if it hasn't been received or has been issued?"
            l_show_content.set(show_package_info)
            l_show.config(fg='red')
        sleep(0.2)
        label_content.set('')


    e.bind('<Return>', send_scanning)

    l_show_content = tk.StringVar()
    l_show_content.set(p_user + ', Welcome! Please scan the issue QR code label to get information.')
    l_show = tk.Label(canvas, textvariable=l_show_content, width = 103, justify = tk.LEFT, font=('Calibri', 15, 'bold'))
    l_show.place(x=40, y=280)

    x0, y0 = 80, -80
    label3 = tk.Label(canvas, text = 'Issue Qty:', font = ('Calibri', 15)).place(x = 800+x0, y = 600+y0, anchor = 'nw')
    e_issue_qty = tk.StringVar()
    e_issue = tk.Entry(canvas, textvariable = e_issue_qty, width = 12, font=('Calibri', 16))
    e_issue.place(x=800+x0, y=640+y0)

    def confirm_issue():
        global p_sn, p_partno, p_qty
        issue_qty = eval(e_issue_qty.get())
        go_next = tk.messagebox.askyesno('Info',
                                         'You will issue SN: {0}, part number: {1}, qty: {2}'.format(p_sn, p_partno, issue_qty) + '. Are you sure?')
        if go_next:
            l_show_content.set("Issuing in progress...")
            if p_sn and issue_qty and p_user:
                if issue_qty > p_qty or issue_qty <= 0:
                    tk.messagebox.showerror('ERROR!', "Issue qty error.")
                else:
                    retVar = run_oracle_function('goods_issue',
                                                 [p_sn, issue_qty, p_user])
                    print(retVar)
                    if retVar == '0':
                        tk.messagebox.showinfo('Success!', 'Issued successfully!')
                        l_show_content.set('Scan Next package')
                        label_content.set('')
                        e_issue_qty.set('')
                    else:
                        tk.messagebox.showerror('ERROR!', 'Move failed. Contact Administrator.')
            else:
                tk.messagebox.showerror('ERROR!', 'Goods Issuing information is not complete')
        else:
            pass


    b = tk.Button(canvas, text = 'Issue!', width = 10, font=('Calibri', 12, 'bold'), command = confirm_issue).place(x= 950+x0, y=640+y0)

    label_user = tk.Label(canvas, text=' Current Login User: ' + p_user + ' ',
                          font=('Calibri', 12, 'bold italic')).place(x=20, y=650, anchor='nw')
    gi_1.mainloop()


if __name__ == '__main__':
    gi_1('TEST')