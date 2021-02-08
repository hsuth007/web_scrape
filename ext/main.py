#!/usr/bin/env python3
from requests.exceptions import HTTPError
from urllib3.exceptions import MaxRetryError
from common import config

import page_objects as sportsnews

import argparse
import csv
import datetime
import re
import logging
logging.basicConfig(level=logging.INFO)


proper_url = re.compile(r'^https?://.+/.+$')
root_path = re.compile(r'^/.+$')
logger = logging.getLogger(__name__)


def sports_news_scraper(news_site_uid):
    host = config()['sports_news_sites'][news_site_uid]['url']

    logging.info('Initializing scraper for {}'.format(host))
    logging.info('Finding news links on homepage...')

    homepage = sportsnews.HomePage(news_site_uid, host)

    articles = []
    for link in homepage.article_links:
        article = fetch_article(news_site_uid, host, link)

        if article:
            logger.info('Article fetched!!')
            article.append(article)
            print(article.title)

    save_articles(news_site_uid, articles)


def fetch_article(news_site_uid, host, link):
    logger.info('Fetching article from {}'.format(link))

    article = None
    try:
        article = sportsnews.ArticlePage(news_site_uid, build_link(host, link))
    except (HTTPError, MaxRetryError) as e:
        logger.warning('Error while fetching article!', exc_info=False)

    if article and not article.body:    # checks for body
        logger.warning('Invalid article. Body is missing.')
        return None

    return article


def build_link(host, link):
    if proper_url.match(link):
        return link
    elif root_path.match(link):
        return '{host}{uri}'.format(host=host, uri=link)
    else:
        return '{host}/{uri}'.format(host=host, uri=link)


def save_articles(news_site_uid, articles):
    now = datetime.datetime.now()
    csv_headers = list(filter(lambda properties: not property.startwith('_'), dir(articles[0])))
    out_file_name = '{news_site_uid}_{datetime}_articles.csv'.format(news_site_uid=news_site_uid,
                                                                     datetime=now.strftime('%Y_%m_%d'))

    with open(out_file_name, mode='w+') as f:
        writer = csv.writer(f)
        writer.writerow(csv_headers)

        for article in articles:
            row = [str(getattr(article, prop)) for prop in csv_headers]
            writer.writerow(row)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    news_options = list(config()['sports_news_sites'].keys())
    parser.add_argument('sports_news_site',
                        help='Select the sports news site for scraping',
                        type=str,
                        choices=news_options
                        )

    args = parser.parse_args()
    sports_news_scraper(args.sports_news_site)
