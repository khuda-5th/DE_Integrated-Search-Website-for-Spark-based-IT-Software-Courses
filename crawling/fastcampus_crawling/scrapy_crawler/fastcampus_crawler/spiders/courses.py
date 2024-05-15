import scrapy


class CoursesSpider(scrapy.Spider):
    name = "courses"
    allowed_domains = ["fastcampus.co.kr"]
    start_urls = ["https://fastcampus.co.kr/categories"]

    def parse(self, response):
        pass
