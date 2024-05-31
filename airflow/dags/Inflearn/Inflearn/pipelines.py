# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
# from itemadapter import ItemAdapter
import json
from datetime import datetime
import os


class InflearnPipeline:
    TODAY = datetime.today().strftime('%y%m%d')
    def __init__(self):
        if not os.path.exists("~/data/inflearn/entire/raw"):
            os.makedirs("~/data/inflearn/entire/raw")
        self.file = open(f"~/data/inflearn/entire/raw/{self.TODAY}_inflearn_entire.json", 'w', encoding='utf-8')
        
    def process_item(self, item, spider):
        line = json.dumps(dict(item), ensure_ascii=False) + "\n" #Item을 한줄씩 구성        
        self.file.write(line) #파일에 기록
        return item

    def spider_closed(self, spider):
        self.file.close() #파일 CLOSE
