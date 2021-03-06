import logging
import json
import bac.utils
import time


class Engine:
    """
    Crawler engine.
    """
    def __init__(self, config):
        self._config = config
        self._options = {}
        self._crawlers = {}
        self._crawler = None
        self._pipelines = []
        self._version = 'v0.1'
        self._descr = 'Bioinfomatics API crawler'
        self._start = time.time()

    def init_crawler(self, argparser):
        """
        Initialize engine.
        :param argparser:
        :return:
        """
        # add arguments
        argparser.add_argument('action', help="Crawler action", choices=['help', 'version', 'list', 'crawl'])
        argparser.add_argument('-V', '--verbose', help="Print more information", action="store_true")
        argparser.add_argument('-c', '--crawler', help="Crawler name")
        argparser.add_argument('--logger', help="Change log output")
        argparser.add_argument('--logfile', help="Change log file path")
        argparser.add_argument('--loglevel', help="Change log level")
        argparser.add_argument('--speed-limit', help="Whether sleep after process some data, default false", action="store_true")
        argparser.add_argument('--limit-num', help="Sleep after how many requests", type=int)
        argparser.add_argument('--sleep-sec', help="Sleep seconds", type=int)
        # init crawlers
        crawlers = self._config.CRAWLERS
        for category, p in crawlers.items():
            pkg, cls = bac.utils.split_class(p)
            pr = __import__(pkg, fromlist=True)
            par = getattr(pr, cls)(category)
            self._crawlers[category] = par
            par.add_arguments(argparser)
        # init pipelines
        pipelines = self._config.PIPELINES
        for p in pipelines:
            pkg, cls = bac.utils.split_class(p)
            pr = __import__(pkg, fromlist=True)
            par = getattr(pr, cls)()
            par.add_arguments(argparser)
            self._pipelines.append(par)

    def parse_arguments(self, args):
        """
        Parse command line options.
        :param args:
        :return:
        """
        self._options = args
        action = args.action.lower()
        if action == 'help':
            print(self.show_help())
        elif action == 'version':
            print(self._version + ' ' + self._descr)
        elif action == 'list':
            for c in self.list_crawlers():
                print(c)
        elif action == 'crawl':
            crw = args.crawler
            if crw is None:
                print('No crawler provided by --crawler')
            else:
                self.start(crw)

    def show_help(self):
        h = 'List available actions. See more info please use --help\n' \
            'version\tShow version\n' \
            'list\tList available crawlers\n' \
            'crawl\tStart crawl by a defined crawler\n'
        return h

    def init_logger(self):
        """
        Initialize logger.
        :return:
        """
        level = {
            'debug': logging.DEBUG,
            'info': logging.INFO,
            'warning': logging.WARNING,
            'ERROR': logging.ERROR
        }
        logtype = self.get_option('logger')
        if logtype:
            self._config.LOG_TYPE = logtype
        loglevel = self.get_option('loglevel')
        if loglevel:
            self._config.LOG_LEVEL = loglevel
        logfile = self.get_option('logfile')
        if logfile:
            self._config.LOG_FILE = logfile
            self._config.LOG_TYPE = 'file'
        if self._config.LOG_LEVEL.lower() in level:
            lv = level[self._config.LOG_LEVEL.lower()]
        else:
            lv = logging.INFO
        logformat = '%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s'
        datefmt = '%a, %d %b %Y %H:%M:%S'
        if self._config.LOG_TYPE == 'file':
            logging.basicConfig(level=lv, format=logformat, datefmt=datefmt, filename=self._config.LOG_FILE, filemode='a')
        else:
            logging.basicConfig(level=lv, format=logformat, datefmt=datefmt)

    def start(self, category):
        self.open_crawler(category)
        self.crawl(category)
        self.close_crawler()
        runtime = time.time() - self._start
        logging.info('Finish! Run time %s ' % str(runtime))

    def open_crawler(self, category=None):
        """
        Start crawler.
        :param category:
        :return:
        """
        self.init_logger()
        if category is None:
            category = self.get_option('crawler')
        crawler = self.get_crawler(category)
        if crawler is None:
            raise CrawlerException('Invalid crawler %s' % (category,))
        logging.info("Open crawler %s" % (category, ))
        self._crawler = crawler
        self._crawler.open(self)
        for p in self._pipelines:
            p.open_crawler(self._crawler, self)

    def crawl(self, category=None):
        """
        Crawl data.
        :param category:
        :return:
        """
        if category is None:
            category = self.get_option('crawler')
        crawler = self.get_crawler(category)
        crawler.process(self)

    def go_through_pipelines(self, item, crawler):
        """
        Go through pipelines for each item.
        :param BaseItem item:
        :param BaseCrawler crawler:
        :return:
        """
        for p in self._pipelines:
            item = p.process_item(item, crawler, self)
            if item is None:
                break
        return item

    def close_crawler(self):
        """
        Close crawler.
        :return:
        """
        logging.info('Close crawler')
        for p in self._pipelines:
            p.close_crawler(self._crawler, self)
        self._crawler.close(self)

    def get_config(self, key):
        """
        Get config by key.
        :param key:
        :return: config
        """
        if hasattr(self._config, key):
            return getattr(self._config, key)
        return None

    def get_option(self, key):
        """
        Get command option by key.
        :param key:
        :return: option
        :rtype: str
        """
        if hasattr(self._options, key):
            return getattr(self._options, key)
        return None

    def get_crawler(self, category):
        """
        Get crawler by category.
        :param category:
        :return: crawler
        :rtype: BaseCrawler
        """
        if category in self._crawlers:
            return self._crawlers[category]
        else:
            return None

    def list_crawlers(self):
        """
        Get available crawlers.
        :return: list
        """
        return self._crawlers.keys()


