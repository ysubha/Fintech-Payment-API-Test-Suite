import mysql.connector

from utils.helper import get_properties


def db_execution(query, values=None):
    db_connect = {
        'host': get_properties('SQL', 'host'),
        'database': get_properties('SQL', 'database'),
        'user': get_properties('SQL', 'user'),
        'password': get_properties('SQL', 'password')
    }
    db_connection = mysql.connector.connect(**db_connect)
    cursor = db_connection.cursor()
    cursor.execute("DELETE FROM " + get_properties('SQL', 'USER_TABLE'))
    cursor.execute("DELETE FROM " + get_properties('SQL', 'TRANSACTIONS_TABLE'))
    if values:
        cursor.execute(query, values)
    else:
        cursor.execute(query)
    db_connection.commit()
    cursor.close()
    db_connection.close()


def create_user_in_db(user_id, balance):
    table = get_properties('SQL', 'USER_TABLE')
    query = f'INSERT INTO {table} (user_id,balance) VALUES (%s, %s)'
    values = (user_id, balance)
    db_execution(query, values)


def insert_transaction_in_db(transaction):
    table = get_properties('SQL', 'TRANSACTIONS_TABLE')
    query = f'INSERT INTO {table} (txn_id, user_id, amount, type, status,payment_txn_id ,timestamp) VALUES (%s,%s,%s,%s,%s,%s,%s);'
    values = (
        transaction['txn_id'],
        transaction['user_id'],
        transaction['amount'],
        transaction['type'],
        transaction['status'],
        transaction.get('payment_txn_id'),
        transaction.get('timestamp'))
    db_execution(query,values)
