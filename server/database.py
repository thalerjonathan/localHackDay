import sqlite3
import hashlib


def db_connect(dbname='../database/database.db'):
    return sqlite3.connect(dbname)


def db_add_user(email, pass_plain, display_name):
    pass_hash = db_hash_password(pass_plain)

    conn = db_connect()

    with conn:
        cur = conn.cursor()
        cur.execute('INSERT INTO users(email, password_hash, display_name) VALUES(?)',
                    (email, pass_hash, display_name))


def db_get_user(email):
    conn = db_connect()

    with conn:
        cur = conn.cursor()
        cur.execute('SELECT email, password_hash, display_name '
                    'FROM users WHERE email = ?', email)
        return cur.fetchone()


def db_validate_user(email, pass_plain):
    row = db_get_user(email)

    if row:
        if row[1] == db_hash_password(pass_plain):
            return True

    return False


def db_user_exists(email):
    row = db_get_user(email)

    if row:
        return True

    return False


def db_hash_password(pass_plain):
    pass_utf8 = pass_plain.encode('utf-8')
    return hashlib.sha512(pass_utf8).hexdigest()

