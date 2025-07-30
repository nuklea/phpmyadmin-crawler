import argparse
import csv
import sys
from urllib.parse import urlencode

import requests
from lxml import html


class Crawler:
    def __init__(self, base_url):
        self.base_url = base_url
        self.session = requests.Session()

    def get_login_form(self):
        response = self.session.get(self.base_url)
        response.raise_for_status()

        doc = html.fromstring(response.content)
        form = doc.get_element_by_id('login_form')

        action = form.get('action')
        inputs = dict(
            (inp.get('name'), inp.get('value') or '')
            for inp in form.xpath('.//input[@name]')
        )
        return response.url + action, inputs

    def login(self, user, password):
        action, inputs = self.get_login_form()

        inputs['pma_username'] = user
        inputs['pma_password'] = password

        response = self.session.post(action, data=inputs)
        response.raise_for_status()
        return response

    def extract_data(self, database, table):
        query = urlencode({'route': '/sql', 'server': 1, 'db': database, 'table': table, 'pos': 0})
        response = self.session.get(self.base_url + f'/index.php?{query}')
        response.raise_for_status()
        doc = html.fromstring(response.content)

        table = doc.xpath('//table[contains(@class, "table_results")]')[0]
        headers = [th.get('data-column') for th in table.xpath('.//th[@data-column]')]

        rows = []
        for tr in table.xpath('.//tbody/tr'):
            cells = [td.text_content().strip() for td in tr.xpath('.//td[@data-type]')]
            rows.append(dict(zip(headers, cells)))

        return headers, rows


def build_parser():
    parser = argparse.ArgumentParser(description="Парсер аргументов для подключения к БД через phpMyAdmin")
    parser.add_argument('-U', '--url', default='http://185.244.219.162/phpmyadmin',
                        help='URL phpMyAdmin (по умолчанию %(default)s)')
    parser.add_argument('-u', '--user', default='test', help='Имя пользователя (по умолчанию %(default)s)')
    parser.add_argument('-p', '--password', required=True, help='Пароль пользователя (обязательно)')
    parser.add_argument('-d', '--database', default='testDB', help='Имя базы данных (по умолчанию %(default)s)')
    parser.add_argument('-t', '--table', default='users', help='Имя таблицы (по умолчанию %(default)s)')
    return parser


if __name__ == '__main__':
    args = build_parser().parse_args()
    crawler = Crawler(args.url)
    crawler.login(args.user, args.password)
    headers, rows = crawler.extract_data(args.database, args.table)

    writer = csv.writer(sys.stdout)
    writer.writerow(headers)

    for row in rows:
        writer.writerow([row.get(col, '') for col in headers])
