import os
import pandas as pd
import datetime

class MPS_Reader:
    def __init__(self, filename):
        self.filename = filename
        self.headline = 7
        self.headline -= 1
        self.df = pd.read_excel(self.filename, header = self.headline)
    def calculate(self):
        # 进行数据预处理
        self.df1 = self.df.iloc[:, 6:]
        self.df2 = self.df1[~self.df1['Col'].isnull()]
        self.colors = list(set(self.df2['Col']))
        self.colors.sort()
        self.weeks = list(self.df2.columns)
        self.weeks.remove('Col')
        # 产生统计的字典
        self.result = {(i,j):0 for i in self.colors for j in self.weeks}
        # 遍历Dataframe所有的值，统计结果
        rows, cols = self.df2.shape
        for i in range(rows):
            for j in range(1, cols):
                self.result[(self.df2.iloc[i,0], self.df2.columns[j])] += self.df2.iloc[i,j]
    def output(self):
        # 生成可供使用的返回二维列表
        out = [[self.filename, k[0], k[1], v] for k, v in self.result.items()]
        return out

logfile = open("running.log", "a")
print('*'*100, file=logfile)
files = os.listdir()
mps_files = [i for i in files if i.endswith('.xlsx') and 'MPS' in i]
mps_files.sort()

# 开始处理每个MPS文件
outfile = []
for filename in mps_files:
    temp_reader = MPS_Reader(filename)
    temp_reader.calculate()
    outfile.extend(temp_reader.output())

# 输出结果
out_df = pd.DataFrame(outfile, columns=['From_File', 'Color', 'Week', 'Sum_Qty'])
out_filename = 'mps_comparison.xlsx'
writer = pd.ExcelWriter(out_filename)
out_df.to_excel(writer, index=False, encoding='UTF-8')
writer.save()