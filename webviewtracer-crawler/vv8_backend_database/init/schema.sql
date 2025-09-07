--


CREATE EXTENSION IF NOT EXISTS pg_trgm;



CREATE TYPE script_genesis AS ENUM (
    'unknown',
    'static',
    'eval',
    'include',
    'insert',
    'write_include',
    'write_insert'
);



CREATE TABLE IF NOT EXISTS adblock (
    id integer NOT NULL,
    url text NOT NULL,
    origin text NOT NULL,
    blocked boolean NOT NULL,
    package_name text
);




CREATE SEQUENCE adblock_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;




ALTER SEQUENCE adblock_id_seq OWNED BY adblock.id;



CREATE TABLE IF NOT EXISTS create_elements (
    id integer NOT NULL,
    logfile_id integer NOT NULL,
    visit_domain text NOT NULL,
    security_origin text NOT NULL,
    script_hash bytea NOT NULL,
    script_offset integer NOT NULL,
    tag_name text NOT NULL,
    create_count integer NOT NULL
);




CREATE SEQUENCE create_elements_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;




ALTER SEQUENCE create_elements_id_seq OWNED BY create_elements.id;



CREATE TABLE IF NOT EXISTS exfil (
    id integer NOT NULL,
    isolate text NOT NULL,
    script_url text,
    evaled_by integer,
    url_hostname text,
    url_port text,
    url_path text,
    url_query text,
    url_protocol text,
    first_origin text,
    package_name text,
    log_id integer,
    type text,
    mock_time integer,
    payload text,
    script_hash bytea,
    evaled_by_hash bytea,
    identif text,
    evaled_by_uuid text,
    api text,
    pii_identified text[]
);




CREATE TABLE IF NOT EXISTS exfil_eval (
    exfil_id integer NOT NULL,
    reviewer text,
    label text,
    correct_pii text[],
    CONSTRAINT exfil_eval_label_check CHECK ((label = ANY (ARRAY['TP'::text, 'TN'::text, 'FP'::text, 'FN'::text])))
);


CREATE SEQUENCE experimental_flow_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;




ALTER SEQUENCE experimental_flow_id_seq OWNED BY exfil.id;



CREATE TABLE IF NOT EXISTS feature_usage (
    id integer NOT NULL,
    logfile_id integer NOT NULL,
    visit_domain text NOT NULL,
    security_origin text NOT NULL,
    script_hash bytea NOT NULL,
    script_offset integer NOT NULL,
    feature_name text NOT NULL,
    feature_use character(1) NOT NULL,
    use_count integer NOT NULL
);




CREATE SEQUENCE feature_usage_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;




ALTER SEQUENCE feature_usage_id_seq OWNED BY feature_usage.id;



CREATE TABLE IF NOT EXISTS frida_log (
    id integer NOT NULL,
    app_name text,
    action text,
    js_object_id text,
    thirdparty_library text[],
    java_func text,
    parameters text[],
    stacktrace text,
    is_3p boolean
);




CREATE SEQUENCE frida_log_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;




ALTER SEQUENCE frida_log_id_seq OWNED BY frida_log.id;



CREATE TABLE IF NOT EXISTS injection_eval (
    injection_id integer NOT NULL,
    reviewer text,
    label text,
    correct_pii text[],
    CONSTRAINT injection_eval_label_check CHECK ((label = ANY (ARRAY['TP'::text, 'TN'::text, 'FP'::text, 'FN'::text])))
);


CREATE TABLE IF NOT EXISTS injection_log (
    id integer NOT NULL,
    app_name text,
    function_name text,
    url text,
    source_code text,
    sha256 bytea NOT NULL,
    thirdparty_library text[],
    ishtmlspoofing boolean,
    isloadurlleakage boolean,
    is_3p boolean,
    pii_identified text[]
);




CREATE SEQUENCE injection_log_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;




ALTER SEQUENCE injection_log_id_seq OWNED BY injection_log.id;



