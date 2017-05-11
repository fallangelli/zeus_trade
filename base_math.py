import numpy as np
import pandas as pd

VALID_15_TIME_LABELS = ['09:45', '10:00', '10:15', '10:30', '10:45', '11:00', '11:15', '11:30',
                        '13:15', '13:30', '13:45', '14:00', '14:15', '14:30', '14:45', '15:00']
VALID_30_TIME_LABELS = ['10:00', '10:30', '11:00', '11:30', '13:30', '14:00', '14:30', '15:00']

# (当日收盘价*2+前一日EMA(12)*11)/13
def ema(x: list, n, l=None):
    ema_list = []
    for i in range(0, len(x)):
        if i == 0:
            if l is None:
                ema_list.append(x[i])
            else:
                y = (2 * x[i] + (n - 1) * l) / (n + 1)
                ema_list.append(y)
        else:
            y = (2 * x[i] + (n - 1) * ema_list[i - 1]) / (n + 1)
            ema_list.append(y)
    return ema_list


def dif(x: list, ema_short, ema_long):
    dif_list = []
    for i in range(len(x)):
        y = ema_short[i] - ema_long[i]
        dif_list.append(y)
    return dif_list


# 前一日DEA * 8/10 + 今日DIF * 2/10
def dea(x: list, dif_date, n=9, dea_l=None):
    dea_list = []
    for i in range(0, len(x)):
        if i == 0:
            if dea_l is None:
                dea_list.append(0)
            else:
                y = (dea_l * (n - 1) + 2 * dif_date[i]) / (n + 1)
                dea_list.append(y)
        else:
            y = (dea_list[i - 1] * (n - 1) + 2 * dif_date[i]) / (n + 1)
            dea_list.append(y)
    return dea_list


# 　　（DIF-DEA）*2
def macd(d: list, x: list, n=9, short_n=12, long_n=26, short_l=None, long_l=None, dea_l=None):
    ema_short = ema(x, short_n, short_l)
    ema_long = ema(x, long_n, long_l)
    dif_data = dif(x, ema_short, ema_long)
    dea_data = dea(x, dif_data, n, dea_l)
    macd_data = []
    for i in range(0, len(x)):
        val = (dif_data[i] - dea_data[i]) * 2
        macd_data.append(val)

    ret_frame = pd.DataFrame({'date': d, 'ema_short': ema_short, 'ema_long': ema_long,
                              'dif': dif_data, 'dea': dea_data, 'macd': macd_data})
    return ret_frame


def cross(backward_a: list, backward_b: list):
    size_a = len(backward_a)
    size_b = len(backward_b)
    if size_a <= 1 or size_b <= 1:
        return False
    if backward_a[0] >= backward_b[0] and backward_a[1] <= backward_b[1]:
        return True
    if backward_a[0] <= backward_b[0] and backward_a[1] >= backward_b[1]:
        return True
    return False


def up_cross(backward_a: list, backward_b: list):
    size_a = len(backward_a)
    size_b = len(backward_b)
    if size_a <= 1 or size_b <= 1:
        return False
    if backward_a[0] >= backward_b[0] and backward_a[1] <= backward_b[1]:
        return True
    return False


def last_cross(backward_a: list, backward_b: list):
    size_a = len(backward_a)
    size_b = len(backward_b)
    ret_val = 0
    i = 0
    if size_a > 1 or size_b > 1:
        if backward_a[0] > backward_b[0]:
            while i < size_a and i < size_b and backward_a[0] < backward_b[0]:
                i = i + 1
            ret_val = i
        if backward_a[0] < backward_b[0]:
            while i < size_a and i < size_b and backward_a[0] > backward_b[0]:
                i = i + 1
            ret_val = i
        if backward_a[0] == backward_b[0]:
            ret_val = i
    return ret_val


def last_greater_0(x: list):
    size = len(x)
    ret_val = -1
    if size <= 1 or x[0] >= 0:
        ret_val = -1

    i = 1
    while i < size - 1:
        if x[i] >= 0:
            ret_val = i
        i = i + 1

    return ret_val


def count_up_cross(backward_a: list, backward_b: list, count):
    size_a = len(backward_a)
    size_b = len(backward_b)
    if size_a <= 1 or size_b <= 1:
        return 0

    ret_count = 0
    i = 0
    tmp_a = backward_a
    tmp_b = backward_b
    while i < size_a - 1 and i < size_b - 1 and i < count:
        if up_cross(tmp_a, tmp_b):
            ret_count = ret_count + 1
        tmp_a = np.delete(tmp_a, 0)
        tmp_b = np.delete(tmp_b, 0)
        i = i + 1

    return ret_count


def if_times(time, k_type):
    str_time = time[time.index(':') - 2: len(time)]
    ret_val = False
    if k_type == '15':
        ret_val = str_time in VALID_15_TIME_LABELS;
    if k_type == '30':
        ret_val = str_time in VALID_30_TIME_LABELS;
    return ret_val


if __name__ == '__main__':
    #    dif_list = DIF(df['close'])
    #    dea_list = DEA(df['close'], dif_list)
    close = [6.38, 6.38, 6.4, 6.4, 6.38]
    ema_list = ema(close, 26, 6.695306)
    print(ema_list)
