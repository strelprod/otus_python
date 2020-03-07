from datetime import datetime
from collections import namedtuple
import os


LogFileData = namedtuple('Log_file', ['file_path', 'dt', 'file_type'])


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
                log_file_data = LogFileData(data[1], data[2], data[3])
    return log_file_data
