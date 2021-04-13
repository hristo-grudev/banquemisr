import scrapy
from scrapy import FormRequest

from scrapy.loader import ItemLoader

from ..items import BanquemisrItem
from itemloaders.processors import TakeFirst


class BanquemisrSpider(scrapy.Spider):
	name = 'banquemisr'
	start_urls = ['https://www.banquemisr.com/en/about-us/press?csrt=15173960905214059161']

	def parse(self, response):
		post_links = response.xpath('//a[@class="ms-linksectionheader"]/@href').getall()
		yield from response.follow_all(post_links, self.parse_post)

		next_page = response.xpath('//a[@class="branchBtn"]/@href').getall()
		if next_page:
			argument = next_page[0][:-1]
			yield FormRequest.from_response(response, formdata={
				'__EVENTTARGET': 'ctl00$m$g_631319fd_1b20_4fe5_b840_ac9b5527871a',
				"__EVENTARGUMENT": 'dvt_firstrow={11}',
				"__REQUESTDIGEST": 'dvt_startposition={Paged=TRUE&p_SortBehavior=0&p_Created_x0020_Date=2%2f15%2f2021%2010%3a56%3a43%20AM&p_ID=375}'}, callback=self.parse)

	def parse_post(self, response):
		title = response.xpath('//div[@class="inrTitle"]/text()').get()
		description = response.xpath('//div[@class="newsLstngContent"]//text()[normalize-space() and not(ancestor::div[@style="display:none"])]').getall()
		description = [p.strip() for p in description if '{' not in p]
		description = ' '.join(description).strip()
		date = response.xpath('//div[@class="newsDate"]//text()[normalize-space()]').get()

		item = ItemLoader(item=BanquemisrItem(), response=response)
		item.default_output_processor = TakeFirst()
		item.add_value('title', title)
		item.add_value('description', description)
		item.add_value('date', date)

		return item.load_item()
