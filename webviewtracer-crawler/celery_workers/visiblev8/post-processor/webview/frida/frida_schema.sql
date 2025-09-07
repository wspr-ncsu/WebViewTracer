CREATE TABLE IF NOT EXISTS frida_log (
    id SERIAL PRIMARY KEY NOT NULL,
    app_name TEXT,
    action TEXT,
    js_object_id TEXT,
    java_func TEXT,
    parameters TEXT[],
    stacktrace TEXT
);