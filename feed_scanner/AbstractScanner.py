# -*- coding: utf-8 -*-
import yaml
from urlparse import urlparse
import os, errno, socket
import logging, urllib2
import re


logger = logging.getLogger(__name__)

logger.propagate = True


class AbstractScanner:
    '''
    A base class for feed crawler.
    '''

    def __init__(self, bangumi, episode_list):
        fr = open('./config/config.yml', 'r')
        config = yaml.load(fr)
        self.base_path = config['download']['location']
        self.feedparser = config['feedparser']
        self.proxy = self._get_proxy(bangumi.rss)
        self.bangumi_path = self.base_path + '/' + str(self.bangumi.id)

        self.bangumi = bangumi
        self.episode_list = episode_list

        if 'timeout' in self.feedparser:
            self.timeout = int(self.feedparser['timeout'])
        else:
            self.timeout = None

        try:
            # create an path for bangumi using bangumi.id
            if not os.path.exists(self.bangumi_path):
                os.makedirs(self.bangumi_path)
                info_file = open(self.bangumi_path + '/info.txt', 'w')
                info_file.write(self.bangumi.name.encode('utf-8'))
                info_file.close()
                logger.info('create dir for %s', self.bangumi.name)
        except OSError as exception:
            if exception.errno != errno.EEXIST:
                raise exception

    def get_url_name(self, url):
        '''
        get the site name by given url
        :param url:
        :return: the site name if not found return default
        '''
        url_name_map = {
            'share.dmhy.org': 'dmhy',
            'bangumi.moe': 'bangumi',
            'nyaa.se': 'nyaa',
            'acg.rip': 'acg_rip'
        }
        location = urlparse(url)[1]

        if location in url_name_map:
            return url_name_map[location]
        else:
            return 'default'

    def _get_proxy(self, rss_url):
        '''
        get the proxy config from config and given url,
        if url specific config is not found using the default config.
        if config is an string, treat it as proxy url, use it for all three schemes
        if config is an dict, make sure it has all scheme set and use it directly
        :param rss_url:
        :return: an dict of config
        '''
        if 'proxy' in self.feedparser:
            proxy_config = self.feedparser['proxy']
            url_name = self.get_url_name(rss_url)
            # find config by name, if not found, use default, if default is not set, return None
            if url_name in proxy_config:
                proxy_for_name = proxy_config[url_name]
            elif 'default' in proxy_config:
                proxy_for_name = proxy_config['default']
            else:
                return None

            if type(proxy_for_name) is str:
                return {'http': proxy_for_name, 'https': proxy_for_name, 'ftp': proxy_for_name}
            elif type(proxy_for_name) is dict:
                return proxy_for_name
            else:
                return None

    def parse_episode_number(self, eps_title):
        '''
        parse the episode number from episode title, it use a list of regular expressions. the position in the list
        is the priority of the regular expression.
        :param eps_title: the title of episode.
        :return: episode number if matched, otherwise, -1
        '''
        try:
            regex_tuple = (u'第(\d+)話', u'第(\d+)话', '\[(\d+)(?:v\d)?\]', '\s(\d+)\s', '(\d+)(?![-p])')
            for regex in regex_tuple:
                search_result = re.search(regex, eps_title, re.U)
                if search_result is not None:
                    return int(search_result.group(1))

            return -1
        except Exception as error:
            logger.warn(error)
            return -1

    def parse_feed(self):
        '''
        subclass should implement this method
        :return: an list of tuples of (download_url, eps_no)
        '''
        pass

    @classmethod
    def has_keyword(cls, bangumi):
        '''
        check if current bangumi has the keyword for this source. the subclass must implement this method
        :param bangumi:
        :return: True if the bangumi has the keyword of current source
        '''
        pass