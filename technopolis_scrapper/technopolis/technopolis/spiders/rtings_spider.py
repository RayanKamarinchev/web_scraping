import logging

import scrapy
from urllib.parse import urlencode
from scrapy_selenium import SeleniumRequest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

API_KEY="2f731a239aad3a07ae3ea2e332cf2ee8"
def get_proxy_url(url):
    payload = {"api_key": API_KEY, "url": url}
    proxy_url = 'http://api.scraperapi.com/?' + urlencode(payload)
    return proxy_url

class RtingsBestKeyboardProductSpider(scrapy.Spider):
    name = "rtings_keyboard_product"

    def start_requests(self):
        SearchUrl = f'https://www.rtings.com/keyboard/tools/table/63539'
        yield SeleniumRequest(url=SearchUrl, callback=self.discover_product_urls,
                              wait_time=15,
                              wait_until=EC.text_to_be_present_in_element((By.CSS_SELECTOR, ".table_tool-title"), "keyboards"),
                              script='''
                                e = document.querySelectorAll(".simple_table-body.e-scrollable_content")[0]
                                function  wait(ms) {
                                        return new Promise(resolve => setTimeout(resolve, ms));
                                 }
                                while (e.scrollHeight > e.scrollTop+e.clientHeight) {
                                    e.scrollBy(0,10000);
                                    await wait(10)
                                }
                              '''
                              )

    def discover_product_urls(self,response):
        keyboard_products = response.css("tbody tr")
        for product in keyboard_products:
            yield {
                "rating": float(product.css("td:nth-child(7) div div span::text").get()),
                "title": product.css("td:nth-child(1) div a div div::text").get()
            }
