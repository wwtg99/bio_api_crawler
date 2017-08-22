#! /bin/python
import config
import argparse
from bac.core import Engine
import logging


def main():
    argparser = argparse.ArgumentParser()
    try:
        eng = Engine(config)
        eng.init_crawler(argparser)
        args = argparser.parse_args()
        eng.parse_arguments(args)
    except Exception as e:
        logging.error(str(e))


if __name__ == '__main__':
    main()

