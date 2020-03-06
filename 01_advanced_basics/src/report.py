import json
import os
from string import Template
import logging


def save_report(report_dir, report_fname, data):
    if not os.path.exists(report_dir):
        os.makedirs(report_dir)
    try:
        with open('report.html', 'r', encoding='utf-8') as report_default:
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
        logging.exception("Unknown exception")
        return
    else:
        return True


def is_report_exists(reports_dir, report_fname):
    for _, _, files in os.walk(reports_dir):
        if report_fname in files:
            return True
    return False
