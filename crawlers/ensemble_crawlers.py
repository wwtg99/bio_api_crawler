from bac.crawlers import AsyncApiCrawler
from bac.core import BaseItem
import json
import time


class EnsembleVariationCrawler(AsyncApiCrawler):

    def __init__(self, category):
        super().__init__(category)
        self.url = 'http://grch37.rest.ensembl.org/variation/homo_sapiens'
        self.method = 'post'
        self.max_batch_num = 200

    def add_arguments(self, argparser):
        super().add_arguments(argparser)
        argparser.add_argument('--snp-ids', help="SNP id list, comma delimiter [" + self.category + ']')
        argparser.add_argument('--snp-file', help="File for SNP id list [" + self.category + ']')
        argparser.add_argument('--genotypes', help="Include individual genotypes [" + self.category + ']',
                               action='store_true')
        argparser.add_argument('--phenotypes', help="Include phenotypes [" + self.category + ']', action='store_true')
        argparser.add_argument('--pops', help="Include population allele frequencies [" + self.category + ']',
                               action='store_true')
        argparser.add_argument('--population-genotypes', help="Include population genotype frequencies [" + self.category + ']',
                               action='store_true')

    def parse_request(self, engine):
        params = {}
        if engine.get_option('genotypes'):
            params['genotypes'] = 1
        if engine.get_option('phenotypes'):
            params['phenotypes'] = 1
        if engine.get_option('pops'):
            params['pops'] = 1
        if engine.get_option('population-genotypes'):
            params['population-genotypes'] = 1
        if engine.get_option('snp_ids'):
            snps = engine.get_option('snp_ids').split(',')
            yield {'data': json.dumps({'ids': snps}), 'params': params, 'headers': self.headers}
        elif engine.get_option('snp_file'):
            for snps in self.load_snp_file(engine.get_option('snp_file')):
                yield {'data': json.dumps({'ids': snps}), 'params': params, 'headers': self.headers}

    def parse(self, response, engine):
        super().parse(response, engine)
        obj = json.loads(response)
        arr = []
        for rs in obj:
            d = obj[rs]
            d['_id'] = rs
            d['updated_at'] = time.strftime('%Y-%m-%d %H:%M:%S')
            arr.append(BaseItem(d))
        return arr

    def load_snp_file(self, fpath):
        """
        Load snp ids from file.
        :param fpath:
        :return:
        """
        snp = []
        num = 0
        with open(fpath) as fp:
            for l in fp:
                l = l.strip()
                if l:
                    snp.append(l)
                    num += 1
                if num >= self.max_batch_num:
                    yield snp
                    snp = []
                    num = 0
            if len(snp) > 0:
                yield snp
                snp = []
        return snp
