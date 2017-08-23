API Crawler for Bioinformatic
=========================

# Description
Async api crawler depends on asyncio of python3.
Crawl data from NCBI Entrez, Ensemble APIs and etc.
It also can be used for other APIs.

# Requirements
- Python 3.5+
- aiohttp
- pymongo if you use MongoDB

# Installation
```
git clone git@github.com:wwtg99/bio_api_crawler.git
```

# Manual
```
python crawler.py -h
```

# Configuration
All config store in the config.py. Some configuration can be changed in command line.

### CRAWLERS: define crawlers
User can add custom crawler by extending AsyncApiCrawler(most time) or BaseCrawler.
Key is the name for crawler and can be called by `--crawler`, value is the class name for crawler.

Each crawler must implement two functions:
- parse_request(self, engine): return params for each request
- parse(self, response, engine): parse response for each request, return BaseItem, list of BaseItem or None

And three optional functions:
- add_arguments(self, argparser): add arguments in the console.
- open(self, engine): called after crawler is initialized, can handle arguments here.
- close(self, engine): called before crawler is closed.

### PIPELINES: define item pipelines
Each item go through each pipeline by order.

Each pipeline must implement one function:
- process_item(self, item, crawler, engine): process each item, should return BaseItem or None

And three optional functions:
- add_arguments(self, argparser): add arguments in the console.
- open_crawler(self, crawler, engine): called after crawler is initialized, can handle arguments here.
- close_crawler(self, crawler, engine): called before crawler is closed.

#### Available pipelines
- ConsolePipeline: print item to console
- JsonLinePipeline: output item to json line file
- MongodbPipeline: store item to mongodb

# Usage
List all available crawlers.
```
python crawler.py list
```

Crawl SNP rs7412 from Ensemble.
```
python crawler.py crawl -c variation --snp-ids=rs7412
```

Crawl SNP rs7412 from NCBI Entrez.
```
python crawler.py crawl -c dbsnp --dbsnp-ids=rs7412
```
