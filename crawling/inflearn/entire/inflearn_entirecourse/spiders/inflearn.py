import scrapy
from Inflearn.items import InflearnItem

class InflearnSpider(scrapy.Spider):
    name = "inflearn"
    # allowed_domains = ["www.inflearn.com"]
    # start_urls = ["http://www.inflearn.com/"]

    # __init__ 함수처럼 기본으로 실행됨. 
    # start_requests 함수 작성시 start_urls 변수는 주석처리 또는 삭제
    def start_requests(self):
        urls = ["https://www.inflearn.com/courses/it-programming?order=seq", # 개발/프로그래밍
                "https://www.inflearn.com/courses/game-dev-all?order=seq", # 게임 개발
                "https://www.inflearn.com/courses/data-science?order=seq", # 데이터 사이언스
                "https://www.inflearn.com/courses/artificial-intelligence?order=seq", # 인공지능
                "https://www.inflearn.com/courses/it?order=seq", # 보안/네트워크
                "https://www.inflearn.com/courses/business?order=seq", # 비즈니스/마케팅
                "https://www.inflearn.com/courses/hardware?order=seq", # 하드웨어
                "https://www.inflearn.com/courses/design?order=seq", # 디자인
                "https://www.inflearn.com/courses/academics?order=seq", # 학문/외국어
                "https://www.inflearn.com/courses/career?order=seq", # 커리어
                "https://www.inflearn.com/courses/life?order=seq"] # 자기계발
        # category_id_list = ['accordion_5', 'accordion_39306', 'accordion_9', 'accordion_456', 'accordion_492',
        #                'accordion_33', 'accordion_178677', 'accordion_22', 'accordion_493', 'accordion_494', 'accordion_666']
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse_sub, meta = {'url': url})

    def parse_sub(self, response):
        url = response.meta['url']
        last_page = int(response.xpath('//*[@id="courses_section"]/div/div/div/footer/nav/div//text()').getall()[-3])
        for page in range(1, last_page + 1):
            yield scrapy.Request(url=url + "&page=" + str(page), callback=self.parse_main)
        
    
    def parse_main(self, response):
        # category_id = response.meta['category_id']
        # ca_name = response.xpath('//*[@id="courses_section"]/div/div/aside/nav').css("div#" + category_id + " span.accordion-header-text__title::text").get()
        # sub_ca_name = response.xpath('//*[@id="' + category_id + '"]/div[2]/a/text()').getall()
        # sub_ca_name.pop(0)
        # sub_ca_link = response.xpath('//*[@id="' + category_id + '"]/div[2]/a/@href').getall()
        
        # for sub_link in sub_ca_link:
        #     yield scrapy.Request(url='https://www.inflearn.com' + sub_link, callback=self.parse_sub_link) \
        urls = response.xpath('//*[@id="courses_section"]/div/div/div/main/div[4]/div/div/div/a/@href').getall()
        for c_url in urls:
            yield scrapy.Request(url="https://www.inflearn.com" + c_url, callback=self.parse_items, meta={'course_link': "https://www.inflearn.com" + c_url})
        # response = scrapy.Request(url=response.meta['url'] + "&page=" + str(page))
        # yield scrapy.Request(url=response.meta['url'] + "&page=" + str(page), callback=self.parse_main, meta={'page' : page+1, 'url': response.meta['url']})

    # def parse_sub_link(self, response): 
    #     ca_name = response.meta['category_name']
    #     sub_ca_name = response.meta['sub_category_name']
    #     urls = response.xpath('//*[@id="courses_section"]/div/div/div/main/div[4]/div/div/div/a/@href').getall()
    #     for url in urls:
    #         yield scrapy.Request(url="https://www.inflearn.com" + url, callback=self.parse_items, \
    #                                 meta={"category_name": ca_name, 'sub_category_name': sub_ca_name, 'course_link': "https://www.inflearn.com" + url})

    def parse_items(self, response):
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


        doc = InflearnItem()
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


        # example = {'test': 1}
        yield doc


