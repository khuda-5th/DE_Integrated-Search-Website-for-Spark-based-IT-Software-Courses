import json
from datetime import datetime
import os

class InflearnNewcoursePipeline:
    TODAY = datetime.today().strftime('%y%m%d')
    def __init__(self):
        if not os.path.exists("~/data/inflearn/new/raw"):
            os.makedirs("~/data/inflearn/new/raw")
        self.file = open(f"~/data/inflearn/new/raw/{self.TODAY}_inflearn_new.json", 'w', encoding='utf-8')
    
    def process_item(self, item, spider):
        line = json.dumps(dict(item), ensure_ascii=False) + "\n" #Item을 한줄씩 구성        
        self.file.write(line) #파일에 기록
        return item

    def spider_closed(self, spider):
        self.file.close() #파일 CLOSE