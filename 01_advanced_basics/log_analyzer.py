#!/usr/bin/env python
# -*- coding: utf-8 -*-


# log_format ui_short '$remote_addr  $remote_user $http_x_real_ip [$time_local] "$request" '
#                     '$status $body_bytes_sent "$http_referer" '
#                     '"$http_user_agent" "$http_x_forwarded_for" "$http_X_REQUEST_ID" "$http_X_RB_USER" '
#                     '$request_time';


from string import Template
from collections import namedtuple
from statistics import mean, median
from datetime import datetime
import gzip
import re
import os
import json
import argparse


LOG_FILE = namedtuple('Log_file', ['file_path', 'dt', 'file_type'])
LOG_FILE_REGEX = r'nginx-access-ui\.log-([0-9]{8})(\.gz|$)'
LOG_FILE_PAT = re.compile(LOG_FILE_REGEX)
LOG_NGINX_REGEX = r'\"(GET|POST|HEAD|PUT|DELETE|CONNECT|OPTIONS|TRACE|PATCH)' \
                  r' (.+) (HTTP|http)\/\d+\.\d\".+(\d\.\d+)$'
LOG_NGINX_PAT = re.compile(LOG_NGINX_REGEX)
REPORT_TPL = "report-{}.html"


config = {
    "REPORT_SIZE": 1000,
    "REPORT_DIR": "./reports",
    "LOG_DIR": "./log"
}


def save_report(report_dir, report_fname, data):
    if not os.path.exists(report_dir):
        os.makedirs(report_dir)
    try:
        with open('report.html', 'r', encoding='utf-8') as f:
            tmplt = f.read()
        s = Template(tmplt)
        report_file = os.path.join(report_dir, report_fname)
        with open(report_file, 'w+', encoding='utf-8') as f:
            f.write(s.safe_substitute(table_json=json.dumps(data)))
    except KeyError:
        print("table_json field not found in report template")
        return
    except OSError as e:
        print(f"File not found: {str(e)}")
        return
    except Exception as e:
        print(f"Unknown exception {str(e)}")
        return
    else:
        return True


def get_logs_stat(log_processed, limit=None):
    stats = []
    total_count = 0
    total_time = 0.0
    for url_stat in get_url_stats(log_processed):
        stats.append(url_stat)
        total_count += url_stat['count']
        total_time += url_stat['time_sum']
    for i, _ in enumerate(stats):
        stats[i]['count_perc'] = stats[i]['count'] / total_count * 100
        stats[i]['time_perc'] = stats[i]['time_sum'] / total_time * 100
    
    stats.sort(key=lambda k: k['time_sum'], reverse=True)

    if limit:
        return stats[:limit]
    return stats


def get_url_stats(log_processed):
    for url in log_processed:
        requests_times = log_processed[url]
        url_stat = {
            'url': url,
            'count': len(requests_times),
            'count_perc': None,
            'time_sum': sum(requests_times),
            'time_perc': None,
            'time_avg': mean(requests_times),
            'time_max': max(requests_times),
            'time_med': median(requests_times)
        }
        yield url_stat


def parsing_log(file_obj, log_nginx_pat):
    while True:
        file_content = file_obj.readline()
        if not file_content:
            break
        parse_line = log_nginx_pat.search(file_content)
        try:
            url = parse_line.group(2)
            request_time = parse_line.group(4)
        except AttributeError:
            yield None, None
        else:
            yield url, float(request_time)


def process_log(log_data, log_nginx_pat):
    allowed_errors_proc = 0.1
    total_lines = 0
    error_parse_line = 0
    log_processed = {}

    try:
        open_log = gzip.open if log_data.file_type == '.gz' else open
        f = open_log(log_data.file_path, 'rt', encoding='utf-8')
    except OSError:
        print(f"File not found: {log_data.file_path}")
        return

    for url, request_time in parsing_log(f, log_nginx_pat):
        total_lines += 1
        if url and request_time: 
            if url not in log_processed:
                log_processed[url] = [request_time]
            else:
                log_processed[url].append(request_time)
        else:
            error_parse_line += 1
    f.close()
    if total_lines == 0 or \
        ((error_parse_line / total_lines) > allowed_errors_proc):
        err_txt = "Failed proccess logs: total " \
                  "lines={}, errors={}, allowed_proc={}"
        print(err_txt.format(total_lines, 
                             error_parse_line, 
                             allowed_errors_proc))
        return {}
    return log_processed


def parse_log_file_name(fname, log_file_pat):
    parsed = log_file_pat.search(fname)
    if parsed:
        return parsed.group(0), parsed.group(1), parsed.group(2)
    return ()

            
def get_logfiles(logs_dir, log_file_pat):
    curr_dt = datetime.now()
    for path, _, files in os.walk(logs_dir):
        for fname in files:
            parsed = parse_log_file_name(fname, log_file_pat)
            if parsed:
                filepath = os.path.join(path, parsed[0])
                dt = datetime.strptime(parsed[1], '%Y%m%d')
                dt_diff = (curr_dt - dt).days
                yield dt_diff, filepath, dt, parsed[2]
            else:
                yield ()


def find_last_logfile(logs_dir, log_file_pat):
    min_dt_diff = float("inf")
    log_file_data = None
    for data in get_logfiles(logs_dir, log_file_pat):
        if data:
            if data[0] == 0:
                return data[1], data[2], data[3]
            if data[0] < min_dt_diff:
                min_dt_diff = data[0]
                log_file_data = LOG_FILE(data[1], data[2], data[3])
    return log_file_data


def is_report_exists(reports_dir, report_fname):
    for _, _, files in os.walk(reports_dir):
        if report_fname in files:
            return True
    return False


def prepare_config(config_base, config_path):
    updated_conf = config_base.copy()
    if config_path:
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config_from_file = json.load(f)
        except OSError:
            print(f"File not found: {config_path}")
            return
        except json.decoder.JSONDecodeError as e:
            print(f"Failed parse config: {config_path}")
            return
        except Exception as e:
            print(f"Unknown exception: {str(e)}")
            return
        updated_conf.update(config_from_file)
    return updated_conf


def parse_inpurt_args():
    parser = argparse.ArgumentParser(description='Process logs')
    parser.add_argument('--config', action="store", dest="config", 
                        default='', type=str,
                        help='input config in json format')
    args = parser.parse_args()
    return args

def main():
    try:
        print("Start main")
        inpurt_args = parse_inpurt_args()
        config_prepared = prepare_config(config, inpurt_args.config)
        if not config_prepared:
            return
        print("Done config_prepared")
        log_file_data = find_last_logfile(config_prepared['LOG_DIR'], 
                                          LOG_FILE_PAT)
        print("Done find_last_logfile")
        if log_file_data:
            dt = datetime.strftime(log_file_data.dt, '%Y.%m.%d')
            report_fname = REPORT_TPL.format(dt)
            if is_report_exists('./reports', report_fname):
                print("Report already exists")
                return
            log_processed = process_log(log_file_data, LOG_NGINX_PAT)
            print("Done process_log")
            if not log_processed:
                return
            logs_stat = get_logs_stat(log_processed, 
                                      config_prepared['REPORT_SIZE'])
            print("Done get_logs_stat")
            if save_report(config_prepared['REPORT_DIR'], 
                           report_fname, 
                           logs_stat):
                print("Done save_report")
            else:
                print("Failed save_report")
        else:
            print("Logs not found")
            return
    except Exception as e:
        print(f"unknown exception: {str(e)}")
    else:
        print("End main")
    return
    

if __name__ == "__main__":
    main()
