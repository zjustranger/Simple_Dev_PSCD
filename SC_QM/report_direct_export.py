import pandas as pd
from DB_Connection import run_select_sql
import os
import datetime
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import subprocess

output_temp_dir = os.getcwd() + r'\temp\tempdata' + '\\'

def stock_query(p_user):
    # Get the detail stock and summary stock
    sql1 = '''
            select iv.partno, iv.loc_id, iv.qty, iv.serial_no, pk.supplier_id, pk.dn, pk.parent_sn, pk.prod_date, pk.valid_day, pk.due_date, sysdate from inventory iv left join packages pk
    on (iv.PACKAGE_ID = pk.package_id and iv.SERIAL_NO = pk.SERIAL_NO) order by iv.partno, iv.loc_id, iv.qty
    '''
    rs1 = run_select_sql(sql1)
    df1 = pd.DataFrame(rs1)
    df1.columns = ['Part Number', 'Location', 'Qty', 'Serial Number', 'Supplier', 'Dispatch Note', 'Parent SN', 'Production Date', 'Valid Day', 'Due Date', 'Report Time']

    sql2 = '''
            select partno, loc_id, sum(qty), sysdate from inventory group by partno, loc_id order by partno, loc_id
    '''
    rs2 = run_select_sql(sql2)
    df2 = pd.DataFrame(rs2)
    df2.columns = ['Part Number', 'Location', 'Total Qty', 'Report Time']

    # Prepare to export to excel
    output_file_name = 'Temp_Stock_Report' + '_' + p_user + '_' + datetime.datetime.now().strftime('%Y%m%d%H%M%S') + '.xlsx'
    writer = pd.ExcelWriter(output_temp_dir + output_file_name)
    df1.to_excel(writer, sheet_name="Detail Stock Info", index=False)
    df2.to_excel(writer, sheet_name="Summary Stock Info", index=False)
    # adjust the column width. 中文2个字符宽度，英文1个字符宽度，根据标题行和内容自行确定每列宽度
    sheet_detail = writer.sheets['Detail Stock Info']
    sheet_summary = writer.sheets['Summary Stock Info']
    sheet_detail.column_dimensions['A'].width = 12
    sheet_detail.column_dimensions['B'].width = 20
    sheet_detail.column_dimensions['C'].width = 8
    sheet_detail.column_dimensions['D'].width = 20
    sheet_detail.column_dimensions['E'].width = 8
    sheet_detail.column_dimensions['F'].width = 20
    sheet_detail.column_dimensions['G'].width = 20
    sheet_detail.column_dimensions['H'].width = 15
    sheet_detail.column_dimensions['I'].width = 10
    sheet_detail.column_dimensions['J'].width = 20
    sheet_detail.column_dimensions['K'].width = 20
    sheet_summary.column_dimensions['A'].width = 12
    sheet_summary.column_dimensions['B'].width = 20
    sheet_summary.column_dimensions['C'].width = 12
    sheet_summary.column_dimensions['D'].width = 20

    try:
        writer.save()
    except Exception as e:
        tk.messagebox.showerror('Error', 'Error in saving excel file: ' + str(e))
        exit(2)

    # Normally at this step, excel file have been generated successfully. Open it.
    # os.popen('"'+output_temp_dir+output_file_name+'"')
    subprocess.Popen('"'+output_temp_dir+output_file_name+'"', shell = True)

def stock_report(p_user):
    choose = tk.messagebox.askokcancel('Choose', 'Will generate an excel report for you, continue?')
    if choose == True:
        stock_query(p_user)
    else:
        pass

