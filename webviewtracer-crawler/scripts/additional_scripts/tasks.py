import psycopg2
from celery_app import celery_app

DB_CONFIG = dict(
    database="vv8_backend",
    host="0.0.0.0",
    user="vv8",
    password="vv8",
    port="45432"
)

def get_db_connection():
    """Establishes a database connection."""
    return psycopg2.connect(**DB_CONFIG)

@celery_app.task
def process_fingerprinting_batch(package_names, offset, limit):
    """
    Fetches scripts for all whitelisted apps, processes them to extract
    unique fingerprinting APIs, and returns a dictionary mapping apps
    to their unique fingerprinting APIs.
    """
    conn = get_db_connection()
    cur = conn.cursor()

    # Fetch data from the database
    cur.execute("""
        SELECT apis, bucket_list, package_name
        FROM script_flow
        WHERE package_name = ANY(%s)
        ORDER BY id
        LIMIT %s OFFSET %s;
    """, (package_names, limit, offset))

    results = cur.fetchall()
    cur.close()
    conn.close()

    app_fingerprinting_data = {}

    for row in results:
        apis, bucket_list, package_name = row
        if package_name not in app_fingerprinting_data:
            app_fingerprinting_data[package_name] = set()

        for api, bucket in zip(apis, bucket_list):
            if "fingerprinting" in bucket:
                parts = api.split(",")
                if len(parts) > 2:
                    app_fingerprinting_data[package_name].add(parts[2])
    app_fingerprinting_data = {app: list(api_set) for app, api_set in app_fingerprinting_data.items()}

    return app_fingerprinting_data