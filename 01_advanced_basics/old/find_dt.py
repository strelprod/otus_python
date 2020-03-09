import re
from datetime import datetime
import os

x = "xxx" \
    "yyy"
print(x)
exit(0)


log_file_regex = r'nginx-access-ui\.log-([0-9]{8})(\.gz|$)'
log_file_pat = re.compile(log_file_regex)


def parse_logfile(fname, log_file_pat):
    parsed = log_file_pat.search(fname)
    if parsed:
        return parsed.group(0), parsed.group(1), parsed.group(2)
    return ()

            
def get_logfiles(logs_dir, log_file_pat):
    curr_dt = datetime.now()
    for path, _, files in os.walk(logs_dir):
        for fname in files:
            parsed = parse_logfile(fname, log_file_pat)
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
                log_file_data = Log_file(data[1], data[2], data[3])
    return log_file_data


def is_report_exists(reports_dir, report_file):
    for _, _, files in os.walk(reports_dir):
        if report_file in files:
            return True
    return False
from collections import namedtuple       
Log_file = namedtuple('Log_file', ['file_path', 'dt', 'file_type'])
log_file_data = find_last_logfile('./log', log_file_pat)
print(log_file_data)
report_tpl = "report-{}.html"
if log_file_data:
    report_file = report_tpl.format(datetime.strftime(log_file_data.dt, '%Y.%m.%d'))
    rprt_exists = is_report_exists('./reports', report_file)
    if rprt_exists:
        print("СУЩЕСТВУЕТ")
    else:
        print("НЕ СУЩЕСТВУЕТ")