CREATE TABLE IF NOT EXISTS java_args (
    identif text,
    mock_time integer,
    apioffset integer,
    evaled_by_uuid text,
    log_id integer,
    sha256 bytea,
    api text,
    java_arg text,
    pii_identified text[]
);




CREATE TABLE IF NOT EXISTS java_exfil (
    mock_time integer,
    apioffset integer,
    log_id integer,
    sha256 bytea,
    api text,
    url_host text,
    url_protocol text,
    url_query text,
    url_path text,
    identif text,
    evaled_by_uuid text,
    pii_identified text[]
);




CREATE TABLE IF NOT EXISTS js_api_features_summary (
    logfile_id integer NOT NULL,
    all_features json NOT NULL
);




CREATE TABLE IF NOT EXISTS logfile (
    id integer NOT NULL,
    mongo_oid bytea NOT NULL,
    uuid text NOT NULL,
    root_name text NOT NULL,
    size bigint NOT NULL,
    lines integer NOT NULL,
    submissionid text,
    package_name text
);




CREATE SEQUENCE logfile_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;




ALTER SEQUENCE logfile_id_seq OWNED BY logfile.id;



CREATE TABLE IF NOT EXISTS mega_features (
    id integer NOT NULL,
    sha256 bytea NOT NULL,
    full_name text NOT NULL,
    receiver_name text,
    member_name text,
    idl_base_receiver text,
    idl_member_role character(1)
);




CREATE SEQUENCE mega_features_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;




ALTER SEQUENCE mega_features_id_seq OWNED BY mega_features.id;



CREATE TABLE IF NOT EXISTS mega_features_import_schema (
    sha256 bytea NOT NULL,
    full_name text NOT NULL,
    receiver_name text,
    member_name text,
    idl_base_receiver text,
    idl_member_role character(1)
);




CREATE TABLE IF NOT EXISTS mega_instances (
    id integer NOT NULL,
    instance_hash bytea NOT NULL,
    logfile_id integer,
    script_id integer,
    isolate_ptr text NOT NULL,
    runtime_id integer NOT NULL,
    origin_url_id integer,
    script_url_id integer,
    eval_parent_hash bytea
);




CREATE SEQUENCE mega_instances_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;




ALTER SEQUENCE mega_instances_id_seq OWNED BY mega_instances.id;



CREATE TABLE IF NOT EXISTS mega_instances_import_schema (
    instance_hash bytea NOT NULL,
    logfile_id integer,
    script_id integer,
    isolate_ptr text NOT NULL,
    runtime_id integer NOT NULL,
    origin_url_sha256 bytea,
    script_url_sha256 bytea,
    eval_parent_hash bytea
);




CREATE TABLE IF NOT EXISTS mega_scripts (
    id integer NOT NULL,
    sha2 bytea NOT NULL,
    sha3 bytea NOT NULL,
    size integer NOT NULL
);




CREATE SEQUENCE mega_scripts_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;




ALTER SEQUENCE mega_scripts_id_seq OWNED BY mega_scripts.id;



CREATE TABLE IF NOT EXISTS mega_scripts_import_schema (
    sha2 bytea NOT NULL,
    sha3 bytea NOT NULL,
    size integer NOT NULL
);




CREATE TABLE IF NOT EXISTS mega_usages (
    instance_id integer NOT NULL,
    feature_id integer NOT NULL,
    origin_url_id integer NOT NULL,
    usage_offset integer NOT NULL,
    usage_mode character(1) NOT NULL,
    usage_count integer NOT NULL
);




CREATE TABLE IF NOT EXISTS mega_usages_import_schema (
    instance_id integer NOT NULL,
    feature_id integer NOT NULL,
    origin_url_sha256 bytea NOT NULL,
    usage_offset integer NOT NULL,
    usage_mode character(1) NOT NULL,
    usage_count integer NOT NULL
);