def stock_aging(p_user):
    # Calculate the stock aging
    choose = tk.messagebox.askokcancel('Choose', 'Will generate an excel report for you, continue?')
    if choose == True:
        sql1 = '''
        select pk.PARTNO, pk.SUPPLIER_ID, pk.serial_no, pk.qty, pk.dn, ts.SYS_TIMESTAMP as gr_date, round(sysdate - ts.sys_timestamp, 2), sysdate from packages pk left join transactions ts
        on (pk.PACKAGE_ID = ts.PACKAGE_ID and pk.partno = ts.PARTNO and ts.movement_type = '101') order by trunc(gr_date), pk.package_id, pk.partno
        '''
        rs1 = run_select_sql(sql1)
        df1 = pd.DataFrame(rs1)
        df1.columns = ['Part Number', 'Supplier', 'Serial Number', 'Qty', 'Dispatch Note', 'GR Date', 'Aging(Day)', 'Report Time']

        # Prepare to export to excel
        output_file_name = 'Temp_Aging_Report' + '_' + p_user + '_' + datetime.datetime.now().strftime(
            '%Y%m%d%H%M%S') + '.xlsx'
        writer = pd.ExcelWriter(output_temp_dir + output_file_name)
        df1.to_excel(writer, sheet_name="Stock Aging Report", index=False)
        # adjust the column width. 中文2个字符宽度，英文1个字符宽度，根据标题行和内容自行确定每列宽度
        sheet_aging = writer.sheets['Stock Aging Report']
        sheet_aging.column_dimensions['A'].width = 12
        sheet_aging.column_dimensions['B'].width = 12
        sheet_aging.column_dimensions['C'].width = 20
        sheet_aging.column_dimensions['D'].width = 8
        sheet_aging.column_dimensions['E'].width = 20
        sheet_aging.column_dimensions['F'].width = 20
        sheet_aging.column_dimensions['G'].width = 12
        sheet_aging.column_dimensions['H'].width = 20

        try:
            writer.save()
        except Exception as e:
            tk.messagebox.showerror('Error', 'Error in saving excel file: ' + str(e))
            exit(2)

        # Normally at this step, excel file have been generated successfully. Open it.
        subprocess.Popen('"'+output_temp_dir+output_file_name+'"', shell = True)
    else:
        pass

def transaction_history(p_user):
    # Export the transaction history
    choose = tk.messagebox.askokcancel('Choose', 'Will generate an excel report for you, continue?')
    if choose == True:
        sql1 = '''
        select ts.partno, ts.qty, ts.location, ts.serial_no, ts.movement_type, mt.TYPE_DESCR, ss.inv_descr, ts.supplier_id, ts.dn, ts.userid, ts.sys_timestamp from
        (select sys_timestamp, partno, qty, supplier_id, inv_type, movement_type, to_loc as location, userid, DN, serial_no, seq from transactions where to_loc is not NULL
        union all
        select sys_timestamp, partno, -qty, supplier_id, inv_type, movement_type, from_loc as location, userid, DN, serial_no, seq from transactions where from_loc is not NULL) ts
        left join movement_type mt on (ts.MOVEMENT_TYPE = mt.type_id) left join stock_status ss on (ts.inv_type = ss.inv_type)
        order by ts.seq, ts.qty
        '''
        rs1 = run_select_sql(sql1)
        df1 = pd.DataFrame(rs1)
        df1.columns = ['Part Number', 'Qty', 'Location', 'Serial Number', 'Movement Type', 'Movement Description', 'Inventory Type', 'Supplier', 'Dispatch Note', 'User Name', 'Transaction Time']

        # Prepare to export to excel
        output_file_name = 'Temp_transaction_Report' + '_' + p_user + '_' + datetime.datetime.now().strftime(
            '%Y%m%d%H%M%S') + '.xlsx'
        writer = pd.ExcelWriter(output_temp_dir + output_file_name)
        df1.to_excel(writer, sheet_name="Transaction History Report", index=False)
        # adjust the column width. 中文2个字符宽度，英文1个字符宽度，根据标题行和内容自行确定每列宽度
        sheet_transaction = writer.sheets['Transaction History Report']
        sheet_transaction.column_dimensions['A'].width = 12
        sheet_transaction.column_dimensions['B'].width = 8
        sheet_transaction.column_dimensions['C'].width = 30
        sheet_transaction.column_dimensions['D'].width = 20
        sheet_transaction.column_dimensions['E'].width = 20
        sheet_transaction.column_dimensions['F'].width = 35
        sheet_transaction.column_dimensions['G'].width = 20
        sheet_transaction.column_dimensions['H'].width = 10
        sheet_transaction.column_dimensions['I'].width = 20
        sheet_transaction.column_dimensions['J'].width = 12
        sheet_transaction.column_dimensions['K'].width = 20

        try:
            writer.save()
        except Exception as e:
            tk.messagebox.showerror('Error', 'Error in saving excel file: ' + str(e))
            exit(2)

        # Normally at this step, excel file have been generated successfully. Open it.
        subprocess.Popen('"'+output_temp_dir+output_file_name+'"', shell = True)
    else:
        pass

