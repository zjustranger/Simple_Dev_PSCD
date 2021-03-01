import cx_Oracle as cx



def run_select_sql(sql):
    tns = cx.makedsn('chepsvol3011.che.volvocars.net', 1521, service_name = 'dpomps1q')
    db = cx.connect('PSQM', 'PSQM12345', tns, encoding = "UTF-8", nencoding = "UTF-8")
    cur = db.cursor()
    try:
        cur.execute(sql)
        rs = cur.fetchall()
        return rs
    except:
        return ['Error in select!']
    finally:
        cur.close()
        db.close()

def run_iud_sql(sql):
    tns = cx.makedsn('chepsvol3011.che.volvocars.net', 1521, service_name = 'dpomps1q')
    db = cx.connect('PSQM', 'PSQM12345', tns, encoding = "UTF-8", nencoding = "UTF-8")
    cur = db.cursor()
    try:
        cur.execute(sql)
        db.commit()
    except:
        db.rollback()
        return ['Error in database change operation!']
    finally:
        cur.close()
        db.close()

def run_oracle_function(proc_name, inputVar=[]):
    tns = cx.makedsn('chepsvol3011.che.volvocars.net', 1521, service_name = 'dpomps1q')
    db = cx.connect('PSQM', 'PSQM12345', tns, encoding = "UTF-8", nencoding = "UTF-8")
    cur = db.cursor()
    retCode = cur.var(cx.STRING)
    cur.callfunc(proc_name, retCode, inputVar)
    return retCode.getvalue()

def run_oracle_procedure(proc_name, inputVar=[]):
    tns = cx.makedsn('chepsvol3011.che.volvocars.net', 1521, service_name = 'dpomps1q')
    db = cx.connect('PSQM', 'PSQM12345', tns, encoding = "UTF-8", nencoding = "UTF-8")
    cur = db.cursor()
    cur.callproc(proc_name, inputVar)

def gr_scanning(p_label, p_user, p_hostname, p_ip, p_loc_id):
    tns = cx.makedsn('chepsvol3011.che.volvocars.net', 1521, service_name = 'dpomps1q')
    db = cx.connect('PSQM', 'PSQM12345', tns, encoding = "UTF-8", nencoding = "UTF-8")
    cur = db.cursor()
    p_retVar = cur.var(cx.NUMBER)
    cur.callproc('GR_Scanning', [p_label, p_user, p_hostname, p_ip, p_loc_id, p_retVar])
    return p_retVar.getvalue()

def get_best_suggestion_package(p_sn):
    tns = cx.makedsn('chepsvol3011.che.volvocars.net', 1521, service_name = 'dpomps1q')
    db = cx.connect('PSQM', 'PSQM12345', tns, encoding = "UTF-8", nencoding = "UTF-8")
    cur = db.cursor()
    p_match_code = cur.var(cx.NUMBER)
    p_chem_flag = cur.var(cx.STRING)
    p_best_sn = cur.var(cx.STRING)
    p_out_loc = cur.var(cx.STRING)
    p_out_qty = cur.var(cx.NUMBER)
    p_out_dd = cur.var(cx.STRING)
    cur.callproc('feedback_best_package',
                 [p_sn, p_match_code, p_chem_flag, p_best_sn, p_out_loc, p_out_qty, p_out_dd])
    return (p_match_code.getvalue(), p_chem_flag.getvalue(), p_best_sn.getvalue(), p_out_loc.getvalue(), p_out_qty.getvalue(), p_out_dd.getvalue())


def get_feedback_from_scanning(label_content):
    tns = cx.makedsn('chepsvol3011.che.volvocars.net', 1521, service_name = 'dpomps1q')
    db = cx.connect('PSQM', 'PSQM12345', tns, encoding = "UTF-8", nencoding = "UTF-8")
    cur = db.cursor()
    p_partno = cur.var(cx.STRING)
    p_qty = cur.var(cx.NUMBER)
    p_supplier = cur.var(cx.STRING)
    p_dn = cur.var(cx.STRING)
    p_sn = cur.var(cx.STRING)
    p_bn = cur.var(cx.STRING)
    p_md = cur.var(cx.STRING)
    p_dd = cur.var(cx.STRING)
    p_loc_id = cur.var(cx.STRING)
    p_parent_sn = cur.var(cx.STRING)
    cur.callproc('feedback_scanning_result', [label_content, p_partno, p_qty, p_supplier, p_dn, p_sn, p_bn, p_md, p_dd, p_loc_id, p_parent_sn])
    return (p_partno.getvalue(), p_qty.getvalue(), p_supplier.getvalue(), p_dn.getvalue(), p_sn.getvalue(), p_bn.getvalue(), p_md.getvalue(), p_dd.getvalue(), p_loc_id.getvalue(), p_parent_sn.getvalue())

def get_sninfo_from_scanning(label_content):
    tns = cx.makedsn('chepsvol3011.che.volvocars.net', 1521, service_name = 'dpomps1q')
    db = cx.connect('PSQM', 'PSQM12345', tns, encoding = "UTF-8", nencoding = "UTF-8")
    cur = db.cursor()
    p_partno = cur.var(cx.STRING)
    p_descr = cur.var(cx.STRING)
    p_sn = cur.var(cx.STRING)
    p_status = cur.var(cx.STRING)
    cur.callproc('feedback_sninfo_scanning',
                 [label_content, p_sn, p_partno, p_descr, p_status])
    return (p_sn.getvalue(), p_partno.getvalue(), p_descr.getvalue(), p_status.getvalue())

if __name__ == '__main__':
    rs = run_select_sql("select * from parts")
    for i in rs:
        print(i)