CREATE TABLE IF NOT EXISTS multi_origin_api_names (
    id integer NOT NULL,
    objectid integer NOT NULL,
    origin text NOT NULL,
    api_name text NOT NULL
);




CREATE SEQUENCE multi_origin_api_names_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;




ALTER SEQUENCE multi_origin_api_names_id_seq OWNED BY multi_origin_api_names.id;



CREATE SEQUENCE multi_origin_api_names_objectid_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;




ALTER SEQUENCE multi_origin_api_names_objectid_seq OWNED BY multi_origin_api_names.objectid;



CREATE TABLE IF NOT EXISTS multi_origin_obj (
    id integer NOT NULL,
    objectid integer NOT NULL,
    origins text[] NOT NULL,
    num_of_origins integer NOT NULL,
    urls text[] NOT NULL
);




CREATE SEQUENCE multi_origin_obj_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;




ALTER SEQUENCE multi_origin_obj_id_seq OWNED BY multi_origin_obj.id;



CREATE SEQUENCE multi_origin_obj_objectid_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;




ALTER SEQUENCE multi_origin_obj_objectid_seq OWNED BY multi_origin_obj.objectid;



CREATE TABLE IF NOT EXISTS page_captcha_systems (
    id integer NOT NULL,
    page_mongo_oid bytea NOT NULL,
    logfile_mongo_oid bytea NOT NULL,
    captcha_systems jsonb NOT NULL
);




CREATE SEQUENCE page_captcha_systems_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;




ALTER SEQUENCE page_captcha_systems_id_seq OWNED BY page_captcha_systems.id;



CREATE TABLE IF NOT EXISTS poly_feature_usage (
    id integer NOT NULL,
    logfile_id integer NOT NULL,
    visit_domain text NOT NULL,
    security_origin text NOT NULL,
    script_hash bytea NOT NULL,
    script_offset integer NOT NULL,
    feature_name text NOT NULL,
    feature_use character(1) NOT NULL,
    use_count integer NOT NULL
);




CREATE SEQUENCE poly_feature_usage_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;




ALTER SEQUENCE poly_feature_usage_id_seq OWNED BY poly_feature_usage.id;



CREATE TABLE IF NOT EXISTS script_blobs (
    id integer NOT NULL,
    script_hash bytea NOT NULL,
    script_code text NOT NULL,
    sha256sum bytea NOT NULL,
    size integer NOT NULL
);




CREATE SEQUENCE script_blobs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;




ALTER SEQUENCE script_blobs_id_seq OWNED BY script_blobs.id;



CREATE TABLE IF NOT EXISTS script_causality (
    id integer NOT NULL,
    logfile_id integer NOT NULL,
    child_hash bytea NOT NULL,
    genesis script_genesis DEFAULT 'unknown'::script_genesis NOT NULL,
    parent_hash bytea,
    by_url text,
    parent_cardinality integer,
    child_cardinality integer,
    child_uuid text,
    parent_uuid text,
    packagename text,
    isiframe boolean,
    parentisiframe boolean
);




CREATE SEQUENCE script_causality_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;




ALTER SEQUENCE script_causality_id_seq OWNED BY script_causality.id;



CREATE TABLE IF NOT EXISTS script_creation (
    id integer NOT NULL,
    isolate_ptr text,
    logfile_id integer NOT NULL,
    visit_domain text NOT NULL,
    script_hash bytea NOT NULL,
    script_url text,
    runtime_id integer,
    first_origin text,
    eval_parent_hash bytea
);




CREATE SEQUENCE script_creation_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;




ALTER SEQUENCE script_creation_id_seq OWNED BY script_creation.id;



CREATE TABLE IF NOT EXISTS script_flow (
    id integer NOT NULL,
    isolate text NOT NULL,
    log_id integer,
    visiblev8 boolean NOT NULL,
    mock_time integer,
    code text NOT NULL,
    first_origin text,
    sha256 bytea NOT NULL,
    arguments text[] NOT NULL,
    bucket_list text[],
    url text,
    apis text[] NOT NULL,
    evaled_by integer,
    package_name text,
    inj_func_name text,
    java_apis text[],
    java_args text[],
    java_ret_val text[],
    identif text,
    is_injection boolean,
    evaled_by_uuid text
);




