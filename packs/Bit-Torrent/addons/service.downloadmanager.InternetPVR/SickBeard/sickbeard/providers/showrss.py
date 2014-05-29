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

import xml.dom.minidom
from xml.dom.minidom import parseString
from pprint import pprint

import re
import time
import sickbeard
import generic

from sickbeard import helpers
from sickbeard import logger
from sickbeard import tvcache
from sickbeard import tvtumbler
from sickbeard.scene_exceptions import get_scene_exceptions


class ShowRssProvider(generic.TorrentProvider):
    

    def __init__(self):

        generic.TorrentProvider.__init__(self, "ShowRSS")
        self.supportsBacklog = True
        self.cache = ShowRssCache(self)
        self.url = 'http://showrss.info/'
        self.backup_urls = ['http://showrss.karmorra.info/', 'http://showrss.info.nyud.net/', ]

    def isEnabled(self):
        return sickbeard.SHOWRSS
        
    def imageName(self):
        return 'showrss.png'
    
    def findSeasonResults(self, show, season):
        
        #logger.log(u'ShowRssProvider.findSeasonResults ' + str(show) + ' Season: ' + str(season), logger.DEBUG)
        results = {}
        if show.air_by_date:
            logger.log(u"ShowRSS doesn't support air-by-date backlog", logger.WARNING)
            return results  
        results = generic.TorrentProvider.findSeasonResults(self, show, season)
        return results

    @classmethod
    def _get_showrss_id(cls, tvdb_id):
        tvt_info = tvtumbler.show_info(tvdb_id)
        if tvt_info and 'showrss_id' in tvt_info:
            return tvt_info['showrss_id']
        else:
            return None

    def _doSearch(self, search_params, show=None):
    
        # we just need one "param" for now, the ShowRssId
        if not 'ShowRssId' in search_params:
            logger.log(u"No ShowRssId passed into _doSearch, search ignored.", logger.WARNING)
            return []
        
      
        searchURL = '%sfeeds/%d.rss' % (self.url, search_params['ShowRssId'])

        logger.log(u"Search string: " + searchURL, logger.DEBUG)

        data = self.getURL(searchURL)

        if not data:
            return []
        
        try:
            parsedXML = parseString(data)
            items = parsedXML.getElementsByTagName('item')
        except Exception, e:
            logger.log(u"Error trying to load ShowRSS RSS feed: " + e, logger.ERROR)
            logger.log(u"RSS data: "+data, logger.DEBUG)
            return []
        
        results = []

        for curItem in items:
            
            (title, url) = self._get_title_and_url(curItem)
            
            if not title or not url:
                logger.log(u"The XML returned from the ShowRSS feed is incomplete, this result is unusable: "+data, logger.ERROR)
                continue
            
            if self.urlIsBlacklisted(url):
                logger.log(u'Ignoring result with url %s as it has been blacklisted' % (url), logger.DEBUG)
                continue
    
            results.append(curItem)

        return results
    
    def _get_season_search_strings(self, show, season=None):
    
        params = {}
        if not show:
            return params
        
        ShowRssId = self._get_showrss_id(show.tvdbid)
        if ShowRssId:
            params['ShowRssId'] = int(ShowRssId)
            return [params]
        
        logger.log(u"Show %s doesn't appear to be known to ShowRSS" % show.name, logger.MESSAGE)
        return []
    
    def _get_episode_search_strings(self, ep_obj):
        if not ep_obj:
            return [{}]
        # we can only usefully query by show, so do that.
        return self._get_season_search_strings(ep_obj.show)

    def _get_title_and_url(self, item):
        '''Yup, this now gets its own "special" parser, because some muppet decided that the ezrss standard
        wasn't good enough for showrss, so they got creative and came up with their own standard.
        Muppets.  "Special" ones.

        This is the crap we have to deal with:
        <item>
            <title>Beauty and the Beast (2012) 2x06 Father Knows Best</title>
            <link>magnet:?xt=urn:btih:836EC00F0DB1AC126D11B22378DC42BB40DADD35&amp;dn=Beauty+and+the+Beast+2012+S02E06+HDTV+x264+2HD&amp;tr=udp://tracker.openbittorrent.com:80&amp;tr=udp://tracker.publicbt.com:80&amp;tr=udp://tracker.istole.it:80&amp;tr=http://tracker.istole.it&amp;tr=http://fr33dom.h33t.com:3310/announce</link>
            <guid isPermaLink="false">569aab610be9c6ee5f81b9afcc8beb59</guid>
            <pubDate>Mon, 11 Nov 2013 04:40:01 +0000</pubDate>
            <description>New standard torrent: Beauty and the Beast (2012) 2x06 Father Knows Best. Link: &lt;a href="magnet:?xt=urn:btih:836EC00F0DB1AC126D11B22378DC42BB40DADD35&amp;dn=Beauty+and+the+Beast+2012+S02E06+HDTV+x264+2HD&amp;tr=udp://tracker.openbittorrent.com:80&amp;tr=udp://tracker.publicbt.com:80&amp;tr=udp://tracker.istole.it:80&amp;tr=http://tracker.istole.it&amp;tr=http://fr33dom.h33t.com:3310/announce"&gt;magnet:?xt=urn:btih:836EC00F0DB1AC126D11B22378DC42BB40DADD35&amp;dn=Beauty+and+the+Beast+2012+S02E06+HDTV+x264+2HD&amp;tr=udp://tracker.openbittorrent.com:80&amp;tr=udp://tracker.publicbt.com:80&amp;tr=udp://tracker.istole.it:80&amp;tr=http://tracker.istole.it&amp;tr=http://fr33dom.h33t.com:3310/announce&lt;/a&gt;</description>
            <showrss:showid>509</showrss:showid>
            <showrss:showname>Beauty and the Beast (2012)</showrss:showname>
            <showrss:episode>30801</showrss:episode>
            <showrss:info_hash>836EC00F0DB1AC126D11B22378DC42BB40DADD35</showrss:info_hash>
            <showrss:rawtitle>Beauty and the Beast 2012 S02E06 HDTV x264 2HD</showrss:rawtitle>
            <enclosure url="magnet:?xt=urn:btih:836EC00F0DB1AC126D11B22378DC42BB40DADD35&amp;dn=Beauty+and+the+Beast+2012+S02E06+HDTV+x264+2HD&amp;tr=udp://tracker.openbittorrent.com:80&amp;tr=udp://tracker.publicbt.com:80&amp;tr=udp://tracker.istole.it:80&amp;tr=http://tracker.istole.it&amp;tr=http://fr33dom.h33t.com:3310/announce" length="0" type="application/x-bittorrent"/>
        </item>
        '''
        if isinstance(item, xml.dom.minidom.Node):
            try:
                title = helpers.get_xml_text(item.getElementsByTagName('showrss:rawtitle')[0], mini_dom=True)
            except Exception:
                title = helpers.get_xml_text(item.getElementsByTagName('title')[0], mini_dom=True)

            url = helpers.get_xml_text(item.getElementsByTagName('link')[0], mini_dom=True)
            if url:
                url = url.replace('&amp;', '&')

            return (title, url)
        else:
            title = helpers.get_xml_text(item.find('{http://showrss.info/}rawtitle'))
            if not title:
                title = helpers.get_xml_text(item.find('title'))
            url = helpers.get_xml_text(item.find('link'))
            if url:
                url = url.replace('&amp;', '&')

            return (title, url)



