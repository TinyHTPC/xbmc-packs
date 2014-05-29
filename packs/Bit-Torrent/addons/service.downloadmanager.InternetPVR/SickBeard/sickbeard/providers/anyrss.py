# Author: Dermot Buckley <dermot@buckley.ie>
#
# This file is part of Sick Beard.
#
# Sick Beard is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Sick Beard is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Sick Beard.  If not, see <http://www.gnu.org/licenses/>.


import os
import xml.dom.minidom

import sickbeard
import generic

from sickbeard import helpers
from sickbeard import encodingKludge as ek

from sickbeard import logger
from sickbeard import tvcache
from sickbeard.exceptions import ex

CONFIG_SEP = '|||'


class AnyRssProvider(generic.TorrentProvider):

    def __init__(self, name, url):

        generic.TorrentProvider.__init__(self, name)
        self.cache = AnyRssCache(self)
        self.url = url
        self.enabled = True
        self.supportsBacklog = False

    def configStr(self):
        return self.name + CONFIG_SEP + str(int(self.enabled)) + CONFIG_SEP + self.url

    @classmethod
    def fromConfigStr(cls, configString):
        name, enabled, url = configString.split(CONFIG_SEP)
        p = cls(name, url)
        p.enabled = enabled == '1'
        return p

    def imageName(self):
        return 'anyrss.png'

    def isEnabled(self):
        return self.enabled

    def _get_title_and_url(self, item):
        title = helpers.get_xml_text(item.find('title'))

        # Finding the url for the torrent can be a bit tricky, as everyone seems to have their own
        # ideas as to where it should be.
        # cf. http://www.bittorrent.org/beps/bep_0036.html (but note that this isn't entirely reliable, 
        # or indeed correct).

        url = None
        if sickbeard.PREFER_MAGNETS:
            # if we have a preference for magnets, go straight for the throat...
            url = helpers.get_xml_text(item.find('{http://xmlns.ezrss.it/0.1/}torrent/{http://xmlns.ezrss.it/0.1/}magnetURI'))

        if not url:

            # If there's an 'enclosure' tag, then we can be reasonably confident that
            # its url attribute will be the torrent url.
            enclos = item.find('enclosure')
            if enclos:
                url = enclos.get('url')

        if not url:
            # next port-of-call is the 'link' tag, we use this if it looks like
            # a torrent link
            url = helpers.get_xml_text(item.find('link'))
            if url and (url.startswith('magnet:') or url.endswith('.torrent')):
                # found!
                pass
            else:
                url = helpers.get_xml_text(item.find('{http://xmlns.ezrss.it/0.1/}torrent/{http://xmlns.ezrss.it/0.1/}magnetURI'))
                if not url:
                    # No magnetURI?  then use the infoHash
                    infoHash = helpers.get_xml_text(item.find('{http://xmlns.ezrss.it/0.1/}torrent/{http://xmlns.ezrss.it/0.1/}infoHash'))
                    if infoHash:
                        url = 'magnet:?xt=urn:btih:' + infoHash
                if not url:
                    # Nothing yet?  Then I guess we just have to use the link
                    # tag, even if it doesn't look like a torrent
                    url = helpers.get_xml_text(item.find('link'))

        if url:
            # Ditto, badly formed rss can have newlines and other crap around the 
            # url, and even spaces in the url.
            url = url.replace('&amp;','&').strip().replace(' ', '%20')

        return (title, url)

    def verifyRss(self):
        """Runs some basic validation on the rss url.
        @return: (bool, string) Returns a tuple.  The bool indicates success, the string will
                                give a reason for failure if the boolean is false.
        """
        try:
            data = self.getURL(self.url)
            if not data:
                return (False, 'No data returned from url: ' + self.url)

            parsedXML = helpers.parse_xml(data)
            if parsedXML is None:
                return (False, 'Unable to parse RSS - is it valid xml? ' + self.url)

            items = parsedXML.findall('.//item')

            if len(items) == 0:
                # Maybe this isn't really a failure?  Not sure what's best here
                return (False, 'There were no items in the RSS feed from %s' % self.url)

            checkItem = items[0]
            (title, url) = self._get_title_and_url(checkItem)
            if not title:
                return (False, 'Failed to get title from first item in feed.')

            if not url:
                return (False, 'Failed to get torrent url from first item in feed.')

            if url.startswith('magnet:'):
                # we just assume that magnet links are ok
                return (True, 'First torrent appears to be ok')
            else:

                torrentFile = self.getURL(url)

                if torrentFile == None:
                    return (False, 'Empty torrent file when downloading first torrent in feed.')

                if not self.is_valid_torrent_data(torrentFile):
                    return (False, 'First torrent in feed does not appear to be valid torrent file (wrong magic number)')

            return (True, 'First torrent in feed verified successfully')
        except Exception, e:
            return (False, 'Error when trying to load RSS: ' + ex(e))


class AnyRssCache(tvcache.TVCache):

    def __init__(self, provider):

        tvcache.TVCache.__init__(self, provider)
        self.minTime = 15

    def _getRSSData(self):

        url = self.provider.url
        logger.log(u"AnyRssCache cache update URL: " + url, logger.DEBUG)
        data = self.provider.getURL(url)
        return data

    def _parseItem(self, item):
        
        (title, url) = self.provider._get_title_and_url(item)
        if not title or not url:
            logger.log(u"The XML returned from the RSS feed is incomplete, this result is unusable", logger.ERROR)
            return
        
        if url and self.provider.urlIsBlacklisted(url):
            logger.log(u'The url "%s" for "%s" is blacklisted, ignoring' % (url, title), logger.DEBUG)
            return

        logger.log(u"Adding item from RSS to cache: " + title, logger.DEBUG)
        self._addCacheEntry(title, url)

