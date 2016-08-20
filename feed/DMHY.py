import feedparser
from utils.exceptions import SchedulerError
import socket
import logging, urllib2
from feed.Feed import Feed

logger = logging.getLogger(__name__)

logger.propagate = True

class DMHY(Feed):

    def __init__(self, bangumi, episode_list):
        super(self.__class__, self).__init__(bangumi, episode_list)
        self.feed_url = 'https://share.dmhy.org/topics/rss/rss.xml?keyword=%s'.format((bangumi.dmhy,))

    def parse_feed(self):
        '''
        parse feed for current bangumi and find not downloaded episode in feed entries.
        this method using an async call to add torrent.
        :param timeout:
        :return: if no error when get feed None is return otherwise return the error object
        '''
        # eps no list
        logger.debug('start scan %s (%s), url is %s', self.bangumi.name, self.bangumi.id, self.bangumi.rss)
        eps_no_list = [eps.episode_no for eps in self.episode_list]

        default_timeout = socket.getdefaulttimeout()
        # set timeout is provided
        if self.timeout is not None:
            socket.setdefaulttimeout(self.timeout)

        # use handlers
        if self.proxy is not None:
            proxy_handler = urllib2.ProxyHandler(self.proxy)
            feed_dict = feedparser.parse(self.feed_url, handlers=[proxy_handler])
        else:
            feed_dict = feedparser.parse(self.feed_url)

        # restore the default timeout
        if self.timeout is not None:
            socket.setdefaulttimeout(default_timeout)

        if feed_dict.bozo != 0:
            raise SchedulerError(feed_dict.bozo_exception)

        result_list = []

        for item in feed_dict.entries:
            eps_no = self.parse_episode_number(item['title'])
            if eps_no in eps_no_list:
                result_list.append((item.enclosures[0].href, eps_no))
                # d = self.add_to_download(item, eps_no)
                # d.addCallback(self.download_callback)

        return result_list

    @classmethod
    def has_keyword(cls, bangumi):
        return bangumi.dmhy is not None

    # @inlineCallbacks
    # def add_to_download(self, item, eps_no):
    #     '''
    #     add current episode to download, when download is added, update episode status and add torrent_file record
    #     :param item: the item of corresponding episode, it contains an enclosure list which has magnet uri
    #     :param eps_no: the episode number
    #     :return: the episode number, the return value is useless
    #     '''
    #     magnet_uri = item.enclosures[0].href
    #     torrent_file = yield threads.blockingCallFromThread(reactor, download_manager.download, magnet_uri, self.bangumi_path)
    #
    #     if torrent_file is None:
    #         logger.warn('episode %s of %s added failed', eps_no, self.bangumi.name)
    #         returnValue(eps_no)
    #     else:
    #
    #         episode = None
    #         for eps in self.episode_list:
    #             if eps_no == eps.episode_no:
    #                 episode = eps
    #                 break
    #
    #         if episode.torrent_files is not list:
    #             episode.torrent_files = []
    #
    #         episode.torrent_files.append(torrent_file)
    #
    #         episode.status = Episode.STATUS_DOWNLOADING
    #
    #         logger.info('episode %s of %s added', eps_no, self.bangumi.name)
    #
    #         returnValue(eps_no)
    #
    # def download_callback(self, eps_no):
    #     pass
