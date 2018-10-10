from datetime import datetime, timedelta
from pymongo import MongoClient, errors

class MongoQueue():
    OUTSTANDING = 1
    PROCESSING = 2
    COMPLETE = 3

    def __init__(self, db, collection, timeout=300):
        self.client = MongoClient()
        self.Client = self.client[db]
        self.db = self.Client[collection]
        self.timeout = timeout

    def __bool__(self):
        record = self.db.find_one(
                {"status": {"$ne": self.complete}}
        )
        return True if record else False

    def push(self, url):
        try:
            self.db.insert({"_id": url, "status": self.OUTSTANDING})
            print(url, " 插入队列成功")
        except Exception as e:
            #print(url, " 已经在队列中")
            pass

    def pop(self):
        record = self.db.find_and_modify(
                query = {"status": self.OUTSTANDING},
                update = {"$set": {"status": self.PROCESSING, "timestamp": datetime.now()}}
                )
        if record:
            return record["_id"]
        else:
            self.repair()
            raise KeyError
    def peek(self):
        record = self.db.find_one({"status": self.OUTSTANDING})
        if record:
            return record["_id"]

    def complete(self, url, title, abstract, props, values, tongyi, tag, duoyi):
        self.db.update({'_id': url}, {'$set': {'status': self.COMPLETE, "abstract": abstract, "props": props, "values": values, "title": title, "tongyi": tongyi, "tag": tag, "duoyi": duoyi}})

    def repair(self):
        record = self.db.find_and_modify(
                query = {
                    "timestamp": {"$lt": datetime.now() - timedelta(seconds=self.timeout)},
                    "status" : {"$ne": self.COMPLETE}
                },
                update = {"$set": {"status": self.OUTSTANDING}}
                )
        if record:
            print("重置URL状态 ", record["_id"])

    def clear(self):
        self.db.drop()

