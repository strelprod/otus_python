import json
import os
from string import Template


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


def is_report_exists(reports_dir, report_fname):
    for _, _, files in os.walk(reports_dir):
        if report_fname in files:
            return True
    return False
