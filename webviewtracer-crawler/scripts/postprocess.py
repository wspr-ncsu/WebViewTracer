import argparse
from typing import List
import requests
import local_data_store
import docker
import csv
from datetime import datetime
import time

class Postprocesser:
    def __init__(
            self,
            output_format: str,
            post_processors: str):
        self.output_format = output_format
        self.post_processors = post_processors
        self.prefetch_count = 128
        self.data_store = local_data_store.init()
        if self.data_store.server_type == 'local':
            docker.wakeup(self.data_store.data_directory)



    def postprocess(self, packagenames: List[str])-> str:
        r = None
        submission_identifiers = []
        for packagename in packagenames:
            packagename = packagename.rstrip('\n')
            r = None

            if self.post_processors:
                print({
                    'packagename': packagename,
                    'rerun': True,
                    'parser_config': {
                        'parser': self.post_processors,
                        'output_format': self.output_format,
                        }
                    })
                r = requests.post(  f'http://{self.data_store.hostname}:4000/api/v1/appsubmit', json={
                    'packagename': packagename,
                    'rerun': True,
                    'parser_config': {
                        'parser': self.post_processors,
                        'output_format': self.output_format,
                        },
                    })
            else:
                r = requests.post(  f'http://{self.data_store.hostname}:4000/api/v1/appsubmit', json={
                    'packagename': packagename,
                    'rerun': True
                })
            submission_id = r.json()['submission_id']
            submission_identifiers.append((submission_id, packagename, datetime.now()))
        self.data_store.db.executemany('INSERT INTO submissions VALUES ( ?, ?, ? )', submission_identifiers)
        self.data_store.commit()

def postprocesser( args: argparse.Namespace):
    output_format = args.output_format
    parsers = args.post_processors
    pp = Postprocesser(
        output_format,
        parsers)
    if args.packagename:
        pp.postprocess([ args.packagename ])
    elif args.file:
        with open(args.file, 'r') as f:
            urls = f.readlines()
            pp.postprocess(urls)
    else:
        raise Exception('No url or file specified') # This should never happen, cause arg parser should show an error if neithier url or file is specified

def postprocessor_parse_args(crawler_arg_parser: argparse.ArgumentParser):
    app_names = crawler_arg_parser.add_mutually_exclusive_group(required=True)
    app_names.add_argument('-p', '--packagename', help='package to crawl')
    app_names.add_argument('-f', '--file', help='file containing list of urls to crawl seperated by newlines')
    crawler_arg_parser.add_argument('-pp', '--post-processors', help='Post processors to run on the crawled url')
    crawler_arg_parser.add_argument('-o', '--output-format', help='Output format to use for the parsed data', default='postgresql')