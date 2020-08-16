from flask import g

import psycopg2

def get_connection():
    if 'db' not in g:
        g.db = psycopg2.connect(user = "postgres",
                                password = "hack2020",
                                host = "34.106.9.169",
                                port = "5432",
                                database = "culturefit")

    return g.db
