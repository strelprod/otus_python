import unittest
import json
import os
import sys

sys.path.append(os.path.realpath('.'))

from src import prepare_config


class TestConfig(unittest.TestCase):
    def setUp(self):
        self.config_default = {"key": "val"}
        self.config_priority = {"key": "new"}
        self.config_priority_fname = 'test_config.json'
        with open(self.config_priority_fname, 'w+', encoding='utf-8') as conf:
            json.dump(self.config_priority, conf)

    def tearDown(self):
        os.remove(self.config_priority_fname)

    def test_config_priority(self):
        upd_conf = prepare_config(self.config_default,
                                  self.config_priority_fname)
        self.assertDictEqual(upd_conf, self.config_priority)

    def test_existing_conf_file(self):
        self.assertRaises(FileNotFoundError, 
                          prepare_config,
                          self.config_default,
                          "fake_conf.json")


if __name__ == '__main__':
    unittest.main()
