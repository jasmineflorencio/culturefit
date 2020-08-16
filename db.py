from flask import g

import configparser
import psycopg2

def get_connection():
    if 'db' not in g:
        config = configparser.ConfigParser()
        config.read('secrets.ini')

        g.db = psycopg2.connect(user = config['database']['user'],
                                password = config['database']['password'],
                                host = config['database']['host'],
                                port = config['database']['port'],
                                database = config['database']['database'])

    return g.db
