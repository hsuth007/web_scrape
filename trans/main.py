from nltk.corpus import stopwords
from urllib.parse import urlparse

import pandas as pd

import argparse
import hashlib
import logging
import nltk

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main(filename):
    logger.info('Data transformation has started...')

    df = read_data(filename)
    source_uid = extract_source_uid(filename)
    df = add_source_uid_column(df, source_uid)
    df = extract_host(df)
    df = fill_missing_titles(df)
    df = generate_uids_for_rows(df)
    df = remove_new_lines_from_body(df)
    df = validate_words(df, 'body')
    df = validate_words(df, 'title')
    df = remove_duplicate_entries(df, 'title')
    df = drop_rows_with_missing_values(df)

    save_data(df, filename)

    return df


def read_data(filename):
    logger.info('Reading file {}'.format(filename))

    return pd.read_csv(filename)


def extract_source_uid(filename):
    logger.info('Extracting source uid')
    source_uid = filename.split('_')[0]

    logger.info('Source uid detected: {}'.format(source_uid))
    return source_uid


def add_source_uid_column(df, source_uid):
    logger.info('Filling source_uid column with {}'.format(source_uid))
    df['source_uid'] = source_uid

    return df


def extract_host(df):
    logger.info('Extracting host from urls')
    df['host'] = df['url'].apply(lambda url: urlparse(url).netloc)

    return df


def fill_missing_titles(df):
    logger.info('Filling missing titles')
    missing_titles_mask = df['title'].isna()

    missing_titles = (df[missing_titles_mask]['url']
                      .str.extract(r'(?P<missing_titles>[^/]+)$')
                      .applymap(lambda title: title.replace('-', ' ').capitalize())
                      )

    df.loc[missing_titles_mask, 'title'] = missing_titles.loc[:, 'missing_titles']

    return df


def generate_uids_for_rows(df):
    logger.info('Generating uids for rows')

    uids = (df.apply(lambda row: hashlib.md5(bytes(row['url'].encode())), axis=1)
            .apply(lambda hash_object: hash_object.hexdigest()))

    df['uids'] = uids

    return df.set_index('uids')


def remove_new_lines_from_body(df):
    logger.info('Removing new lines from body')

    stripped_body = (df.apply(lambda row: row['body'], axis=1)
                     .apply(lambda body: body.replace('\n', ' '))
                     .apply(lambda body: body.replace('\t', ' '))
                     )

    df['body'] = stripped_body

    return df


def validate_words(df, column_name):
    logger.info('Starting to validate words in {}'.format(column_name))
    stop_words = set(stopwords.words('spanish'))

    def tokenize_column(df, column_name):
        logger.info('Tokenizing {}'.format(column_name))

        return (df
                .dropna()
                .apply(lambda row: nltk.word_tokenize(row[column_name]), axis=1)
                .apply(lambda tokens: list(filter(lambda token: token.isalpha(), tokens)))
                .apply(lambda tokens: list(map(lambda tokens: tokens.lower(), tokens)))
                .apply(lambda word_list: list(filter(lambda words: words not in stop_words, word_list)))
                .apply(lambda valid_word_list: len(valid_word_list))
                )

    df['n_tokens_{}'.format(column_name)] = tokenize_column(df, '{}'.format(column_name))

    return df


def remove_duplicate_entries(df, column_name):
    logger.info('Removing duplicate entries')
    df.drop_duplicates(subset=[column_name], keep='first', inplace=True)

    return df


def drop_rows_with_missing_values(df):
    logger.info('Dropping rows with missing values')
    return df.dropna()


def save_data(df, filename):
    clean_filename = 'clean_{}'.format(filename)
    logger.info('Saving data at location {}'.format(clean_filename))

    df.to_csv(clean_filename)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('filename',
                        help='Path to the dirty data',
                        type=str)

    args = parser.parse_args()

    df = main(args.filename)
    print(df)