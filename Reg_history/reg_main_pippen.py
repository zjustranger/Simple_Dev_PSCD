import pandas as pd
import cx_Oracle as cx
import datetime

def change_volvoday_to_date(volvoday):
    try:
        year, isoweek, day = volvoday[0:4], volvoday[4:6], volvoday[6]
        return datetime.datetime.fromisocalendar(int(year), int(isoweek), int(day)).strftime('%Y-%m-%d')
    except:
        return None

logfile = open("running.log", "a")
print('*'*100, file=logfile)

sql = '''
select my, ifyon, rvariant, rmarkt, rkleur, rmfk, rbekled, rfindest, options, ibody, tagid, p11, ivmix, vin, p1, p2, p3, p4, p5, p6, p7, p8, p9, plan_fr, p10 from 
(select tcp715.ibody, tcp715.tagid, tcp712.ivmix, tcp710.rvintyp||tcp710.ichassis vin, tcp712.dtnfycpt plan_fr, tcp010.iincd, TCP716.DBREG, 'MY'||tcp715.IMODELJ my, tcp715.ifyon, tcp710.rkleur, tcp710.rmarkt, tcp710.rfindest, tcp711.RVARIANT, tcp711.rmfk, tcp711.rbekled, opt.options
from tcp715 left join tcp712 on (tcp715.ibody = tcp712.ibody) left join tcp710 on (tcp715.ibody = tcp710.ibody) left join tcp716 on (tcp716.NIDTCP715 = tcp715.nidtcp715) left join tcp010 on (tcp010.nidtcp010 = tcp716.nidtcp010) 
left join tcp711 on (tcp711.NIDTCP712 = tcp712.nidtcp712) left join (select ifyon, listagg(rsopt, '/') within group(order by rsopt) options from tcp720 group by ifyon) opt on (opt.ifyon = tcp715.ifyon)
where tcp715.ibody >= '1800000' and tcp010.iincd in ('15000', '15630', '15700', '15900', '28000', '30000', '31100', '35900', '38000', '39800', '02000')
order by tcp715.ibody, tcp010.iincd) original_result
pivot (max(to_char(dbreg, 'yyyy-mm-dd')) for iincd in('15000' as p1, '15630' as p2, '15700' as p3, '15900' as p4, '28000' as p5, '30000' as p6, '31100' as p7, '35900' as p8, '38000' as p9, '39800' as p10, '02000' as p11))
order by ivmix, ibody
'''

try:
    tns = cx.makedsn('npc.che.volvocars.net', 49957, sid='DPQ')
    db = cx.connect('cip_sys', 'cip_sys1', tns, encoding="UTF-8", nencoding="UTF-8")
    cur = db.cursor()
    cur.execute(sql)
    rs = cur.fetchall()
    df = pd.DataFrame(rs)
    df.columns = ['MY', 'FY', 'Variant', 'MKT', 'COLOR', 'MKT CODE', 'Interior Color', 'Final Destination', 'Options', 'Body Number','RFID', 'Scrapped', 'MIX Number','VIN','Under Body On Line','Upper Body On Line','UB in HOP','A Shop Buy Off','B Shop On Line','Mix','Pre-trim On Line','Final End','R&B (Q Start)','FR Target SYS','FR Real']

    # change the volvoday to iso date -- for FR Target SYS
    rows = df.shape[0]
    col = list(df.columns).index('FR Target SYS')
    for i in range(rows):
        df.iloc[i, col] = change_volvoday_to_date(df.iloc[i, col])

    filename = r'\\chesnm0201.che.volvocars.net\PROJ2\6765-SHR-VCC08200\Production Plan & Order\Production Plan\Cars_Reg_Tracking_Daily.xlsx'
    # filename = 'Cars_Reg_Tracking_Daily.xlsx'    # use this line to debug if needed
    writer = pd.ExcelWriter(filename)
    df.to_excel(writer, index=False, encoding='UTF-8')
    writer.save()
    print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), "    ",
          "New excel file generated successfully!", file=logfile)
except Exception as e:
    print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), "    ", e, file=logfile)
finally:
    cur.close()
    db.close()
    logfile.close()
