CREATE SEQUENCE script_flow_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;




ALTER SEQUENCE script_flow_id_seq OWNED BY script_flow.id;



CREATE TABLE IF NOT EXISTS submissions (
    id character varying(36) NOT NULL,
    start_time timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    end_time timestamp without time zone,
    packagename text NOT NULL,
    vv8_req_id text NOT NULL,
    log_parser_req_id text,
    postprocessor_used text,
    postprocessor_output_format text,
    mongo_id text
);




CREATE TABLE IF NOT EXISTS thirdpartyfirstparty (
    id integer NOT NULL,
    sha2 bytea NOT NULL,
    root_domain text NOT NULL,
    url text NOT NULL,
    first_origin text NOT NULL,
    property_of_root_domain text NOT NULL,
    property_of_first_origin text NOT NULL,
    property_of_script text NOT NULL,
    is_script_third_party_with_root_domain boolean NOT NULL,
    is_script_third_party_with_first_origin boolean NOT NULL,
    script_origin_tracking_value double precision NOT NULL
);




CREATE SEQUENCE thirdpartyfirstparty_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;




ALTER SEQUENCE thirdpartyfirstparty_id_seq OWNED BY thirdpartyfirstparty.id;



CREATE TABLE IF NOT EXISTS urls (
    id integer NOT NULL,
    sha256 bytea NOT NULL,
    url_full text,
    url_scheme text,
    url_hostname text,
    url_port text,
    url_path text,
    url_query text,
    url_etld1 text,
    url_stemmed text
);




CREATE SEQUENCE urls_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;




ALTER SEQUENCE urls_id_seq OWNED BY urls.id;



CREATE TABLE IF NOT EXISTS urls_import_schema (
    id integer NOT NULL,
    sha256 bytea NOT NULL,
    url_full text,
    url_scheme text,
    url_hostname text,
    url_port text,
    url_path text,
    url_query text,
    url_etld1 text,
    url_stemmed text
);




CREATE SEQUENCE urls_import_schema_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;




ALTER SEQUENCE urls_import_schema_id_seq OWNED BY urls_import_schema.id;



CREATE TABLE IF NOT EXISTS user_data (
    username character varying(255) NOT NULL,
    password character varying(255),
    apps jsonb
);




CREATE TABLE IF NOT EXISTS xleaks (
    id integer NOT NULL,
    isolate text NOT NULL,
    visiblev8 boolean NOT NULL,
    first_origin text,
    url text,
    evaled_by integer
);




CREATE SEQUENCE xleaks_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;




ALTER SEQUENCE xleaks_id_seq OWNED BY xleaks.id;



ALTER TABLE ONLY adblock ALTER COLUMN id SET DEFAULT nextval('adblock_id_seq'::regclass);



ALTER TABLE ONLY create_elements ALTER COLUMN id SET DEFAULT nextval('create_elements_id_seq'::regclass);



ALTER TABLE ONLY exfil ALTER COLUMN id SET DEFAULT nextval('experimental_flow_id_seq'::regclass);



ALTER TABLE ONLY feature_usage ALTER COLUMN id SET DEFAULT nextval('feature_usage_id_seq'::regclass);



ALTER TABLE ONLY frida_log ALTER COLUMN id SET DEFAULT nextval('frida_log_id_seq'::regclass);



ALTER TABLE ONLY injection_log ALTER COLUMN id SET DEFAULT nextval('injection_log_id_seq'::regclass);



ALTER TABLE ONLY logfile ALTER COLUMN id SET DEFAULT nextval('logfile_id_seq'::regclass);



ALTER TABLE ONLY mega_features ALTER COLUMN id SET DEFAULT nextval('mega_features_id_seq'::regclass);



