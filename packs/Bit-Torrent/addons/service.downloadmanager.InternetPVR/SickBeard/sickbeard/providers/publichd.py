# @author: Dermot Buckley <dermot@buckley.ie>
# Adapted from ezrss.py, original author of which is Nic Wolfe <nic@wolfeden.ca>
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
#  GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Sick Beard.  If not, see <http://www.gnu.org/licenses/>.

import sickbeard
import generic
import re

from sickbeard import helpers, logger, exceptions, tvcache


class PublicHdProvider(generic.TorrentProvider):

    def __init__(self):
        generic.TorrentProvider.__init__(self, "PublicHD")

        self.supportsBacklog = False
        self.cache = PublicHdCache(self)
        self.url = 'http://publichd.se/'

    def isEnabled(self):
        return sickbeard.PUBLICHD

    def imageName(self):
        return 'publichd.png'

    def _get_title_and_url(self, item):
        title = helpers.get_xml_text(item.find('title'))
        # logger.log('publichd got title' + title)
        url = None
        if sickbeard.PREFER_MAGNETS:
            magnetURI = helpers.get_xml_text(item.find('{http://xmlns.ezrss.it/0.1/}torrent/{http://xmlns.ezrss.it/0.1/}magnetURI'))
            # logger.log('publichd got magnetURI' + magnetURI)
            if magnetURI:
                url = magnetURI

        if not url:
            enclos = item.find('enclosure')
            if enclos is not None:
                url = enclos.get('url')
                # logger.log('publichd got enclosure url ' + url)
                if url:
                    url = url.replace('&amp;', '&')

        if title.startswith('[TORRENT] '):
            title = title[10:]

        # these guys also get creative with the torrent names, adding crud at the
        # end like "[PublicHD]", "[P2PDL]" etc. which confuses sb.  Best to
        # just remove it if present
        crudAtEndMatch = re.match(r'(.*) \[\w+\]$', title)
        if crudAtEndMatch:
            title = crudAtEndMatch.group(1)

        return (title, url)

    def isValidCategory(self, item):
        """
        Decides if the category of an item (from the rss feed) could be a valid
        tv show.
        @param item: An elementTree Node representing the <item> tag of the RSS feed
        @return: boolean
        """
        category = helpers.get_xml_text(item.find('category'))
        return category in ('BluRay 720p', 'BluRay 1080p', 'BluRay Remux',
                            'BluRay', 'BluRay 3D', 'XviD', 'BRRip',
                            'HDTV', 'SDTV', 'TV WEB-DL', 'TV Packs')


class PublicHdCache(tvcache.TVCache):

    def __init__(self, provider):
        tvcache.TVCache.__init__(self, provider)
        self.minTime = 15   # 15 mins

    def _getRSSData(self):

        url = 'http://publichd.se/rss.php'  # for now this is all we can do, no params accepted
        logger.log(u"PublicHD cache update URL: " + url, logger.DEBUG)
        data = self.provider.getURL(url)
        return data

    def _parseItem(self, item):

        (title, url) = self.provider._get_title_and_url(item)
        if not title or not url:
            logger.log(u"The XML returned from the PublicHD RSS feed is incomplete, this result is unusable", logger.ERROR)
            return

        if url and self.provider.urlIsBlacklisted(url):
            logger.log(u'The url "%s" for "%s" is blacklisted, ignoring' % (url, title), logger.DEBUG)
            return

        logger.log(u"Adding item from RSS to cache: " + title, logger.DEBUG)
        self._addCacheEntry(title, url)

provider = PublicHdProvider()
