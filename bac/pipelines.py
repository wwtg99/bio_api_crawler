from bac.core import BasePipeline


class JsonLinePipeline(BasePipeline):

    def process_item(self, item, crawler, engine):
        super().process_item(item, crawler, engine)
        output = engine.get_option('output')
        if output is None:
            output = engine.get_config('STORAGE_OUTPUT')
        with open(output, 'a') as fp:
            fp.write(str(item) + '\n')

    def add_arguments(self, argparser):
        super().add_arguments(argparser)
        argparser.add_argument('--output', help="Json line output file name")


class MongodbPipeline(BasePipeline):

    def add_arguments(self, argparser):
        super().add_arguments(argparser)
        argparser.add_argument('--mongo-host', help="MongoDB host")
        argparser.add_argument('--mongo-port', help="MongoDB port")
        argparser.add_argument('--mongo-db', help="MongoDB database")
        argparser.add_argument('--mongo-collection', help="MongoDB collection")

    def open_crawler(self, crawler, engine):
        super().open_crawler(crawler, engine)
        from pymongo import MongoClient
        host = engine.get_option('mongo-host')
        if not host:
            host = engine.get_config('MONGO_HOST')
        port = engine.get_option('mongo-port')
        if not port:
            port = engine.get_config('MONGO_PORT')
        self.db = engine.get_option('mongo-db')
        if not self.db:
            self.db = engine.get_config('MONGO_DB')
        self.collection = engine.get_option('mongo-collection')
        if not self.collection:
            self.collection = engine.get_config('MONGO_COLLECTION')
        self.conn = MongoClient(host, port)

    def process_item(self, item, crawler, engine):
        super().process_item(item, crawler, engine)
        self.get_collection().replace_one({'_id': item['_id']}, dict(item), True)

    def get_collection(self):
        """
        Get MongoDB collection

        :return:
        :rtype: Collection
        """
        return self.conn.get_database(self.db).get_collection(self.collection)
