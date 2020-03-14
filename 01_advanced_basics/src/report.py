import json
import os
from string import Template
import logging
import shutil
from datetime import datetime


REPORT_TPL = "report-{}.html"


def copy_file_to_report_dir(report_dir, fname):
    fpath = os.path.join(report_dir, fname)
    if not is_file_exists(fpath):
        shutil.copyfile(f'./report_tpl/{fname}', fpath)


def save_report_tpl(report_dir, 
                    report_fname, 
                    report_tpl, 
                    data):
    report_file = os.path.join(report_dir, report_fname)
    report_tpl_filled = report_tpl.safe_substitute(table_json=json.dumps(data))
    with open(report_file, 'w+', encoding='utf-8') as report:
        report.write(report_tpl_filled)


def get_report_tpl():
    with open('./report_tpl/report.html', 'r', encoding='utf-8') as report_default:
            tmplt = report_default.read()
    report_tpl = Template(tmplt)
    return report_tpl


def save_report(report_dir, report_fname, data):
    if not os.path.exists(report_dir):
        os.makedirs(report_dir)
    try:
        js_file = 'jquery.tablesorter.min.js'
        copy_file_to_report_dir(report_dir, js_file)
        report_tpl = get_report_tpl()
        save_report_tpl(report_dir, report_fname, report_tpl, data)
    except KeyError:
        logging.error("table_json field not found in report template")
        raise KeyError("table_json field not found in report template")
    except FileNotFoundError as e:
        logging.error(str(e))
        raise FileNotFoundError(str(e))


def get_report_fname(fpath, dt, report_tpl=REPORT_TPL):
    dt = datetime.strftime(dt, '%Y.%m.%d')
    report_fname = report_tpl.format(dt)
    is_report_exists(fpath, report_fname)
    return report_fname


def is_file_exists(fpath):
    return os.path.exists(fpath)


def is_report_exists(reports_dir, report_fname):
    fpath = os.path.join(reports_dir, report_fname)
    if is_file_exists(fpath):
        logging.error(f"Report {fpath} already exists")
        raise AssertionError(f"Report {fpath} already exists")
