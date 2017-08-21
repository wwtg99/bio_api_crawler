#! /bin/python
import config
import argparse
from bac.core import Engine
import logging


VERSION = '0.1'


def show_version():
    print(VERSION)


def main():
    argparser = argparse.ArgumentParser()
    argparser.add_argument('crawler', help="Crawler name")
    argparser.add_argument('-v', '--version', help="Show Version", action="store_true")
    argparser.add_argument('-V', '--verbose', help="Print more information", action="store_true")
    argparser.add_argument('--logger', help="Change log output")
    argparser.add_argument('--logfile', help="Change log file path")
    argparser.add_argument('--loglevel', help="Change log level")
    try:
        eng = Engine(config)
        eng.init_crawler(argparser)
        args = argparser.parse_args()
        if args.version:
            show_version()
            return
        eng.parse_options(args)
        category = args.crawler
        eng.start(category)
    except Exception as e:
        logging.error(str(e))


if __name__ == '__main__':
    main()

