import logging

import scrapy
from urllib.parse import urlencode
import math

API_KEY="2f731a239aad3a07ae3ea2e332cf2ee8"
def get_proxy_url(url):
    payload = {"api_key": API_KEY, "url": url}
    proxy_url = 'http://api.scraperapi.com/?' + urlencode(payload)
    return proxy_url

class TechnopolisKeyboardProductSpider(scrapy.Spider):
    name = "technopolis_keyboard_product"

    def start_requests(self):
        SearchUrl = f'https://www.technopolis.bg/bg//Kompyut%C3%A0rni-aksesoari/Mishki-i-klaviaturi/Klaviaturi/c/P11020202?pageselect=90&page=0'
        yield scrapy.Request(url=get_proxy_url(SearchUrl), callback=self.discover_product_urls, meta={"page": 0})

    def discover_product_urls(self,response):
        page = response.meta["page"]
        keyboard_products = response.css(".products-grid-list .list-item .product-box")
        for product in keyboard_products:
            yield {
                "price": int(product.css(".product-box__bottom .product-box__bottom-top .product-box__prices .product-box__price .product-box__price-value::text").get())+1,
                "title": product.css(".product-box__middle h3 .product-box__title-link::text").get().replace("Клавиатура ", "")
            }

        if page==0:
            last_page = math.ceil(int(response.css(".content-title small .highlight *::text").get())/90)
            for page_num in range(1, int(last_page)):
                SearchUrl = f'https://www.technopolis.bg/bg//Kompyut%C3%A0rni-aksesoari/Mishki-i-klaviaturi/Klaviaturi/c/P11020202?pageselect=90&page={page_num}'
                yield scrapy.Request(url=get_proxy_url(SearchUrl), callback=self.discover_product_urls, meta={"page": page_num})
