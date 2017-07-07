# coding:utf-8
import numpy as np

VALID_15_TIME_LABELS = ['09:45', '10:00', '10:15', '10:30', '10:45', '11:00', '11:15', '11:30',
                        '13:15', '13:30', '13:45', '14:00', '14:15', '14:30', '14:45', '15:00']
VALID_30_TIME_LABELS = ['10:00', '10:30', '11:00', '11:30', '13:30', '14:00', '14:30', '15:00']


def cross(backward_a, backward_b):
    size_a = len(backward_a)
    size_b = len(backward_b)
    if size_a <= 1 or size_b <= 1:
        return False
    if backward_a[0] >= backward_b[0] and backward_a[1] <= backward_b[1]:
        return True
    if backward_a[0] <= backward_b[0] and backward_a[1] >= backward_b[1]:
        return True
    return False


def up_cross(backward_a, backward_b):
    size_a = len(backward_a)
    size_b = len(backward_b)
    if size_a <= 1 or size_b <= 1:
        return False
    if backward_a[0] > backward_b[0] and backward_a[1] <= backward_b[1]:
        return True
    return False


def down_cross(backward_a, backward_b):
    size_a = len(backward_a)
    size_b = len(backward_b)
    if size_a <= 1 or size_b <= 1:
        return False
    if backward_a[0] < backward_b[0] and backward_a[1] >= backward_b[1]:
        return True
    return False


def last_cross(backward_a, backward_b):
    size_a = len(backward_a)
    size_b = len(backward_b)
    ret_val = 0
    i = 0
    if size_a > 1 or size_b > 1:
        if backward_a[0] > backward_b[0]:
            while i < size_a and i < size_b and backward_a[i] >= backward_b[i]:
                i = i + 1
            ret_val = i
        if backward_a[0] < backward_b[0]:
            while i < size_a and i < size_b and backward_a[i] <= backward_b[i]:
                i = i + 1
            ret_val = i
        if backward_a[0] == backward_b[0]:
            ret_val = i
    return ret_val


def last_greater_0(x):
    size = len(x)
    ret_val = -1
    if size <= 1 or x[0] > 0:
        ret_val = -1
    i = 1
    while i < size - 1:
        if x[i] >= 0:
            ret_val = i
            break
        else:
            i = i + 1

    return ret_val


def last_less_0(x):
    size = len(x)
    ret_val = -1
    if size <= 1 or x[0] < 0:
        ret_val = -1
    i = 1
    while i < size - 1:
        if x[i] <= 0:
            ret_val = i
            break
        else:
            i = i + 1

    return ret_val


def count_up_cross(backward_a, backward_b, count):
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


def count_down_cross(backward_a, backward_b, count):
    size_a = len(backward_a)
    size_b = len(backward_b)
    if size_a <= 1 or size_b <= 1:
        return 0

    ret_count = 0
    i = 0
    tmp_a = backward_a
    tmp_b = backward_b
    while i < size_a - 1 and i < size_b - 1 and i < count:
        if down_cross(tmp_a, tmp_b):
            ret_count = ret_count + 1
        tmp_a = np.delete(tmp_a, 0)
        tmp_b = np.delete(tmp_b, 0)
        i = i + 1

    return ret_count


def if_times(time, k_type):
    str_time = time[time.index(':') - 2: len(time)]
    ret_val = False
    if k_type == '15':
        ret_val = str_time in VALID_15_TIME_LABELS
    if k_type == '30':
        ret_val = str_time in VALID_30_TIME_LABELS
    return ret_val


if __name__ == '__main__':
    close = [6.38, 6.38, 6.4, 6.4, 6.38]
    print(close)
