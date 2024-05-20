import scrapy
from inflearn_newcourse.items import InflearNewcoursenItem
import sys

sys.path.append('home/dbgpw/Downloads/DE5th_project/Inflearn')


class InflearnNewCourseSpider(scrapy.Spider):
    name = "inflearn_newcourse_spider"
    # allowed_domains = ["www.inflearn.com"]
    # start_urls = ["http://www.inflearn.com/"]


    def start_requests(self):
        url = 'https://www.inflearn.com/courses?order=recent'
        yield scrapy.Request(url=url, callback=self.parse_sub, meta={'url': url})

    def parse_sub(self, response):
        url = response.meta['url']
        for page in range(1, 9): 
            yield scrapy.Request(url=url + "&page=" + str(page), callback=self.parse_main) 
    
    def parse_main(self, response):
        urls = (response.xpath('//*[@id="courses_section"]/div/div/div/main/div[4]/div/div/div/a/@href').getall())
        for c_url in urls:
            yield scrapy.Request(url="https://www.inflearn.com" + c_url, callback=self.parse_items, meta={'course_link': "https://www.inflearn.com" + c_url})

    def parse_items(self, response):
        new_tag = response.xpath('//*[@id="main"]/section/div[1]/div[1]/div/div/div[2]/div[1]/div/span/text()').getall()
        if "NEW" in new_tag:

            category_name = response.xpath('//*[@id="main"]/section/div[1]/div[1]/div/div/div[2]/div[1]/span[1]/text()').get()
            sub_category_name = response.xpath('//*[@id="main"]/section/div[1]/div[1]/div/div/div[2]/div[1]/span[3]/text()').get()

            title = response.css('h1.cd-header__title::text').get()
            num_of_lecture = response.xpath('//*[@id="main"]/section/div[1]/div[2]/div[2]/div/div[2]/text()').getall()
            curri = response.xpath('//*[@id="curriculum"]/div[3]/div//text()').getall()
            instructor = response.css('a.cd-header__instructors--main::text').get()
            instructor_desc = response.xpath('//*[@id="main"]/section/div[3]/div/div/div[1]/div/section[2]/div/div[2]/div//text()').getall()
            tag = response.css('a.cd-header__tag::text').getall()
            star = response.css('span.cd-header__info--star strong::text').get()
            num_of_stud = response.xpath('//*[@id="main"]/section/div[1]/div[1]/div/div/div[2]/div[3]/span[2]/strong/text()').getall()
            num_of_review = response.css('div.cd-header__info-cover > a::text').get(default='0')
            # 수강평도 '수강평 더보기' 버튼 눌러서 더 가져와야 함.
            review = response.css('div.review-el__body::text').getall()
            img = response.xpath('//*[@id="main"]/section/div[1]/div[1]/div/div/div[1]/div/div[1]/img/@src').get()
            # 원가, 할인가, 할부금까지 전부 아래 xpath와 같음.
            price = response.xpath('//*[@id="main"]/section/div[1]/div[2]/div[1]//text()').getall()
            text = response.xpath('//*[@id="description"]//text()').getall()


            doc = InflearnNewCourseSpider()
            doc['category'] = [{}]
            doc['category'][0]['category_name'] = category_name
            doc['category'][0]['sub_category'] = {}
            doc['category'][0]['sub_category']['sub_category_name'] = sub_category_name
            doc['category'][0]['sub_category']['courses'] = [{}]
            doc['category'][0]['sub_category']['courses'][0]['title'] = title
            doc['category'][0]['sub_category']['courses'][0]['course_link'] = response.meta['course_link']
            doc['category'][0]['sub_category']['courses'][0]['num_of_lecture'] = num_of_lecture
            doc['category'][0]['sub_category']['courses'][0]['curri'] = curri
            doc['category'][0]['sub_category']['courses'][0]['instructor'] = instructor
            doc['category'][0]['sub_category']['courses'][0]['instructor_desc'] = instructor_desc
            doc['category'][0]['sub_category']['courses'][0]['tag'] = tag
            doc['category'][0]['sub_category']['courses'][0]['star'] = star
            doc['category'][0]['sub_category']['courses'][0]['num_of_stud'] = num_of_stud
            doc['category'][0]['sub_category']['courses'][0]['num_of_review'] = num_of_review
            doc['category'][0]['sub_category']['courses'][0]['review'] = review
            doc['category'][0]['sub_category']['courses'][0]['img'] = img
            doc['category'][0]['sub_category']['courses'][0]['price'] = price
            doc['category'][0]['sub_category']['courses'][0]['text'] = text


            yield doc


