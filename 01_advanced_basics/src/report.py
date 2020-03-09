import json
import os
from string import Template
import logging
import shutil


REPORT_TPL = "report-{}.html"


def save_report(report_dir, report_fname, data):
    if not os.path.exists(report_dir):
        os.makedirs(report_dir)
    try:
        js_file = 'jquery.tablesorter.min.js'
        shutil.copyfile(f'./report_tpl/{js_file}', os.path.join(report_dir, js_file))
        with open('./report_tpl/report.html', 'r', encoding='utf-8') as report_default:
            tmplt = report_default.read()
        report_tpl = Template(tmplt)
        report_file = os.path.join(report_dir, report_fname)
        report_tpl_filled = report_tpl.safe_substitute(table_json=json.dumps(data))
        with open(report_file, 'w+', encoding='utf-8') as report:
            report.write(report_tpl_filled)
        return True
    except KeyError:
        raise KeyError("table_json field not found in report template")
    except FileNotFoundError as e:
        raise FileNotFoundError(str(e))


def is_report_exists(reports_dir, report_fname):
    return os.path.exists(os.path.join(reports_dir, report_fname))
