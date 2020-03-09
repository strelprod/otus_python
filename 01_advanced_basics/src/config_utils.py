import json
import logging


CONFIG = {
    "REPORT_SIZE": 1000,
    "REPORT_DIR": "./reports",
    "LOG_DIR": "./log","LOGGER_FILE": "./logdata.log"
}


def prepare_config(config_base, config_path, log_formatter=None):
    updated_conf = config_base.copy()
    if config_path:
        try:
            with open(config_path, 'r', encoding='utf-8') as conf:
                config_from_file = json.load(conf)
        except FileNotFoundError:
            raise FileNotFoundError(f"Config file not found: {config_path}")
        except json.decoder.JSONDecodeError as e:          
            raise json.decoder.JSONDecodeError(
                f"Failed parse json config: {config_path}", 
                e.doc,
                e.pos
            )
        
        updated_conf.update(config_from_file)

        if log_formatter and "LOGGER_FILE" in updated_conf:
            try:
                root_logger = logging.getLogger()
                file_handler = logging.FileHandler(updated_conf['LOGGER_FILE'])
                file_handler.setFormatter(log_formatter)
                root_logger.addHandler(file_handler)
            except FileNotFoundError:
                msg = "Logger_file using in config not found: {}"
                raise FileNotFoundError(msg.format(updated_conf['LOGGER_FILE']))

    return updated_conf
