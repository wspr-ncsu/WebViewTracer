import psycopg2
import concurrent.futures
import pandas as pd
import json
import os
import sys

import warnings
warnings.filterwarnings("ignore")

pii_regexes = [
    ( "[0-9]+\\.com\\.android\\.vending", "Play store package version"),
    ("b6580686-37c0-4795-a359-1be4299bbc99", "Advertising ID"),
    ("ranchu|YWJmYXJtLXJlbGVhc2UtcmJlLTY0LTIwMDQtMDA5Mw|4451a071126e0f0928f52e0c83ac43a668b19ca08c9f00045868a6980f7d7926", "Kernel build version"),
    ("r-8891092928c26a74-hmvm|YjUtMC41LTk4MjU3MDY|9b16fe4332fd89b46ef57bff04f7496bc704461e221b9af1c6b142678804d3a2","Bootloader version"),
    ("Pixel 6a|pixel6a|UGl4ZWwgNGE|cGl4ZWw0YQ|6e16ca4e4cd0c660a56e991c62151392ff5f79254f526290dc448a99471c1b2f","Device model"),
    ("emu64x|YnJhbWJsZQ|8f564af39fab12a40644275ed6ac20d772908228e9c667ad420dee1a54264b47","Device code name"),
    ("TE1A\\.240213\\.009|VFEzQS4yMzA5MDEuMDAx|b74ef2dbb937a4507932dff897f9759fde769df401d1ba509f531ffa6cc07df6"," Build ID"),
    ("[bB]attery|YmF0dGVyeQ|QmF0dGVyeQ","Battery level"),
    ("[pP]artition|cGFydGl0aW9u|UGFydGl0aW9u","Partition space"),
    ("[mM]emory|bWVtb3J5Cg|TWVtb3J5","Memory space"),
    ("192\\.58\\.122\\.|100\\.84\\.104\\.89|100\\.108\\.84\\.3|100\\.115\\.113\\.14|100\\.126\\.4\\.61","Internal IP-related info"),
    ("latitude|longitude|lat=|lon=","Location"),
    ("North\\+Carolina\\+State\\+University|North%20Carolina%20State%20University|Tm9ydGggQ2Fyb2xpbmEgU3RhdGUgVW5pdmVyc2l0eQ","Network Provider"),
    ("[rR]aleigh|UmFsZWlnaA","City"),
    ("Sodium Chromium|Sodium%20Chromium|SodiumChloride|chloride|U29kaXVt|c29kaXVt","Name"),
    ("afma-sdk-a-v|YWZtYS1zZGstYS12", "AdMob SDK version"),
    ("27606|27607|Mjc2MDY|Mjc2MDc","Zip code")
]

def get_connection():
    """
    Establish a connection to the PostgreSQL database.
    """
    try:
        conn = psycopg2.connect(
            dbname="vv8_backend",
            user="vv8",
            password="vv8",  # Replace with your actual password
            host="localhost",
            port="5439"
        )
        return conn
    except Exception as e:
        print(f"Error connecting to the database: {e}")
        return None

def results(): 
    conn = get_connection()
    if conn is None:
        print("Failed to connect to the database.")
        sys.exit(1)
        
    def query(statement: str):
        return pd.read_sql_query(statement, con=conn)
            
    total_apps = int(query('SELECT COUNT(DISTINCT package_name) FROM logfile')['count'][0])

    print(f"Total apps crawled: {total_apps}")

    def get_log_ids(query_statement: str):
        #print(f"Executing query: {query_statement}")
        return set(query(query_statement)['log_id'])

    def directly_get_app_names(query_statement: str):
        #print(f"Executing query: {query_statement}")
        return set(query(query_statement)['package_name'])

    def get_app_names(log_ids):
        if not log_ids:
            return set()
        #print(f"Aggregating app names for log_ids")
        log_id_list = ','.join(map(str, log_ids))
        query_statement = f"SELECT DISTINCT package_name FROM script_flow WHERE log_id IN ({log_id_list})"
        return set(query(query_statement)['package_name'])

    def process_query(query_tuple):
        query_part, description = query_tuple
        
        query_statement_inj_1 = f"SELECT DISTINCT app_name as package_name FROM injection_log WHERE source_code ~* '{query_part}'"
        query_statement_inj_2 = f"SELECT log_id FROM java_args WHERE java_arg ~* '{query_part}'"
        query_statement_exfil_1 = f"SELECT log_id FROM java_exfil WHERE url_query ~* '{query_part}' OR url_path ~* '{query_part}'"
        query_statement_exfil_2 = f"SELECT log_id FROM exfil WHERE url_query ~* '{query_part}' OR url_path ~* '{query_part}' OR payload ~* '{query_part}'"
                
        inj_apps = directly_get_app_names(query_statement_inj_1)
        inj_apps |= get_app_names(get_log_ids(query_statement_inj_2))
        exfil_apps = get_app_names(get_log_ids(query_statement_exfil_1))
        exfil_apps |= get_app_names(get_log_ids(query_statement_exfil_2))
        
        
        app_names = inj_apps & exfil_apps


        os.system(f"mkdir -p './results/{description}'")
        json.dump(list(app_names), open('./results/' + description+'/app_names_intersecting.json', 'w'))
        json.dump(list(exfil_apps), open('./results/' + description+'/app_names_exfil.json', 'w'))
        json.dump(list(inj_apps), open('./results/' + description+'/app_names_inj.json', 'w'))
        
        count = len(app_names)
        exfil_total = len(exfil_apps)
        inj_total = len(inj_apps)
        inj_exfil_percentage = (count / total_apps * 100) if total_apps > 0 else 0
        exfil_percentage = (exfil_total / total_apps * 100) if total_apps > 0 else 0
        inj_percentage = (inj_total / total_apps * 100) if total_apps > 0 else 0
        
        return description, count, exfil_total, inj_total, f"{inj_percentage:.2f}%", f"{exfil_percentage:.2f}%", f"{inj_exfil_percentage:.2f}%"

    with concurrent.futures.ThreadPoolExecutor() as executor:
        res = list(executor.map(process_query, pii_regexes))

    df = pd.DataFrame(res, columns=['Description', 'Count', 'Exfil Total', 'Inj Total', 'Inj %', 'Exfil %', 'Inj & Exfil %'])
    df = df.sort_values(by='Count', ascending=False)
    df.to_csv('./results/results.csv', index=False)
    print(df)

    