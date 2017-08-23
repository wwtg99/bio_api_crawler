from bac.core import BaseCrawler
import asyncio
import aiohttp
import async_timeout
import logging
from bac.core import CrawlerException


class AsyncApiCrawler(BaseCrawler):

    def __init__(self, category):
        super().__init__(category)
        self._speed_limit = False
        self._limit_num = 10
        self._sleep_second = 3
        self._batch = 0

    def open(self, engine):
        super().open(engine)
        self._speed_limit = engine.get_config('SPEED_LIMIT')
        if engine.get_option('speed_limit'):
            self._speed_limit = engine.get_option('speed_limit')
        self._limit_num = engine.get_option('speed_limit')
        if engine.get_option('limit_num'):
            self._limit_num = engine.get_option('limit_num')
        self._sleep_second = engine.get_config('SLEEP_SECOND')
        if engine.get_option('sleep-sec'):
            self._sleep_second = engine.get_option('sleep_sec')

    def process(self, engine):
        super().process(engine)
        loop = asyncio.get_event_loop()
        tasks = []
        for d in self.parse_request(engine):
            if engine.get_option('verbose'):
                logging.info('Start %s for %s with %s' % (self.method, self.url, str(d)))
            tasks.append(self.request_task(engine, self.method, **d))
        loop.run_until_complete(asyncio.wait(tasks))
        loop.close()

    async def request_task(self, engine, method, **kwargs):
        async with aiohttp.ClientSession() as session:
            res = await self.async_request(session, method, self.url, **kwargs)
            item = self.parse(res, engine)
            if item is not None:
                if isinstance(item, list):
                    for t in item:
                        self.pipeline_item(t, engine)
                else:
                    self.pipeline_item(item, engine)

    async def async_request(self, session, method, url, **kwargs):
        """
        Async request
        :param session:
        :param method:
        :param url:
        :param kwargs:
        :return: response text
        """
        if self._speed_limit:
            if self._batch >= self._limit_num:
                await asyncio.sleep(self._sleep_second)
                self._batch = 0
        self._batch += 1
        with async_timeout.timeout(10):
            if method.lower() == 'get':
                async with session.get(url, **kwargs) as response:
                    if response.status >= 400:
                        txt = await response.text()
                        logging.error(txt)
                        return []
                    return await response.text()
            elif method.lower() == 'post':
                async with session.post(url, **kwargs) as response:
                    if response.status >= 400:
                        txt = await response.text()
                        logging.error(txt)
                        return []
                    return await response.text()
            elif method.lower() == 'put':
                async with session.put(url, **kwargs) as response:
                    if response.status >= 400:
                        txt = await response.text()
                        logging.error(txt)
                        return []
                    return await response.text()
            elif method.lower() == 'patch':
                async with session.patch(url, **kwargs) as response:
                    if response.status >= 400:
                        txt = await response.text()
                        logging.error(txt)
                        return []
                    return await response.text()
            elif method.lower() == 'delete':
                async with session.delete(url, **kwargs) as response:
                    if response.status >= 400:
                        txt = await response.text()
                        logging.error(txt)
                        return []
                    return await response.text()
            else:
                raise CrawlerException('Invalid request method %s' % (method, ))

    def pipeline_item(self, item, engine):
        if engine.get_option('verbose'):
            logging.info('Parse item ' + str(item))
        engine.go_through_pipelines(item, self)
