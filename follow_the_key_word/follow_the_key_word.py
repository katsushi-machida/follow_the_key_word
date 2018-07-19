# -*- coding: utf-8 -*-

"""
follow_the_key_word.py

DESCRIPTION
"""

__author__ = 'k-machida'
__version__ = '1.0.0'
__date__ = '2018/06/19'

import argparse
import requests
import cchardet
import logging
import logging.config

from os import path
from bs4 import BeautifulSoup
from urllib.parse import urljoin


log_file_path = path.join(path.dirname(path.abspath(__file__)), 'logging.conf')
logging.config.fileConfig(log_file_path)
logger = logging.getLogger(__name__)


def follow_the_key_word(start_url, key_word):
    """
    実行時の引数A(URL)からURLを辿り、引数B(文字列)の値が出現するURLまでの経路を出力する。

    :param str start_url: search start URL
    :param str key_word: search target key word
    """

    trace_root_list = []
    next_crawl_url_list = None
    crawled_url_list = []

    try:
        search_match_flg, next_crawl_url_list = _search_key_word(
            start_url, key_word)
        trace_root_list.append({start_url: next_crawl_url_list})

        if search_match_flg:
            _out_trace_url(search_match_flg, trace_root_list)
            return

        crawl_continue_flg = True
        while crawl_continue_flg:
            trace_url_dict = {}
            crawl_url_child_list = []
            for url in next_crawl_url_list:
                if url in crawled_url_list:
                    continue

                search_match_flg, child_url_list = _search_key_word(
                    url, key_word)
                trace_url_dict[url] = child_url_list
                if search_match_flg:
                    crawl_continue_flg = False
                    break

                crawled_url_list.append(url)
                crawl_url_child_list.extend(child_url_list)

            if crawl_continue_flg:
                if 0 < len(crawl_url_child_list):
                    next_crawl_url_list = []
                    next_crawl_url_list.extend(crawl_url_child_list)
                else:
                    crawl_continue_flg = False

            trace_root_list.append(trace_url_dict)

        _out_trace_url(search_match_flg, trace_root_list)

    except Exception as e:
        print(u'予期しないエラーが発生しました。')
        logger.exception(u'予期しないエラーが発生しました。: %s', e)


def _search_key_word(url, key_word):
    """
    対象のURLにキーワードが存在するかチェックする。
    存在しない場合、チェック結果に加え、対象のURLに存在するリンクURLを返却する。

    :param str url: search target URL
    :param str key_word: search target key word
    :return: bool: key word exists
    :return: List[str]: Link URL on target URL
    """

    child_url_list = []

    response = None
    try:
        if not is_content_type_html(url):
            return False, child_url_list

        response = requests.get(url)
        response.encoding = cchardet.detect(response.content)["encoding"]

    except Exception as e:
        # 接続時のエラーについては握り潰し、検索候補のURLがなくなるまで続ける
        logger.warning(e)
        return False, child_url_list

    if key_word.lower() in response.text.lower():
        # key word hit
        return True, None

    soup = BeautifulSoup(response.text, "html.parser")
    url_tags = soup.select("a[href]")
    for url_tag in url_tags:
        child_url = urljoin(url, url_tag.attrs['href'])
        if child_url is not None and child_url.lower().startswith('http'):
            child_url_list.append(child_url)

    return False, child_url_list


def is_content_type_html(url):
    """
    対象のURLの`content-type`が`text/html`か判定する

    :param str url: target URL
    :return: bool: is content-type 'text/html'
    """

    response = requests.head(url)
    content_type = response.headers.get('content-type')

    if not content_type:
        return False

    if 'text/html' in content_type.lower():
        return True

    return False


def _out_trace_url(search_match_flg, trace_root_list):
    """
    検索順にURLと子URLが格納されているListから、検索経路を標準出力する。

    :param list[dict {str URL: [str child URL]}] trace_root_list: trace root
    """

    if not search_match_flg:
        print('key word is not found')

    now_point_url = None
    trace_url = []
    for res_dict in (reversed(trace_root_list)):
        for key_url, value_url_list in res_dict.items():
            if len(trace_url) == 0 and value_url_list is None:
                trace_url.insert(0, key_url)
                now_point_url = key_url
                break
            elif now_point_url in value_url_list:
                trace_url.insert(0, key_url)
                now_point_url = key_url
                break

    logger.info('out_trace_url')
    logger.info(trace_url)
    for index in range(len(trace_url)):
        if 0 == index:
            print(trace_url[index])
        else:
            print(' |')
            print(' --' + trace_url[index])


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        prog='follow_the_key_word',
        usage='Demonstration of argparser',
        description='description',
        epilog='end',
        add_help=True,
    )
    parser.add_argument('start_url')
    parser.add_argument('key_word')
    input_args = parser.parse_args()

    follow_the_key_word(input_args.start_url, input_args.key_word)
