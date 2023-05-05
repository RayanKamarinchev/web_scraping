from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem

class PriceToUSDPipeline:
    poundToUsd = 1.3
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        if adapter.get("price"):
            floatPrice = float(adapter["price"])
            adapter["price"] = floatPrice*self.poundToUsd
            return item
        else:
            raise DropItem(f"Missing price in {item}")

class DuplicatesPipeline:

    def __init__(self):
        self.names_seen = set()

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        if adapter['name'] in self.names_seen:
            raise DropItem(f"Duplicate item found: {item!r}")
        else:
            self.names_seen.add(adapter['name'])
            return item