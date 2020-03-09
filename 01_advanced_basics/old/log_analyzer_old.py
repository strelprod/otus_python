#!/usr/bin/env python
# -*- coding: utf-8 -*-


# log_format ui_short '$remote_addr  $remote_user $http_x_real_ip [$time_local] "$request" '
#                     '$status $body_bytes_sent "$http_referer" '
#                     '"$http_user_agent" "$http_x_forwarded_for" "$http_X_REQUEST_ID" "$http_X_RB_USER" '
#                     '$request_time';

config = {
    "REPORT_SIZE": 1000,
    "REPORT_DIR": "./reports",
    "LOG_DIR": "./log"
}

"""
+функцию, которая будет парсить лог желательно сделать генератором.

не забывайте про кодировки, когда читаете лог и пишите отчет.

из функции, которая будет искать последний лог удобно возвращать 
namedtuple с указанием пути до него, распаршенной через datetime даты 
из имени файла и расширением, например.

распаршенная дата из имени логфайла пригодится, чтобы составить путь до отчета, 
это можно сделать "за один присест", не нужно проходится по всем файлам и что-то искать.

+протестируйте функцию поиска лога, она не должна возвращать .bz2 файлы и т.п. Этого можно добиться правильной регуляркой.

найти самый свежий лог можно за один проход по файлам, без использования glob, сортировки и т.п.

+ нужный открыватель лога (open/gzip.open) перед парсингом можно выбрать через тернарный оператор.

+ проверка на превышение процента ошибок при парсинге выполняетя один раз, в конце чтения файла, а не на каждую строчку/ошибку.
"""


from itertools import groupby
from collections import namedtuple
from statistics import mean, median
import gzip
import re

Log_file = namedtuple('Log_file', ['filepath', 'datetime', 'is_gzip'])

log_file_regex = r'nginx-access-ui\.log-([0-9]{8})\.(gz|$)'
log_file = re.compile(log_file_regex)

log_nginx_regex = r'\"(GET|POST|HEAD|PUT|DELETE|CONNECT|OPTIONS|TRACE|PATCH) (.+) (HTTP|http)\/\d+\.\d\".+(\d\.\d+)$'
log_nginx = re.compile(log_nginx_regex)


def get_url(url):
    return url[0]


def get_url_stats(log_processed):
    url_agg = groupby(log_processed, get_url)
    stats = []
    total_count = 0
    total_time = 0.0
    for key, group in url_agg:
        #TODO как лучше с генератором быь? прохожу много раз цикл
        group = list(group)

        count_ = len(group)
        time_sum = sum((vals[1] for vals in group))
        time_avg = mean((vals[1] for vals in group))
        time_avg = mean((vals[1] for vals in group))
        time_max = max((vals[1] for vals in group))
        time_med = median((vals[1] for vals in group))

        total_count += count_
        total_time += time_sum

        stats.append({
            'url': key,
            'count': count_,
            'count_perc': None,
            'time_sum': time_sum,
            'time_perc': None,
            'time_avg': time_avg,
            'time_max': time_max,
            'time_med': time_med
        })

    for i, _ in enumerate(stats):
        stats[i]['count_perc'] = stats[i]['count'] / total_count * 100
        stats[i]['time_perc'] = stats[i]['time_sum'] / total_time * 100
    print(stats)
    return stats


def parsing_log(file_obj):
    while True:
        file_content = file_obj.readline()
        if not file_content:
            break
        parse_line = log_nginx.search(file_content)
        try:
            url = parse_line.group(2)
            request_time = parse_line.group(4)
        except AttributeError:
            print('FAILED ROW:', file_content)
            yield None, None
        else:
            yield url, float(request_time)


def process_log(log_data):
    open_log = gzip.open if log_data.is_gzip else open
    failed_proc = 0.1
    total_lines = 0
    failed_parse_line = 0
    log_processed = {}
    try:
        with open_log(log_data.filepath, 'rt', encoding='us-ascii') as f:
        #with open_log(log_data.filepath, 'rt', encoding='utf-8') as f:
            for url, request_time in parsing_log(f):
                if url and request_time: 
                    if url in ["/api/v2/banner/26659584", "/api/v2/banner/26583670","/api/v2/banner/24860528","/api/v2/banner/25003697"]:
                        #log_processed.append((url, request_time))
                        if url not in log_processed:
                            log_processed[url] = [request_time]
                        else:
                            log_processed[url].append(request_time)
                else:
                    failed_parse_line += 1
                total_lines += 1
    except OSError:
        print("Failed open file, file not found")
        return
    print(total_lines)
    if total_lines == 0:
        print("Log file no contatins rows")
        return
    errors_cnt = failed_parse_line / total_lines
    if errors_cnt > failed_proc:
        print("FAILED PARSING", failed_parse_line / total_lines)
        return
    # print(log_processed)
    return log_processed


def find_logs():
    pass

#TODO
#проверка что директория с логами существует - fail если нет
#проверка что директория с отчетами существует - создать если нет
#проверка что отчет существует
#если отчета нет, то подставить в отчет данные https://docs.python.org/2/library/string.html#string.Template.safe_substitute
#поиск логов по дате
#
#

from time import time
"""
{"count": 251, "time_avg": 1.0089999999999999, "time_max": 2.8860000000000001, "time_sum": 253.33199999999999, "url": "/api/v2/banner/26659584", "time_med": 0.88600000000000001, "time_perc": 0.012999999999999999, "count_perc": 0.01}, 
{"count": 251, "time_avg": 1.0089999999999999, "time_max": 2.915, "time_sum": 253.316, "url": "/api/v2/banner/26583670", "time_med": 0.89500000000000002, "time_perc": 0.012999999999999999, "count_perc": 0.01}, 
{"count": 251, "time_avg": 1.0089999999999999, "time_max": 2.9060000000000001, "time_sum": 253.303, "url": "/api/v2/banner/24860528", "time_med": 0.90000000000000002, "time_perc": 0.012999999999999999, "count_perc": 0.01}, 
{"count": 251, "time_avg": 1.0089999999999999, "time_max": 2.702, "time_sum": 253.286, "url": "/api/v2/banner/25003697", "time_med": 0.94799999999999995, "time_perc": 0.012999999999999999, "count_perc": 0.01}]
"""
def main():
    # log_data = find_logs()
    # report_exists = check_report_for_log()
    t = time()
    import json
    """
    
    with open("xxx.json", "r") as fp:
        d = json.load(fp) 
    x = []
    for val in d:
        if val['url'] in ["/api/v2/banner/26659584", "/api/v2/banner/26583670","/api/v2/banner/24860528","/api/v2/banner/25003697"]:
            print(val)
    exit(0)
    """
    report_exists = False
    if report_exists:
        print("REPORT EXISTS")
        return
    log_data = Log_file('./log/nginx-access-ui.log-20170630.gz', 'x', True)
    print((time() - t)/60,time() - t, "PROC LOG")
    log_processed = process_log(log_data)
    print((time() - t)/60,time() - t, "GET STAT")
    stats = get_url_stats(log_processed)
    print((time() - t)/60,time() - t, "SAVE STAT")
    with open("xxx3.json", "w+") as fp:
        json.dump(stats , fp) 
    #print(stats)
    print((time() - t)/60,time() - t, 'DONE')

if __name__ == "__main__":
    main()