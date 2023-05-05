import scrapy
import json
import re
from urllib.parse import urljoin, urlencode

API_KEY="2f731a239aad3a07ae3ea2e332cf2ee8"
def get_proxy_url(url):
    payload = {"api_key": API_KEY, "url": url}
    proxy_url = 'http://api.scraperapi.com/?' + urlencode(payload)
    return proxy_url

class AmazonSearchProductSpider(scrapy.Spider):
    name = "amazon_search_product"

    def start_requests(self):
        keywordList = ["ipad"]
        for keyword in keywordList:
            amazonSearchUrl = f'https://www.amazon.com/s?k={keyword}&page=1'
            yield scrapy.Request(url=get_proxy_url(amazonSearchUrl), callback=self.discover_product_urls, meta={"keyword": keyword, "page": 1})

    def discover_product_urls(self,response):
        page = response.meta["page"]
        keyword = response.meta["keyword"]

        search_products = response.css("div.s-result-item[data-component-type=s-search-result]")
        for product in search_products:
            relative_url = product.css("h2>a::attr(href)").get()
            product_url = urljoin('https://www.amazon.com/', relative_url).split("?")[0]
            yield scrapy.Request(url=get_proxy_url(product_url), callback=self.parse_product_data, meta={"keyword": keyword, "page": page})

        if page==1:
            available_pages = response.xpath('//*[contains(@class, "s-pagination-item")][not(has-class("s-pagination-separator"))]/text()').getall()

            last_page = available_pages[-1]
            for page_num in range(2, int(last_page)):
                amazonSearchUrl = f'https://www.amazon.com/s?k={keyword}&page={page_num}'
                yield scrapy.Request(url=get_proxy_url(amazonSearchUrl), callback=self.parse_search_results, meta={"keyword": keyword, "page": page_num})

    def parse_product_data(self, response):
        image_data = json.loads(re.findall(r"colorImages':.*'initial':\s*(\[.+?\])},\n", response.text)[0])
        variant_data = re.findall(r'dimensionValuesDisplayData"\s*:\s* ({.+?}),\n', response.text)
        feature_bullets = [bullet.strip() for bullet in response.css("#feature-bullets li ::text").getall()]
        price = response.css('.a-price span[aria-hidden="true"] ::text').get("")
        if not price:
            price = response.css('.a-price .a-offscreen ::text').get("")
        yield {
            "name": response.css("#productTitle::text").get("").strip(),
            "price": price,
            "stars": response.css("i[data-hook=average-star-rating] ::text").get("").strip(),
            "rating_count": response.css("div[data-hook=total-review-count] ::text").get("").strip(),
            "feature_bullets": feature_bullets,
            "images": image_data,
            "variant_data": variant_data,
        }

