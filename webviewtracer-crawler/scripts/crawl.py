import docker
from pathlib import Path
import local_data_store
import os

def crawl():
    data_store = local_data_store.init()
    docker.create(os.path.join(data_store.data_directory, '..'))
    docker.wakeup(os.path.join(data_store.data_directory, '..'))

def setup_crawler_args():
    pass