import json
import os
from string import Template
import logging
import shutil


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
        with open(report_file, 'w+', encoding='utf-8') as report:
            report.write(
                report_tpl.safe_substitute(table_json=json.dumps(data))
            )
    except KeyError:
        logging.error("table_json field not found in report template")
        return
    except OSError as e:
        logging.error(f"File not found: {str(e)}")
        return
    except BaseException:
        logging.exception("Unknown exception with save report")
        return
    else:
        return True


def is_report_exists(reports_dir, report_fname):
    try:
        report_fpath = os.path.join(reports_dir, report_fname)
        report = open(report_fpath, 'r')
    except OSError:
        return False
    else:
        report.close()
        return True
