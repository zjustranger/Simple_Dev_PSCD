import datetime

# format YYYY/MM/DD HH24:MI:SS
def str_to_datetime(str):
    'the string format should be like YYYY/MM/DD HH24:MI:SS, return a datetime value'
    return datetime.datetime.strptime(str, '%Y/%m/%d %H:%M:%S')

def datetime_to_str(dt):
    'transfer a value from datetime to string format like YYYY/MM/DD HH24:MI:SS'
    return dt.strftime('%Y/%m/%d %H:%M:%S')

def calculate_prod_diff(from_dt, to_dt, working_periods = None, no_working_days = None):
    '''calculate a time difference according to Polestar working schedule, input 2 datetime value, return a number represent the total seconds
    the optional parameter working_periods is used to define working time in normal days. format:[['08:30:00', '10:00:00'], ['10:10:00', '11:30:00'], ...]
    the optional parameter no_working_days is used to define no working days, format:['2020/07/25', '2020/07/26', ...]'''
    # for testing, define default working periods and no working days.
    if not working_periods:
        working_periods = [['08:20:00', '10:00:00'], ['10:10:00', '11:35:00'],['12:15:00', '14:30:00'],['14:40:00', '16:40:00']]
    if not no_working_days:
        no_working_days = ['2020/07/25','2020/07/26','2020/08/01','2020/08/02','2020/08/08','2020/08/09']

    # swap two datetime if sequence is not correct
    if from_dt > to_dt:
        from_dt, to_dt = to_dt, from_dt

    # # prepare the no_working_periods
    # no_working_periods = []
    # for index, period in enumerate(working_periods):
    #     if index == 0:
    #         # 首次迭代，判断生产时间是否从0点开始，如果不从0点开始，则非生产时段需要从0点开始记
    #         if period[0] != '00:00:00':
    #             add_periods = ['00:00:00', period[0]]
    #             no_working_periods.append(add_periods)
    #     else:
    #         # 加上这次的区间
    #         new_period_end = period[0]
    #         no_working_periods.append([new_period_start, new_period_end])
    #     if index == len(working_periods)-1:
    #         # 如果已经是最后一次迭代，判断生产结束时间是否是24点，否则非生产时段需要加上最后到24点的一段
    #         if period[1] != '24:00:00':
    #             add_periods = [period[1], '24:00:00']
    #             no_working_periods.append(add_periods)
    #     # 标记下一个非生产时段的起始时间为这个生产时段的结束,为下次循环做准备
    #     new_period_start = period[1]

    # 定义函数，如果当前时间戳是非生产时间，寻找下一个最近的生产时间开始点; 否则就返回本身
    def find_next_prod_start(dt):
        date, time = datetime_to_str(dt).split(' ')
        if date in no_working_days:
            while date in no_working_days:
                # 循环找下一天，直到找到的天数不在非工作日为止
                date = (datetime.datetime.strptime(date, '%Y/%m/%d') + datetime.timedelta(days=1)).strftime('%Y/%m/%d')
            # 找到下一个工作日后，直接选取生产时间开始点，组合后转换成时间戳返回
            new_datetime_string = date + ' ' + working_periods[0][0]
            return str_to_datetime(new_datetime_string)
        else:
            # 到这里，说明当天是工作日，先循环一遍工作时间区间，如果时间在工作时间区间，则直接返回本身，不做处理
            for period in working_periods:
                if period[0] <= time < period[1]:
                    return dt
            # 经过前面的循环，说明时间不在工作时间范围内，因此需要找到接近的下一个工作时间区间开始点
            is_find = False
            for period in working_periods:
                if period[0] > time:
                    new_time = period[0]
                    is_find = True
                    break
            if is_find:
                new_datetime_string = date + ' ' + new_time
                return str_to_datetime(new_datetime_string)
            else:
                # 到这里说明这个时间点在工作日下班后，则用下一个工作日的开始生产时间来作为计算日期
                new_date = (datetime.datetime.strptime(date, '%Y/%m/%d') + datetime.timedelta(days=1)).strftime('%Y/%m/%d')
                new_time = working_periods[0][0]
                new_datetime_string = new_date + ' ' + new_time
                # 返回时注意到如果下一天是非工作日，那么需要基于这个时间继续寻找正确的下一个生产开始时间点，用递归的方式调用本函数返回
                return find_next_prod_start(str_to_datetime(new_datetime_string))

    # 定义函数，如果当前时间戳是非生产时间，寻找上一个生产时间结束点，否则就返回本身
    def find_previous_prod_end(dt):
        date, time = datetime_to_str(dt).split(' ')
        if date in no_working_days:
            while date in no_working_days:
                # 循环找前一天，直到找到生产日期为止
                date = (datetime.datetime.strptime(date, '%Y/%m/%d') + datetime.timedelta(days=-1)).strftime('%Y/%m/%d')
            # 找到前一个工作日后，直接选取最后一段生产时间结束点，组合后转换成时间戳返回
            new_time = working_periods[-1][1]
            if new_time >= '24:00:00':
                # 这说明当天工作最后一段时间到24点结束，直接返回下一天0点
                return datetime.datetime.strptime(date, '%Y/%m/%d') + datetime.timedelta(days=1)
            else:
                # 这说明当天工作最后一段时间不到24点，直接拼接日期和时间，转换成时间戳返回
                new_datetime_string = date + ' ' + new_time
                return str_to_datetime(new_datetime_string)
        else:
            # 这说明当天就是生产日，先循环一遍工作时间区间，如果时间在工作时间区间，则直接返回，不做处理
            for period in working_periods:
                if period[0] <= time < period[1]:
                    return dt
            # 经过前面的循环未返回，说明时间不在工作时间范围内，那么寻找前一段生产时间的结束时间返回
            is_find = False
            for period in reversed(working_periods):
                # 倒着往前找
                if period[1] <= time:
                    new_time = period[1]
                    is_find = True
                    break
            if is_find:
                new_datetime_string = date + ' ' + new_time
                return str_to_datetime(new_datetime_string)
            else:
                # 到这里说明这个时间点在上班时间之前，那么，需要找到前一个工作日的生产结束时间点返回
                new_date = (datetime.datetime.strptime(date, '%Y/%m/%d') + datetime.timedelta(days=-1)).strftime('%Y/%m/%d')
                new_time = working_periods[-1][1]
                if new_time < '24:00:00':
                    new_datetime_string = new_date + ' ' + new_time
                    # 返回时注意到前一天也是非工作日的情况，那么需要基于这个时间继续寻找正确的上一个生产开始时间点，用递归的方式调用本函数返回
                    return find_previous_prod_end(str_to_datetime(new_datetime_string))
                else:
                    # 如果生产结束时间在24点，为了避免死循环，单独编写这种情况寻找上一个生产结束时间点的代码
                    # 找到确定的上一个生产日，然后因为是24:00:00，需要加到下一天0点
                    while new_date in no_working_days:
                        new_date = (datetime.datetime.strptime(new_date, '%Y/%m/%d') + datetime.timedelta(days=-1)).strftime('%Y/%m/%d')
                    # 找到确定的上一个生产日后，直接返回下一天0点
                    return datetime.datetime.strptime(new_date, '%Y/%m/%d') + datetime.timedelta(days=1)

    from_dt = find_next_prod_start(from_dt)
    to_dt = find_previous_prod_end(to_dt)

    # 本来已经交换开始结束时间，如果经过前面的处理后，大小顺序改变了，说明两个时间戳之间都是非生产时间，直接返回差值0
    if from_dt >= to_dt:
        return 0

    # 生成统计每个生产时段对应的秒数的列表
    working_seconds = []
    for index, period in enumerate(working_periods):
        if index < len(working_periods) -1:
            # 不到最后一个区间，不用判断结束时间是否写成24点
            working_seconds.append((datetime.datetime.strptime(period[1], '%H:%M:%S')-datetime.datetime.strptime(period[0], '%H:%M:%S')).total_seconds())
        else:
            # 已到最后一个区间，判断结束是否写成24点，如果写成24点计算方法稍作调整
            if period[1] < '24:00:00':
                working_seconds.append((datetime.datetime.strptime(period[1], '%H:%M:%S') - datetime.datetime.strptime(period[0], '%H:%M:%S')).total_seconds())
            else:
                working_seconds.append((datetime.datetime.strptime('00:00:00', '%H:%M:%S') + datetime.timedelta(days=1) - datetime.datetime.strptime(period[0], '%H:%M:%S')).total_seconds())

    # 计算工作日总工作时间
    prod_seconds_daily = sum(working_seconds)

    # 定义函数，计算根据时间'%H:%M:%S'计算0点到此时刻所经历的工时秒数
    def cal_prod_seconds_to_time(t):
        prod_seconds = 0
        for index, period in enumerate(working_periods):
            if t < period[0]:
                break
            elif period[0] <= t < period[1]:
                prod_seconds += (datetime.datetime.strptime(t, '%H:%M:%S') - datetime.datetime.strptime(period[0], '%H:%M:%S')).total_seconds()
                break
            else:
                prod_seconds += working_seconds[index]
        return prod_seconds


    '''开始计算两个时间戳之间相差的纯粹生产时间，以秒计
    算法如下：判断两个时间戳是否在同一天，
    如果在同一天：计算当天0点到两个时间戳，分别经历了多少纯生产时间；将两个数相减，即可得到两个时间戳之间相隔的生产时间
    如果不在同一天：计算开始时间点到当天24点之间的纯生产时间，再计算结束时间戳当天的0点到结束时间点之间的纯生产时间，再计算中间相隔的整天包含了多少个生产日，用生产天数*每天的纯工作时间，计算这部分时间，三部分相加得到两个时间戳之间的纯生产时间
    '''

    from_date, from_time = datetime_to_str(from_dt).split(' ')
    to_date, to_time = datetime_to_str(to_dt).split(' ')

    if from_date == to_date:
        diff_seconds = cal_prod_seconds_to_time(to_time) - cal_prod_seconds_to_time(from_time)
        return diff_seconds
    else:
        # 开始和结束不在同一天，分三部分来计算
        # 开始时间到当天24点的所有工作秒数, 用一天的总工作时间减去从0点到当前时间点的秒数
        diff_seconds_part1 = prod_seconds_daily - cal_prod_seconds_to_time(from_time)
        # 结束时间当天0点到结束时间点之间的工作秒数
        diff_seconds_part2 = cal_prod_seconds_to_time(to_time)
        # 统计这两个时间戳中间间隔的整天，有多少个工作日，从而计算出这期间的工时秒数。例如9月6号和9月4号减出来是2，但是中间间隔的整天只有5号一天
        diff_whole_days = (datetime.datetime.strptime(to_date, '%Y/%m/%d') - datetime.datetime.strptime(from_date, '%Y/%m/%d')).days - 1
        # 再依次遍历非工作日，如果处于这两天之间的，还需要减掉相应的天数
        for day in no_working_days:
            if from_date < day < to_date:
                diff_whole_days -= 1
        # 计算相隔整工作日的工作秒数
        diff_seconds_part3 = prod_seconds_daily * diff_whole_days
        # 合计所有秒数并返回
        diff_seconds = diff_seconds_part1 + diff_seconds_part2 + diff_seconds_part3
        return diff_seconds



if __name__ == '__main__':
    import pandas as pd
    df = pd.read_excel('temp.xlsx')
    print(1)








