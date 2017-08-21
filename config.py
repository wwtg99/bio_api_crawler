# log type
# available: console, file
LOG_TYPE = 'console'
LOG_FILE = 'parser_error.log'  # log file path if LOG_TYPE is file
LOG_LEVEL = 'DEBUG'

# crawlers
CRAWLERS = {
    'variation': 'crawlers.ensemble_crawlers.EnsembleVariationCrawler'
}

# pipelines
# execute by order
PIPELINES = [
    # 'bac.pipelines.JsonLinePipeline'  # store items in json line file
    'bac.pipelines.MongodbPipeline'  # store items in mongodb
]

# pipelines config
# json line pipeline
STORAGE_OUTPUT = 'data/out.json'  # default output file for json line
# mongo storage
MONGO_HOST = '192.168.0.21'  # default mongodb host
MONGO_PORT = 27017  # default mongodb port
MONGO_DB = 'gparser'  # default mongodb db
MONGO_COLLECTION = 'gene'  # default mongodb collection
