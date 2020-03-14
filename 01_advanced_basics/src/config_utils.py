import json
import logging


CONFIG = {
    "REPORT_SIZE": 1000,
    "REPORT_DIR": "./reports",
    "LOG_DIR": "./log"
}


def read_config(config_path):
    try:
        with open(config_path, 'r', encoding='utf-8') as conf:
            config_from_file = json.load(conf)
        return config_from_file
    except FileNotFoundError:
        logging.error(f"Config file not found: {config_path}")
        raise FileNotFoundError(f"Config file not found: {config_path}")
    except json.decoder.JSONDecodeError as e:
        logging.error(f"Failed parse json config: {config_path}")
        raise json.decoder.JSONDecodeError(
            f"Failed parse json config: {config_path}", 
            e.doc,
            e.pos
        )


def prepare_config(config_path, config_base=CONFIG):
    updated_conf = config_base.copy()
    config_from_file = read_config(config_path)
    updated_conf.update(config_from_file)
    return updated_conf