class ShowRssCache(tvcache.TVCache):

    def __init__(self, provider):

        tvcache.TVCache.__init__(self, provider)

        # only poll ShowRss every 15 minutes max
        self.minTime = 15

    def _getRSSData(self):
        url = self.provider.url + 'feeds/all.rss'   # this is the "global" feed
        logger.log(u"ShowRSS cache update URL: " + url, logger.DEBUG)
        data = self.provider.getURL(url)
        if data:
            return data

        for provider_url in self.provider.backup_urls:
            url = provider_url + 'feeds/all.rss'
            logger.log(u"ShowRSS cache update URL: " + url, logger.DEBUG)
            data = self.provider.getURL(url)
            if data:
                return data

        return None

    def _parseItem(self, item):

        (title, url) = self.provider._get_title_and_url(item)

        if not title or not url:
            logger.log(u"The XML returned from the ShowRss RSS feed is incomplete, this result is unusable", logger.ERROR)
            return
            
        if url and self.provider.urlIsBlacklisted(url):
            # Url is blacklisted, but maybe we can turn it into a magnet which
            # isn't?
            as_magnet = self.provider.cacheLinkToMagnet(url)
            if as_magnet is None or self.provider.urlIsBlacklisted(as_magnet):
                logger.log(u"url %s is blacklisted (and can't be converted to a useful magnet), skipping..." % url, logger.DEBUG)
                return
            else:
                url = as_magnet

        logger.log(u"Adding item from RSS to cache: " + title, logger.DEBUG)

        self._addCacheEntry(title, url)


provider = ShowRssProvider()
