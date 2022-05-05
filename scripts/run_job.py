import logging
from scrapinghub import ScrapinghubClient
from config import cloud_config

logging.basicConfig(level=10)


def run_spider_job():
    """Runs the ufc_scraper spider job in scrapy cloud"""

    client = ScrapinghubClient(cloud_config["API_KEY"])
    spider = client.get_project(580548).spiders.get("ufc_spider")
    job = spider.jobs.run()
    logging.info(f"Job {job.key} scheduled")


if __name__ == "__main__":
    run_spider_job()
