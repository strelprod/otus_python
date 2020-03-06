import json


def prepare_config(config_base, config_path):
    updated_conf = config_base.copy()
    if config_path:
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config_from_file = json.load(f)
        except OSError:
            print(f"File not found: {config_path}")
            return
        except json.decoder.JSONDecodeError as e:
            print(f"Failed parse config: {config_path}")
            return
        except Exception as e:
            print(f"Unknown exception: {str(e)}")
            return
        updated_conf.update(config_from_file)
    return updated_conf
