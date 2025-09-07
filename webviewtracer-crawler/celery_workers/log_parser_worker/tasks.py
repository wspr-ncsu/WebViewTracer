from typing import Optional, TypedDict
from log_parser_worker.app import celery_app
import os
import glob
import fnmatch
import subprocess as sp
import shutil
import time

class ParserConfig(TypedDict):
    parser: str
    delete_log_after_parsing: bool
    output_format: Optional[str]

def remove_entry(filepath):
    if os.path.isdir(filepath):
        shutil.rmtree(filepath)
    else:
        os.remove(filepath)

def find_logs(directory, pattern='vv8*.log'):
    matches = []
    for root, dirnames, filenames in os.walk(directory):
        for filename in fnmatch.filter(filenames, pattern):
            # Service Workers are wonky in this dataset, ignore them for now
            if 'ServiceWorker' not in filename:
                matches.append(os.path.join(root, filename))
    return matches

# TODO: add frida parsing logic
@celery_app.task(name='log_parser_worker.parse_log', bind=True)
def parse_log(self, submission_id: str, packagename: str, config: ParserConfig):
    time.sleep(10)
    start = time.perf_counter()
    print(f'log_parser parse_log_task: submission_id: {submission_id}')
    self.update_state(state='PROGRESS', meta={'status': 'Postprocessor started'})
    postprocessor_path = os.path.join('/app/post-processors', 'vv8-post-processor')
    frida_postprocessor_path = os.path.join('/app/post-processors', 'frida-post-processor')
    if not os.path.isfile(postprocessor_path):
        raise Exception(f'Postprocessor script cannot be found or does not exist. Expected path: {postprocessor_path}')
    logsdir = os.path.join('/app/raw_logs/', packagename)
    outputdir = os.path.join('/app/parsed_logs', submission_id)
    if not os.path.isdir(logsdir):
        raise Exception(f'No logs found in workdir: {logsdir}')
        return
    parsers = ''
    if 'frida' in config['parser']:
        parsers = config['parser'].replace('+frida', '').replace('frida', '')
    else:
        parsers = config['parser']
    arguments = [postprocessor_path, '-aggs', parsers, '-submissionid', submission_id, '-packagename', packagename]
    #print(arguments)
    print(os.path.join(logsdir, '**/vv8*.log'))
    filelist = find_logs(logsdir)
    print(f"Found {filelist}")
    if len(filelist) == 0:
        raise Exception(f'No logs found in workdir: {logsdir}')
        return
    if config['output_format']:
        arguments.append( '-output' )
        arguments.append( config['output_format'] )
    self.update_state(state='PROGRESS', meta={'status': 'Running postprocessor'})
    for entry in filelist:
        arguments.append(entry)
    # Run postprocessor
    postprocessor_proc = None
    if config['output_format'] == 'stdout' or not config['output_format']:
        if os.path.exists(outputdir):
            # Remove all files from working directory
            for entry in glob.glob(os.path.join(outputdir, '*')):
                remove_entry(entry)
        else:
            os.mkdir(outputdir)
        outputfile = os.path.join(outputdir, 'parsed_log.output')
        f = open(outputfile, 'w+')
        postprocessor_proc = sp.Popen(arguments, cwd=logsdir, stdout=f)
        postprocessor_proc.wait()
        f.close()
    else:
        print(arguments)
        postprocessor_proc = sp.Popen(arguments, cwd=logsdir)
        postprocessor_proc.wait()
        if postprocessor_proc.returncode != 0:
            raise Exception('Postprocessor did not a return a success code')
    frida_postprocessor_proc = sp.Popen([frida_postprocessor_path, logsdir], cwd=logsdir)
    frida_postprocessor_proc.wait()
    if frida_postprocessor_proc.returncode != 0:
        raise Exception('Frida postprocessor did not a return a success code')
    end = time.perf_counter()
    self.update_state(state='SUCCESS', meta={'status': 'Postprocessor finished', 'time': end - start, 'end_time': time.time()})