def shelf_life_report(p_user):
    # Export the shelf life report
    choose = tk.messagebox.askokcancel('Choose', 'Will generate an excel report for you, continue?')
    if choose == True:
        sql1 = '''
        select rslt.*, case rvd when 'NO_MANAGEMENT' then 'NO_MANAGEMENT' else to_char(round((valid_day - rvd)*100/valid_day, 2))||'%' end, sysdate from
        (select pk.partno, iv.loc_id, pk.qty, pk.serial_no, pk.supplier_id, pk.prod_date, pk.due_date, pk.dn, pk.parent_sn, pa.valid_day,
        case when pa.chem_flag is NULL then 'NO_MANAGEMENT' else to_char(round(to_date(pk.due_date, 'yyyymmdd') - sysdate, 2)) end rvd from packages pk
        left join inventory iv on (pk.SERIAL_NO = iv.SERIAL_NO and pk.PARTNO = iv.partno and pk.qty = iv.qty) left join parts pa on pk.partno = pa.partno) rslt
        order by partno, loc_id, rvd
        '''
        rs1 = run_select_sql(sql1)
        df1 = pd.DataFrame(rs1)
        df1.columns = ['Part Number', 'Location', 'Qty', 'Serial Number', 'Supplier', 'Production Date', 'Due Date', 'Dispatch Note', 'Parent SN', 'Part\'s Valid Day', 'Remaining Valid Day', 'Ratio', 'Report Time']

        # Prepare to export to excel
        output_file_name = 'Temp_shelf_life_Report' + '_' + p_user + '_' + datetime.datetime.now().strftime(
            '%Y%m%d%H%M%S') + '.xlsx'
        writer = pd.ExcelWriter(output_temp_dir + output_file_name)
        df1.to_excel(writer, sheet_name="Shelf Life Report", index=False)
        # adjust the column width. 中文2个字符宽度，英文1个字符宽度，根据标题行和内容自行确定每列宽度
        sheet_shelf_life = writer.sheets['Shelf Life Report']
        sheet_shelf_life.column_dimensions['A'].width = 12
        sheet_shelf_life.column_dimensions['B'].width = 30
        sheet_shelf_life.column_dimensions['C'].width = 8
        sheet_shelf_life.column_dimensions['D'].width = 20
        sheet_shelf_life.column_dimensions['E'].width = 10
        sheet_shelf_life.column_dimensions['F'].width = 20
        sheet_shelf_life.column_dimensions['G'].width = 12
        sheet_shelf_life.column_dimensions['H'].width = 20
        sheet_shelf_life.column_dimensions['I'].width = 20
        sheet_shelf_life.column_dimensions['J'].width = 20
        sheet_shelf_life.column_dimensions['K'].width = 20
        sheet_shelf_life.column_dimensions['L'].width = 20
        sheet_shelf_life.column_dimensions['M'].width = 20

        try:
            writer.save()
        except Exception as e:
            tk.messagebox.showerror('Error', 'Error in saving excel file: ' + str(e))
            exit(2)

        # Normally at this step, excel file have been generated successfully. Open it.
        subprocess.Popen('"'+output_temp_dir+output_file_name+'"', shell = True)
    else:
        pass



if __name__ == '__main__':
    stock_aging('cyang44')