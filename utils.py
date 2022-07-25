def chunks(lst):
    start = 0
    new_list = []
    for i in range(len(lst) // 6 + 1):
        stop = start + 6
        new_list.append(lst[start:stop])
        start = stop
    return new_list


def increment_month(date):
    month = int(date.split('/')[1])
    if month == 12:
        return int(date.split('/')[0]), 1, int(date.split('/')[2]) + 1

    else:
        print(date.split('/')[0], month + 1, date.split('/')[2])
        return int(date.split('/')[0]), month + 1, int(date.split('/')[2])


def increment_year(date):
    year = int(date.split('/')[2])
    return int(date.split('/')[0]), int(date.split('/')[1]), year + 1


def decrement_month(date):
    month = int(date.split('/')[1])
    if month == 1:
        return int(date.split('/')[0]), 12, int(date.split('/')[2]) - 1

    else:
        return int(date.split('/')[0]), month - 1, int(date.split('/')[2])


def decrement_year(date):
    year = int(date.split('/')[2])
    return int(date.split('/')[0]), int(date.split('/')[1]), year - 1