class BaseItem:
    """
    Base item object.
    """

    def __init__(self, *args, **kwargs):
        self._values = {}
        if args or kwargs:  # avoid creating dict for most common case
            for k, v in dict(*args, **kwargs).items():
                self._values[k] = v

    def __getitem__(self, item):
        return self._values[item]

    def __setitem__(self, key, value):
        self._values[key] = value

    def __delitem__(self, key):
        del self._values[key]

    def __len__(self):
        return len(self._values)

    def __iter__(self):
        return iter(self._values)

    def __str__(self):
        return json.dumps(self._values)

    def keys(self):
        return self._values.keys()

    def copy(self):
        return self.__class__(self)


class BasePipeline:
    """
    Super class for pipeline.
    """
    def __init__(self):
        pass

    def open_crawler(self, crawler, engine):
        """
        Call this function after crawler opened.

        :param crawler:
        :param engine:
        :return:
        """
        pass

    def close_crawler(self, crawler, engine):
        """
        Call this function before crawler closing.

        :param crawler:
        :param engine:
        :return:
        """
        pass

    def add_arguments(self, argparser):
        """

        Add command arguments.

        :param argparse.ArgumentParser argparser:
        :return:
        """
        pass

    def process_item(self, item, crawler, engine):
        """
        Process each item, return BastItem or None to stop.

        :param item:
        :param crawler:
        :param engine:
        :return: BaseItem or None
        """
        pass


class BaseCrawler:
    """
    Super class for crawler..
    """

    def __init__(self, category):
        self.category = category
        self.url = ''
        self.method = 'get'
        self.headers = {"Content-Type": "application/json", "Accept": "application/json"}

    def add_arguments(self, argparser):
        """

        Add command arguments.

        :param argparse.ArgumentParser argparser:
        :return:
        """
        pass

    def open(self, engine):
        """
        Called when crawler is opened.
        :param Engine engine:
        :return:
        """
        pass

    def process(self, engine):
        """
        Called when process data.
        :param Engine engine:
        :return:
        """
        pass

    def parse_request(self, engine):
        """
        Parse request params.
        :param Engine engine:
        :return: generator for request params, data or headers
        """
        pass

    def parse(self, response, engine):
        """

        Parse data to crawler.

        :param response:
        :param engine
        :return: BaseItem, list of BaseItem or None
        """
        return None

    def close(self, engine):
        """
        Called when crawler is closing.
        :param Engine engine:
        :return:
        """
        pass


class CrawlerException(Exception):

    def __init__(self, message):
        self._msg = message

    def __str__(self):
        return self._msg
