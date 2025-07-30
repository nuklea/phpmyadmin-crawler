## phpMyAdmin crawler

Python-скрипт, который через HTTP-запросы авторизуется в
интерфейсе phpMyAdmin и извлекает содержимое из указанной базы данных и таблицы.

### Установка
```bash
$ pip install poetry
$ poetry env use python
$ poetry install
```

### Как запустить
```bash
$ ./crawler.py -p password 
```
