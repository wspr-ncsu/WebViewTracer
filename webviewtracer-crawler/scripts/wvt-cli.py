import argparse
import postprocess as postprocess
import setup
import docker
import crawl
import shutdown
import results

from enum import Enum

class Mode(Enum):
    postprocess = 'postprocess'
    crawl = 'crawl'
    fetch = 'fetch'
    setup = 'setup'
    docker = 'docker'
    shutdown = 'shutdown'
    results = 'results'

    def __str__(self):
        return self.value

def main():
    docker.system_check()
    parser = argparse.ArgumentParser(prog='vv8-cli',
                    description='A cli to run basic WebViewTracer jobs from the command line')
    mode = parser.add_subparsers(dest='mode', title='various actions that can be performed using the cli')
    crawl_arg_parser = mode.add_parser(Mode.postprocess.value, help='Postprocess the data from crawled apps')
    postprocess.postprocessor_parse_args(crawl_arg_parser)
    setup_arg_parser = mode.add_parser(Mode.setup.value, help='setup webviewtracer cli and crawler (in case you want to run the crawler locally)')
    setup.setup_parse_args(setup_arg_parser)
    docker_arg_parser = mode.add_parser(Mode.docker.value, help='manage local docker instance of webviewtracer server, only available for local installs')
    docker.docker_parse_args(docker_arg_parser)
    crawl_arg_parser = mode.add_parser(Mode.crawl.value, help='Crawl apps using webviewtracer')
    mode.add_parser(Mode.shutdown.value, help='Shutdown the WebViewTracer crawler gracefully')
    mode.add_parser(Mode.results.value, help='Get results from the crawled apps')

    opts, unkown_args = parser.parse_known_args()


    if opts.mode != Mode.postprocess.value and unkown_args:
        print('ignoring unknown args: ', unkown_args)
        parser.print_usage()
        return

    match opts.mode:
        case Mode.postprocess.value:
            postprocess.postprocesser(opts)
        case Mode.setup.value:
            setup.setup(opts)
        case Mode.docker.value:
            docker.docker(opts)
        case Mode.crawl.value:
            crawl.crawl()
        case Mode.shutdown.value:
            shutdown.shutdown()
        case Mode.results.value:
            results.results()

if __name__ == '__main__':
    main()