ALTER TABLE ONLY mega_instances ALTER COLUMN id SET DEFAULT nextval('mega_instances_id_seq'::regclass);



ALTER TABLE ONLY mega_scripts ALTER COLUMN id SET DEFAULT nextval('mega_scripts_id_seq'::regclass);



ALTER TABLE ONLY multi_origin_api_names ALTER COLUMN id SET DEFAULT nextval('multi_origin_api_names_id_seq'::regclass);



ALTER TABLE ONLY multi_origin_api_names ALTER COLUMN objectid SET DEFAULT nextval('multi_origin_api_names_objectid_seq'::regclass);



ALTER TABLE ONLY multi_origin_obj ALTER COLUMN id SET DEFAULT nextval('multi_origin_obj_id_seq'::regclass);



ALTER TABLE ONLY multi_origin_obj ALTER COLUMN objectid SET DEFAULT nextval('multi_origin_obj_objectid_seq'::regclass);



ALTER TABLE ONLY page_captcha_systems ALTER COLUMN id SET DEFAULT nextval('page_captcha_systems_id_seq'::regclass);



ALTER TABLE ONLY poly_feature_usage ALTER COLUMN id SET DEFAULT nextval('poly_feature_usage_id_seq'::regclass);



ALTER TABLE ONLY script_blobs ALTER COLUMN id SET DEFAULT nextval('script_blobs_id_seq'::regclass);



ALTER TABLE ONLY script_causality ALTER COLUMN id SET DEFAULT nextval('script_causality_id_seq'::regclass);



ALTER TABLE ONLY script_creation ALTER COLUMN id SET DEFAULT nextval('script_creation_id_seq'::regclass);



ALTER TABLE ONLY script_flow ALTER COLUMN id SET DEFAULT nextval('script_flow_id_seq'::regclass);



ALTER TABLE ONLY thirdpartyfirstparty ALTER COLUMN id SET DEFAULT nextval('thirdpartyfirstparty_id_seq'::regclass);



ALTER TABLE ONLY urls ALTER COLUMN id SET DEFAULT nextval('urls_id_seq'::regclass);



ALTER TABLE ONLY urls_import_schema ALTER COLUMN id SET DEFAULT nextval('urls_import_schema_id_seq'::regclass);



ALTER TABLE ONLY xleaks ALTER COLUMN id SET DEFAULT nextval('xleaks_id_seq'::regclass);



ALTER TABLE ONLY adblock
    ADD CONSTRAINT adblock_pkey PRIMARY KEY (id);



ALTER TABLE ONLY create_elements
    ADD CONSTRAINT create_elements_pkey PRIMARY KEY (id);



ALTER TABLE ONLY exfil_eval
    ADD CONSTRAINT exfil_eval_pkey PRIMARY KEY (exfil_id);



ALTER TABLE ONLY exfil
    ADD CONSTRAINT experimental_flow_pkey PRIMARY KEY (id);



ALTER TABLE ONLY feature_usage
    ADD CONSTRAINT feature_usage_pkey PRIMARY KEY (id);



ALTER TABLE ONLY frida_log
    ADD CONSTRAINT frida_log_pkey PRIMARY KEY (id);



ALTER TABLE ONLY injection_eval
    ADD CONSTRAINT injection_eval_pkey PRIMARY KEY (injection_id);



ALTER TABLE ONLY injection_log
    ADD CONSTRAINT injection_log_pkey PRIMARY KEY (id);



ALTER TABLE ONLY logfile
    ADD CONSTRAINT logfile_pkey PRIMARY KEY (id);



ALTER TABLE ONLY logfile
    ADD CONSTRAINT logfile_uuid_key UNIQUE (uuid);



ALTER TABLE ONLY mega_features_import_schema
    ADD CONSTRAINT mega_features_import_schema_pkey PRIMARY KEY (sha256);



ALTER TABLE ONLY mega_features
    ADD CONSTRAINT mega_features_pkey PRIMARY KEY (id);



