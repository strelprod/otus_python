import json
import os
from string import Template
import logging
import shutil
from datetime import datetime


REPORT_TPL = "report-{}.html"
JS_FILE = 'jquery.tablesorter.min.js'


def save_report_tpl(report_dir, 
                    report_fname, 
                    report_tpl, 
                    data):
    report_file = os.path.join(report_dir, report_fname)
    report_tpl_filled = report_tpl.safe_substitute(table_json=json.dumps(data))
    with open(report_file + '_tmp', 'w+', encoding='utf-8') as report:
        report.write(report_tpl_filled)
    os.rename(report_file + '_tmp', report_file)


def get_report_tpl():
    with open('./report_tpl/report.html', 'r', encoding='utf-8') as report_default:
        tmplt = report_default.read()
    report_tpl = Template(tmplt)
    return report_tpl


def save_report(report_dir, report_fname, data):
    if not os.path.exists(report_dir):
        os.makedirs(report_dir)
    shutil.copyfile(f'./report_tpl/{JS_FILE}', 
                    os.path.join(report_dir, JS_FILE))
    report_tpl = get_report_tpl()
    save_report_tpl(report_dir, report_fname, report_tpl, data)


def get_report_fname(fpath, dt, report_tpl=REPORT_TPL):
    dt = datetime.strftime(dt, '%Y.%m.%d')
    report_fname = report_tpl.format(dt)
    is_report_exists(fpath, report_fname)
    return report_fname


def is_report_exists(reports_dir, report_fname):
    fpath = os.path.join(reports_dir, report_fname)
    if os.path.exists(fpath):
        logging.error(f"Report {fpath} already exists")
        raise AssertionError(f"Report {fpath} already exists")
