import pandas as pd
from datetime import datetime, timedelta

df = pd.read_clipboard()  # 从粘贴板上读取数据
t = datetime.now().date() - timedelta(days=1)
writer = pd.ExcelWriter('样式%d%02d%02d.xlsx' % (t.year, t.month, t.day))
workbook = writer.book
fmt = workbook.add_format({"font_name": u"微软雅黑"})
percent_fmt = workbook.add_format({'num_format': '0.00%'})
amt_fmt = workbook.add_format({'num_format': '#,##0'})
border_format = workbook.add_format({'border': 1})
note_fmt = workbook.add_format(
    {'bold': True, 'font_name': u'微软雅黑', 'font_color': 'red', 'align': 'left', 'valign': 'vcenter'})
date_fmt = workbook.add_format({'bold': False, 'font_name': u'微软雅黑', 'num_format': 'yyyy-mm-dd'})

date_fmt1 = workbook.add_format(
    {'bold': True, 'font_size': 10, 'font_name': u'微软雅黑', 'num_format': 'yyyy-mm-dd', 'bg_color': '#9FC3D1',
     'valign': 'vcenter', 'align': 'center'})
highlight_fmt = workbook.add_format({'bg_color': '#FFD7E2', 'num_format': '0.00%'})

l_end = len(df.index) + 2  # 表格的行数,便于下面设置格式
df.to_excel(writer, sheet_name=u'测试页签', encoding='utf8', header=False, index=False, startcol=0, startrow=2)
worksheet1 = writer.sheets[u'测试页签']
for col_num, value in enumerate(df.columns.values):
    worksheet1.write(1, col_num, value, date_fmt1)
worksheet1.merge_range('A1:B1', u'测试情况统计表', note_fmt)
# 设置列宽
worksheet1.set_column('A:D', 30, fmt)
# 有条件设定表格格式：金额列
worksheet1.conditional_format('B3:E%d' % l_end, {'type': 'cell', 'criteria': '>=', 'value': 1, 'format': amt_fmt})
# 有条件设定表格格式：百分比
worksheet1.conditional_format('E3:E%d' % l_end,
                              {'type': 'cell', 'criteria': '<=', 'value': 0.1, 'format': percent_fmt})
# 有条件设定表格格式：高亮百分比
worksheet1.conditional_format('E3:E%d' % l_end,
                              {'type': 'cell', 'criteria': '>', 'value': 0.1, 'format': highlight_fmt})
# 加边框
worksheet1.conditional_format('A1:E%d' % l_end, {'type': 'no_blanks', 'format': border_format})
# 设置日期格式
worksheet1.conditional_format('A3:A62', {'type': 'no_blanks', 'format': date_fmt})
writer.save()