ALTER TABLE ONLY mega_features
    ADD CONSTRAINT mega_features_sha256_key UNIQUE (sha256);



ALTER TABLE ONLY mega_instances_import_schema
    ADD CONSTRAINT mega_instances_import_schema_instance_hash_key UNIQUE (instance_hash);



ALTER TABLE ONLY mega_instances
    ADD CONSTRAINT mega_instances_instance_hash_key UNIQUE (instance_hash);



ALTER TABLE ONLY mega_instances
    ADD CONSTRAINT mega_instances_pkey PRIMARY KEY (id);



ALTER TABLE ONLY mega_scripts_import_schema
    ADD CONSTRAINT mega_scripts_import_schema_pkey PRIMARY KEY (sha2, sha3, size);



ALTER TABLE ONLY mega_scripts
    ADD CONSTRAINT mega_scripts_pkey PRIMARY KEY (id);



ALTER TABLE ONLY mega_scripts
    ADD CONSTRAINT mega_scripts_sha2_sha3_size_key UNIQUE (sha2, sha3, size);



ALTER TABLE ONLY mega_usages_import_schema
    ADD CONSTRAINT mega_usages_import_schema_pkey PRIMARY KEY (instance_id, feature_id, origin_url_sha256, usage_offset, usage_mode);



ALTER TABLE ONLY mega_usages
    ADD CONSTRAINT mega_usages_pkey PRIMARY KEY (instance_id, feature_id, origin_url_id, usage_offset, usage_mode);



ALTER TABLE ONLY multi_origin_api_names
    ADD CONSTRAINT multi_origin_api_names_pkey PRIMARY KEY (id);



ALTER TABLE ONLY multi_origin_obj
    ADD CONSTRAINT multi_origin_obj_pkey PRIMARY KEY (id);



ALTER TABLE ONLY page_captcha_systems
    ADD CONSTRAINT page_captcha_systems_pkey PRIMARY KEY (id);



ALTER TABLE ONLY poly_feature_usage
    ADD CONSTRAINT poly_feature_usage_pkey PRIMARY KEY (id);



ALTER TABLE ONLY script_blobs
    ADD CONSTRAINT script_blobs_pkey PRIMARY KEY (id);



ALTER TABLE ONLY script_causality
    ADD CONSTRAINT script_causality_pkey PRIMARY KEY (id);



ALTER TABLE ONLY script_creation
    ADD CONSTRAINT script_creation_pkey PRIMARY KEY (id);



ALTER TABLE ONLY script_flow
    ADD CONSTRAINT script_flow_pkey PRIMARY KEY (id);



ALTER TABLE ONLY submissions
    ADD CONSTRAINT submissions_pkey PRIMARY KEY (id);



ALTER TABLE ONLY thirdpartyfirstparty
    ADD CONSTRAINT thirdpartyfirstparty_pkey PRIMARY KEY (id);



ALTER TABLE ONLY urls_import_schema
    ADD CONSTRAINT urls_import_schema_pkey PRIMARY KEY (id);



ALTER TABLE ONLY urls_import_schema
    ADD CONSTRAINT urls_import_schema_sha256_key UNIQUE (sha256);



ALTER TABLE ONLY urls
    ADD CONSTRAINT urls_pkey PRIMARY KEY (id);



ALTER TABLE ONLY urls
    ADD CONSTRAINT urls_sha256_key UNIQUE (sha256);



ALTER TABLE ONLY user_data
    ADD CONSTRAINT user_data_pkey PRIMARY KEY (username);



ALTER TABLE ONLY xleaks
    ADD CONSTRAINT xleaks_pkey PRIMARY KEY (id);



CREATE INDEX idx_script_flow_package_name ON script_flow USING btree (package_name);



CREATE INDEX idx_source_code_trgm ON injection_log USING gin (source_code gin_trgm_ops);



CREATE INDEX java_arg_idx ON java_args USING gin (java_arg gin_trgm_ops);



