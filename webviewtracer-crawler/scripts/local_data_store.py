import sqlite3
import os
import json

class DataStore:
    def __init__(self, conn, data_directory: str):
        self.conn = conn
        self.db = conn.cursor()
        self.config = json.loads(self.db.execute('SELECT config FROM config').fetchone()[0])
        self.hostname = self.config['hostname']
        self.server_type = self.config['server_type']
        self.instance_count = self.config['instance_count']
        self.data_directory = data_directory
        self.raw_logs_dir = os.path.join(data_directory, '..' , 'raw_logs')
        self.crawl_data_dir = os.path.join(data_directory, '..', 'crawl_data')
        self.number_of_phones = self.config['number_of_phones'] if 'number_of_phones' in self.config else 1
    def commit(self):
        self.conn.commit()


def init():
    config_database_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), '.wvt.db')
    if not os.path.exists(config_database_path):
        help()
        os._exit(-1)
    conn = sqlite3.connect(config_database_path)
    return DataStore(conn, os.path.dirname(os.path.realpath(__file__)))

def setup(hostname: str, server_type: str = 'local', instance_count: int = 1, number_of_phones: int = 1):
    config_database_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), '.wvt.db')
    if os.path.exists(config_database_path):
        print('wvt-cli has already been setup')
        os._exit(-1)
    conn = sqlite3.connect(config_database_path)
    db = conn.cursor()
    db.execute('CREATE TABLE config (config TEXT)') # TEXT --> JSON
    db.execute('INSERT INTO config (config) VALUES (?)', (json.dumps({ 'hostname': hostname, 'server_type': server_type, 'instance_count': instance_count, 'number_of_phones': number_of_phones }),))
    db.execute('CREATE TABLE submissions (submission_id TEXT NOT NULL PRIMARY KEY, url TEXT, start_time timestamp)')
    conn.commit()

def help():
    print('wvt-cli has not been setup yet, please run `wvt-cli setup` to setup the cli according to your configurations')