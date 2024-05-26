import json
import codecs


class InflearnNewcoursePipeline:
    def __init__(self):
        self.file = codecs.open('new_course_test01.json', 'w', encoding='utf-8') #크롤링 데이터를 저장할 파일 OPEN             
        
    def process_item(self, item, spider):
        line = json.dumps(dict(item), ensure_ascii=False) + "\n" #Item을 한줄씩 구성        
        self.file.write(line) #파일에 기록
        return item

    def spider_closed(self, spider):
        self.file.close() #파일 CLOSE