CREATE INDEX java_url_path_idx ON java_exfil USING gin (url_path gin_trgm_ops);



CREATE INDEX java_url_query_idx ON java_exfil USING gin (url_query gin_trgm_ops);



CREATE INDEX payload_idx ON exfil USING gin (payload gin_trgm_ops);



CREATE INDEX script_flow_log_id_idx ON script_flow USING btree (log_id);



CREATE INDEX source_code_idx ON script_flow USING gin (code gin_trgm_ops);



CREATE INDEX url_path_idx ON exfil USING gin (url_path gin_trgm_ops);



CREATE INDEX url_query_idx ON exfil USING gin (url_query gin_trgm_ops);



ALTER TABLE ONLY create_elements
    ADD CONSTRAINT create_elements_logfile_id_fkey FOREIGN KEY (logfile_id) REFERENCES logfile(id);



ALTER TABLE ONLY feature_usage
    ADD CONSTRAINT feature_usage_logfile_id_fkey FOREIGN KEY (logfile_id) REFERENCES logfile(id);



ALTER TABLE ONLY js_api_features_summary
    ADD CONSTRAINT js_api_features_summary_logfile_id_fkey FOREIGN KEY (logfile_id) REFERENCES logfile(id);



ALTER TABLE ONLY mega_instances_import_schema
    ADD CONSTRAINT mega_instances_import_schema_logfile_id_fkey FOREIGN KEY (logfile_id) REFERENCES logfile(id);



ALTER TABLE ONLY mega_instances_import_schema
    ADD CONSTRAINT mega_instances_import_schema_script_id_fkey FOREIGN KEY (script_id) REFERENCES mega_scripts(id);



ALTER TABLE ONLY mega_instances
    ADD CONSTRAINT mega_instances_logfile_id_fkey FOREIGN KEY (logfile_id) REFERENCES logfile(id);



ALTER TABLE ONLY mega_instances
    ADD CONSTRAINT mega_instances_origin_url_id_fkey FOREIGN KEY (origin_url_id) REFERENCES urls(id);



ALTER TABLE ONLY mega_instances
    ADD CONSTRAINT mega_instances_script_id_fkey FOREIGN KEY (script_id) REFERENCES mega_scripts(id);



ALTER TABLE ONLY mega_instances
    ADD CONSTRAINT mega_instances_script_url_id_fkey FOREIGN KEY (script_url_id) REFERENCES urls(id);



ALTER TABLE ONLY mega_usages
    ADD CONSTRAINT mega_usages_feature_id_fkey FOREIGN KEY (feature_id) REFERENCES mega_features(id);



ALTER TABLE ONLY mega_usages_import_schema
    ADD CONSTRAINT mega_usages_import_schema_feature_id_fkey FOREIGN KEY (feature_id) REFERENCES mega_features(id);



ALTER TABLE ONLY mega_usages_import_schema
    ADD CONSTRAINT mega_usages_import_schema_instance_id_fkey FOREIGN KEY (instance_id) REFERENCES mega_instances(id);



ALTER TABLE ONLY mega_usages
    ADD CONSTRAINT mega_usages_instance_id_fkey FOREIGN KEY (instance_id) REFERENCES mega_instances(id);



ALTER TABLE ONLY mega_usages
    ADD CONSTRAINT mega_usages_origin_url_id_fkey FOREIGN KEY (origin_url_id) REFERENCES urls(id);



ALTER TABLE ONLY poly_feature_usage
    ADD CONSTRAINT poly_feature_usage_logfile_id_fkey FOREIGN KEY (logfile_id) REFERENCES logfile(id);



ALTER TABLE ONLY script_causality
    ADD CONSTRAINT script_causality_logfile_id_fkey FOREIGN KEY (logfile_id) REFERENCES logfile(id);



ALTER TABLE ONLY script_creation
    ADD CONSTRAINT script_creation_logfile_id_fkey FOREIGN KEY (logfile_id) REFERENCES logfile(id);




