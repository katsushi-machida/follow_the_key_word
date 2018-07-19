# -*- coding: utf-8 -*-

import sys
import unittest
import argparse

from io import StringIO
from unittest.mock import patch, MagicMock, PropertyMock
from mock import patch
from follow_the_key_word import follow_the_key_word


class test_follow_the_key_word(unittest.TestCase):
    """follow_the_key_word tests"""

    def test_is_content_type_html(self):
        res = follow_the_key_word.is_content_type_html(
            'https://www.google.com/')
        self.assertTrue(res)

    def test_is_content_type_image(self):
        res = follow_the_key_word.is_content_type_html(
            'https://2.bp.blogspot.com/-avJFYWIu4_s/WI1zYXY2QNI/AAAAAAABBYU/Xe8q_a8YJawkZo0CJcgBvw-7D679lxc3gCLcB/s600/computer_programming_contest.png')
        self.assertFalse(res)

    def test__out_trace_url_single(self):
        trace_url_list = [{'https://google.com': None}]
        io = StringIO()
        sys.stdout = io
        res = follow_the_key_word._out_trace_url(True, trace_url_list)
        sys.stdout = sys.__stdout__
        self.assertEqual(io.getvalue(), 'https://google.com\n')

    def test__out_trace_url_three_stage(self):
        trace_url_list = [{'https://google.com': ['https://google.com/c1', 'https://google.com/c2']}, {'https://google.com/c1': [
            'https://google.com/c1_1', 'https://google.com/c1_2']}, {'https://google.com/c2': ['https://google.com/c2_1']}, {'https://google.com/c2_1': None}]
        io = StringIO()
        sys.stdout = io
        res = follow_the_key_word._out_trace_url(True, trace_url_list)
        sys.stdout = sys.__stdout__
        print_trace_url = [
            'https://google.com',
            ' |',
            ' --https://google.com/c2',
            ' |',
            ' --https://google.com/c2_1',
            '']
        self.assertEqual(io.getvalue(), '\n'.join(print_trace_url))

    def test__search_key_word_hitted(self):
        with open('tests/test1.html', encoding='UTF-8') as f:
            html_data = f.read()
            response = MagicMock()
            response.text = html_data
            response.content = html_data.encode()
            with patch('requests.get', return_value=response):
                res1, res2 = follow_the_key_word._search_key_word(
                    'https://www.google.com', u'キーワード１')
                self.assertTrue(res1)
                self.assertEqual(res2, None)

    def test__search_key_word_not_hitted(self):
        with open('tests/test1.html', encoding='UTF-8') as f:
            html_data = f.read()
            response = MagicMock()
            response.text = html_data
            response.content = html_data.encode()
            with patch('requests.get', return_value=response):
                res1, res2 = follow_the_key_word._search_key_word(
                    'https://www.goo.ne.jp/', u'キーワード2')
                self.assertFalse(res1)
                self.assertEqual(res2, [
                                  'https://www.google.com', 'https://www.goo.ne.jp/soutai1.html', 'https://www.goo.ne.jp/soutai2.html'])

    def test_follow_the_key_word_hitted(self):
        io = StringIO()
        sys.stdout = io
        follow_the_key_word.follow_the_key_word(
            'http://machicloud.tokyo', u'急速充電')
        sys.stdout = sys.__stdout__
        print_trace_url = [
            'http://machicloud.tokyo',
            ' |',
            ' --http://machicloud.tokyo/openrec-fullscreen-%e5%85%a8%e7%94%bb%e9%9d%a2-%e3%83%95%e3%83%ab%e3%82%b9%e3%82%af%e3%83%aa%e3%83%bc%e3%83%b3/',
            ' |',
            ' --http://machicloud.tokyo/pokemon-go-mobile-battery-wifi-anker-zmi-cheero/',
            '']
        self.assertEqual(io.getvalue(), '\n'.join(print_trace_url))

    def test_follow_the_key_word_not_hitted(self):
        io = StringIO()
        sys.stdout = io
        follow_the_key_word.follow_the_key_word(
            'http://gaming-profile.com/google3fc8234faaff6315.html', u'キーワード')
        sys.stdout = sys.__stdout__
        self.assertEqual(io.getvalue(), 'key word is not found\n')

    def test_follow_the_key_word_invalid_url(self):
        io = StringIO()
        sys.stdout = io
        follow_the_key_word.follow_the_key_word(
            'http://machicloud', u'キーワード')
        sys.stdout = sys.__stdout__
        self.assertEqual(io.getvalue(), 'key word is not found\n')


if __name__ == '__main__':
    unittest.main()
