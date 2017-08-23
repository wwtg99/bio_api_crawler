from bac.crawlers import AsyncApiCrawler
from bac.core import BaseItem
from bac.core import CrawlerException
from bac.utils import XML2Dict
import time


class EntrezSNPCrawler(AsyncApiCrawler):

    def __init__(self, category):
        super().__init__(category)
        self.url = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi'

    def parse(self, response, engine):
        super().parse(response, engine)
        xml = XML2Dict()
        r = xml.fromstring(response)
        a = xml.format_xml_dict(r)
        if 'ExchangeSet' in a:
            a = a['ExchangeSet']
            a['_id'] = 'rs' + a['Rs']['@rsId']
            a['updated_at'] = time.strftime('%Y-%m-%d %H:%M:%S')
            return BaseItem(a)
        return None

    def parse_request(self, engine):
        super().parse_request(engine)
        params = {'db': 'snp', 'report': 'XML'}
        if engine.get_option('dbsnp_ids'):
            snps = engine.get_option('dbsnp_ids').split(',')
            for snp in snps:
                p = params.copy()
                p['id'] = snp
                yield {'params': p, 'headers': self.headers}
        elif engine.get_option('dbsnp_file'):
            for snp in self.load_snp_file(engine.get_option('dbsnp_file')):
                p = params.copy()
                p['id'] = snp
                yield {'params': p, 'headers': self.headers}
        else:
            raise CrawlerException('Neither dbsnp-ids nor dbsnp-file provided')

    def add_arguments(self, argparser):
        super().add_arguments(argparser)
        argparser.add_argument('--dbsnp-ids', help="dbSNP id list, comma delimiter [" + self.category + ']')
        argparser.add_argument('--dbsnp-file', help="File for dbSNP id list [" + self.category + ']')

    def load_snp_file(self, fpath):
        """
        Load snp ids from file.
        :param fpath:
        :return:
        """
        with open(fpath) as fp:
            for l in fp:
                l = l.strip()
                if l:
                    if l.startswith('rs'):
                        l = l[2:]
                    yield l
        return
