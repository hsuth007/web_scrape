import subprocess

import logging
logging.basicConfig(level=logging.INFO)


logger = logging.getLogger(__name__)
sports_news_sites_uids = ['nbcsports', 'espn']


def main():
    extract()
    transform()
    load()


def extract():
    logger.info('Starting extract')
    for sports_news_site_uid in sports_news_sites_uids:
        subprocess.run(['python', 'main.py', sports_news_site_uid], cwd='./ext')
        subprocess.run(['find', '.', '-name', '{}*'.format(sports_news_site_uid),
                        '-exec', 'mv', '{}', '../trans/{}_.csv'.format(sports_news_site_uid), ';'], cwd='./ext')


def transform():
    logger.info('Starting transform')
    for sports_news_site_uid in sports_news_sites_uids:
        dirty_data_filename = '{}_.csv'.format(sports_news_site_uid)
        clean_data_filename = 'clean_{}'.format(dirty_data_filename)
        subprocess.run(['python', 'main.py', dirty_data_filename], cwd='./trans')
        subprocess.run(['rm', dirty_data_filename], cwd='./trans')
        subprocess.run(['cp', clean_data_filename, '../load/{}.csv'.format(sports_news_site_uid)], cwd='./trans')


def load():
    logger.info('Starting load')
    for sports_news_site_uid in sports_news_sites_uids:
        clean_data_filename = '{}.csv'.format(sports_news_site_uid)
        subprocess.run(['python', 'main.py', clean_data_filename], cwd='./load')
        subprocess.run(['rm', clean_data_filename], cwd='./load')


if __name__ == '__main__':
    main()
