from article import Article
from base import Base, engine, Session

import pandas as pd

import argparse
import logging
logging.basicConfig(level=logging.INFO)


logger = logging.getLogger(__name__)


def main(filename):
    Base.metadata.create_all(engine)
    session = Session()
    articles = pd.read_csv(filename)

    for index, row in articles.iterrows():
        logger.info('Loading article uid {} into DB'.format(row['uids']))
        article = Article(row['uids'],
                          row['body'],
                          row['host'],
                          row['source_uid'],
                          row['n_tokens_body'],
                          row['n_tokens_title'],
                          row['title'],
                          row['url'])

        session.add(article)

    session.commit()
    session.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('filename',
                        help='Select the file needed to seed db',
                        type=str)

    args = parser.parse_args()
    main(args.filename)
