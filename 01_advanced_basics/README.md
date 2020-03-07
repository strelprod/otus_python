# Log analyzer
## Структура проекта
Директория **log_analyzer** содержит модули для реализации задачи генерации отчета по логамю
Пакет **log_analyzer/log_analyzer.py** выполняет задачу, импортируя вспомогательные модули из src
* log_analyzer/src/config.py - обновление дефолтного конфига
* log_analyzer/src/find_logs.py - поиск наиболее свежего лога
* log_analyzer/src/parse_log.py - чтение и парсинг найденного лог файла
* log_analyzer/src/logs_stat.py - подсчет статистик по url для лог файла после парсинга
* log_analyzer/src/report.py - сохранение в файл отчета по статистике по логам*

В директории **log_analyzer/tests** содержатся unit-тесты для пакетов из **src**.
## Запуск обработки логов
Из корня директории 01_advanced_basics запуск:
```sh
$ python log_analyzer/log_analyzer.py
```
В результате работы программы формируется отчет в директории, которая задана в конфиге.

Скрипт принимаем опциональный параметр --config, в который передается json файл для переопределения конфига по-умолчанию.
Пример запуска: 
```sh
$ python log_analyzer/log_analyzer.py --config log_analyzer/test_conf.json
```
## Запуск тестов
Из корня директории 01_advanced_basics запуск:
```sh
$ python -m unittest discover -s log_analyzer
```