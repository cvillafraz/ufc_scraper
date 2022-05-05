from scrapy import Spider
from scrapy.selector import Selector


class UFCSpider(Spider):
    name = "ufc_spider"
    start_urls = ["http://ufcstats.com/statistics/events/completed?page=all"]
    custom_settings = {
        "FEEDS": {
            "items.json": {
                "format": "json",
                "encoding": "utf8",
            },
        },
        "CONCURRENT_REQUESTS": 24,
        "MEMUSAGE_LIMIT_MB": 2048,
        "MEMUSAGE_NOTIFY_MAIL": ["contact@cirov.com"],
    }

    def parse(self, res):
        """Get the links to the event pages, and follow them

        Args:
            res: response object from the request made to the start_urls

        Yields:
            res.follow(): follow the link to the event pages
        """

        event_links = res.xpath(
            '//i[@class="b-statistics__table-content"]/a/@href'
        ).getall()

        for link in event_links:
            yield res.follow(
                link,
                callback=self.parse_event,
            )

    def parse_event(self, res):
        """Parse data from the event page, such as event name, date and location

        Args:
            res: response object from the request made to the event page

        Yields:
            dictionary containing the event data
        """

        event_name = res.xpath("//h2//text()").getall()[1].strip()
        event_info = res.xpath("//li[@class='b-list__box-list-item']/text()").getall()
        event_date = event_info[1].strip()
        event_location = event_info[3].strip()
        fights_xpath = res.xpath("//tr").getall()[1:]
        fights = []

        for idx, fight in enumerate(fights_xpath):

            fights.append(self._parse_fight(idx, fight))

        yield {
            "event_name": event_name,
            "event_date": event_date,
            "event_location": event_location,
            "fights": fights,
        }

    def _parse_fight(self, idx, fight):
        """Parse data of a single fight

        Args:
            idx (int): index of the fight in the list of fights from the event page
            fight (str): html string containing the fight data

        Returns:
            dictionary containing the fight data
        """

        details = [
            s.strip()
            for s in Selector(text=fight).xpath("//p//text()").getall()
            if len(s.strip()) > 0
        ]

        if "draw" in details or "nc" in details:
            details.pop(0)

        # Check if fight has detailed method of finish
        method_detail = None
        if details[12] in ("KO/TKO", "SUB") and not details[13].isnumeric():
            method_detail = details[13]

        fight_details = {
            "fighter_1": details[1],
            "fighter_2": details[2],
            "fighter_1_kd": details[3],
            "fighter_2_kd": details[4],
            "fighter_1_str": details[5],
            "fighter_2_str": details[6],
            "fighter_1_td": details[7],
            "fighter_2_td": details[8],
            "fighter_1_sub": details[9],
            "fighter_2_sub": details[10],
            "weigh_class": details[11],
            "method": details[12],
            "method_detail": method_detail,
            "round": details[-2],
            "time": details[-1],
            "closure": details[0],
            "is_main_event": True if idx == 0 else False,
        }

        return fight_details
