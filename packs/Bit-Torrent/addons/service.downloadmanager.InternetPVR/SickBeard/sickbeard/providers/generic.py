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
#
# @author: Dermot Buckley <dermot@buckley.ie>
# Adapted from the original, which was authored by Nic Wolfe <nic@wolfeden.ca>

from __future__ import with_statement # This isn't required in Python 2.6

import datetime
import os
import re
import copy
import traceback
import base64
import time
import xml.dom.minidom

import sickbeard

from sickbeard import helpers, classes, logger, db

from sickbeard.common import Quality, MULTI_EP_RESULT, SEASON_RESULT
from sickbeard import tvcache
from sickbeard import encodingKludge as ek
from sickbeard.exceptions import ex
from sickbeard import downloader

from sickbeard.name_parser.parser import NameParser, InvalidNameException


class GenericProvider:

    NZB = "nzb"
    TORRENT = "torrent"
    VOD = "strm"    # just to keep SB happy, not really an extension like the other two.

    def __init__(self, name):

        # these need to be set in the subclass
        self.providerType = None
        self.name = name
        self.url = ''

        self.supportsBacklog = False

        self.cache = tvcache.TVCache(self)

    def getID(self):
        return GenericProvider.makeID(self.name)

    @staticmethod
    def makeID(name):
        return re.sub("[^\w\d_]", "_", name).lower()

    def imageName(self):
        return self.getID() + '.png'

    def _checkAuth(self):
        return

    def isActive(self):
        if self.providerType == GenericProvider.NZB and sickbeard.USE_NZBS:
            return self.isEnabled()
        elif self.providerType == GenericProvider.TORRENT and sickbeard.USE_TORRENTS:
            return self.isEnabled()
        elif self.providerType == GenericProvider.VOD and sickbeard.USE_VODS:
            return self.isEnabled()
        else:
            return False

    def isEnabled(self):
        """
        This should be overridden and should return the config setting eg. sickbeard.MYPROVIDER
        """
        return False

    def getResult(self, episodes):
        """
        Returns a result of the correct type for this provider
        """

        if self.providerType == GenericProvider.NZB:
            result = classes.NZBSearchResult(episodes)
        elif self.providerType == GenericProvider.TORRENT:
            result = classes.TorrentSearchResult(episodes)
        elif self.providerType == GenericProvider.VOD:
            result = classes.VODSearchResult(episodes)
        else:
            result = classes.SearchResult(episodes)

        result.provider = self

        return result

    def getURL(self, url, headers=None):
        """
        By default this is just a simple urlopen call but this method should be overridden
        for providers with special URL requirements (like cookies)
        """

        if not headers:
            headers = []

        data = helpers.getURL(url, headers)

        if not data:
            logger.log(u"Error loading " + self.name + " URL: " + url, logger.ERROR)
            return None

        return data

    def downloadResult(self, result):
        """
        Save the result to disk.
        """

        logger.log(u"Downloading a result from " + self.name + " at " + result.url)

        data = self.getURL(result.url)

        if not data:
            return False

        # use the appropriate watch folder
        if self.providerType == GenericProvider.NZB:
            saveDir = sickbeard.NZB_DIR
            writeMode = 'w'
        elif self.providerType == GenericProvider.TORRENT:
            saveDir = sickbeard.TORRENT_DIR
            writeMode = 'wb'
        else:
            return False

        # use the result name as the filename
        file_name = ek.ek(os.path.join, saveDir, helpers.sanitizeFileName(result.name) + '.' + self.providerType)

        logger.log(u"Saving to " + file_name, logger.DEBUG)

        try:
            fileOut = open(file_name, writeMode)
            fileOut.write(data)
            fileOut.close()
            helpers.chmodAsParent(file_name)
        except IOError, e:
            logger.log(u"Unable to save the file: " + ex(e), logger.ERROR)
            return False

        # as long as it's a valid download then consider it a successful snatch
        return self._verify_download(file_name)

    def _verify_download(self, file_name=None):
        """
        Checks the saved file to see if it was actually valid, if not then consider the download a failure.
        Returns a Boolean
        """
        # this is now simply overridden when it needs to be.
        return True

    def searchRSS(self):

        self._checkAuth()
        self.cache.updateCache()

        return self.cache.findNeededEpisodes()

    def getQuality(self, item):
        """
        Figures out the quality of the given RSS item node

        item: An elementtree.ElementTree element (or xml.dom.minidom.Node)
            representing the <item> tag of the RSS feed

        Returns a Quality value obtained from the node's data

        """
        (title, url) = self._get_title_and_url(item)  # @UnusedVariable
        quality = Quality.nameQuality(title)
        return quality

    def _doSearch(self):
        return []

    def _get_season_search_strings(self, show, season, episode=None):
        return []

    def _get_episode_search_strings(self, ep_obj):
        return []

    def _get_title_and_url(self, item):
        """
        Retrieves the title and URL data from the item XML node.

        Some Einstein decided to change `item` from a xml.dom.minidom.Node to
        an elementtree.ElementTree element upstream, without taking into
        account that this is the base for *LOTS* of classes, so it will
        basically break every one of them unless they are all changed.
        Why does python even allow this crap?  Strong typing is a good thing
        for a language Guido!

        (so, rant over, we now need to cater for both cases here)

        @param item: An xml.dom.minidom.Node (or an elementtree.ElementTree
                element) representing the <item> tag of the RSS feed.
        @return: A tuple containing two strings representing title and URL
                respectively.
        """
        if isinstance(item, xml.dom.minidom.Node):
            title = helpers.get_xml_text(item.getElementsByTagName('title')[0], mini_dom=True)
            try:
                url = helpers.get_xml_text(item.getElementsByTagName('link')[0], mini_dom=True)
                if url:
                    url = url.replace('&amp;', '&')
            except IndexError:
                url = None
        else:
            title = helpers.get_xml_text(item.find('title'))
            if title:
                title = title.replace(' ', '.')

            url = helpers.get_xml_text(item.find('link'))
            if url:
                url = url.replace('&amp;', '&')

        return (title, url)

    def findEpisode(self, episode, manualSearch=False):

        self._checkAuth()

        # create a copy of the episode, using scene numbering
        episode_scene = copy.copy(episode)
        episode_scene.convertToSceneNumbering()

        logger.log(u'Searching "%s" for "%s" as "%s"'
                   % (self.name, episode.prettyName() , episode_scene.prettyName()))

        self.cache.updateCache()
        results = self.cache.searchCache(episode_scene, manualSearch)
        logger.log(u"Cache results: " + str(results), logger.DEBUG)
        logger.log(u"manualSearch: " + str(manualSearch), logger.DEBUG)

        # if we got some results then use them no matter what.
        # OR
        # return anyway unless we're doing a manual search
        if results or not manualSearch:
            return results

        itemList = []

        for cur_search_string in self._get_episode_search_strings(episode_scene):
            itemList += self._doSearch(cur_search_string, show=episode.show)

        for item in itemList:

            (title, url) = self._get_title_and_url(item)

            if self.urlIsBlacklisted(url):
                logger.log(u'Ignoring %s as the url %s is blacklisted' % (title, url), logger.DEBUG)
                continue

            # parse the file name
            try:
                myParser = NameParser()
                parse_result = myParser.parse(title, fix_scene_numbering=True)
            except InvalidNameException:
                logger.log(u"Unable to parse the filename " + title + " into a valid episode", logger.WARNING)
                continue

            if episode.show.air_by_date:
                if parse_result.air_date != episode.airdate:
                    logger.log(u"Episode " + title + " didn't air on " + str(episode.airdate) + ", skipping it", logger.DEBUG)
                    continue

            elif parse_result.season_number != episode.season or episode.episode not in parse_result.episode_numbers:
                logger.log(u"Episode " + title + " isn't " + str(episode.season) + "x" + str(episode.episode) + ", skipping it", logger.DEBUG)
                continue

            quality = self.getQuality(item)

            if not episode.show.wantEpisode(episode.season, episode.episode, quality, manualSearch):
                logger.log(u"Ignoring result " + title + " because we don't want an episode that is " + Quality.qualityStrings[quality], logger.DEBUG)
                continue

            logger.log(u"Found result " + title + " at " + url, logger.DEBUG)

            result = self.getResult([episode])
            result.url = url
            result.name = title
            result.quality = quality

            results.append(result)

        return results

    def findSeasonResults(self, show, season):

        itemList = []
        results = {}

        for cur_string in self._get_season_search_strings(show, season):
            itemList += self._doSearch(cur_string)

        for item in itemList:

            (title, url) = self._get_title_and_url(item)

            if self.urlIsBlacklisted(url):
                logger.log(u'Ignoring %s as the url %s is blacklisted' % (title, url), logger.DEBUG)
                continue

            quality = self.getQuality(item)

            # parse the file name
            try:
                myParser = NameParser(False)
                parse_result = myParser.parse(title, True)
            except InvalidNameException:
                logger.log(u"Unable to parse the filename " + title + " into a valid episode", logger.WARNING)
                continue

            if not show.air_by_date:
                # this check is meaningless for non-season searches
                if (parse_result.season_number != None and parse_result.season_number != season) or (parse_result.season_number == None and season != 1):
                    logger.log(u"The result " + title + " doesn't seem to be a valid episode for season " + str(season) + ", ignoring")
                    continue

                # we just use the existing info for normal searches
                actual_season = season
                actual_episodes = parse_result.episode_numbers

            else:
                if not parse_result.air_by_date:
                    logger.log(u"This is supposed to be an air-by-date search but the result " + title + " didn't parse as one, skipping it", logger.DEBUG)
                    continue

                myDB = db.DBConnection()
                sql_results = myDB.select("SELECT season, episode FROM tv_episodes WHERE showid = ? AND airdate = ?", [show.tvdbid, parse_result.air_date.toordinal()])

                if len(sql_results) != 1:
                    logger.log(u"Tried to look up the date for the episode " + title + " but the database didn't give proper results, skipping it", logger.WARNING)
                    continue

                actual_season = int(sql_results[0]["season"])
                actual_episodes = [int(sql_results[0]["episode"])]

            # make sure we want the episode
            wantEp = True
            for epNo in actual_episodes:
                if not show.wantEpisode(actual_season, epNo, quality):
                    wantEp = False
                    break

            if not wantEp:
                logger.log(u"Ignoring result " + title + " because we don't want an episode that is " + Quality.qualityStrings[quality], logger.DEBUG)
                continue

            logger.log(u"Found result " + title + " at " + url, logger.DEBUG)

            # make a result object
            epObj = []
            for curEp in actual_episodes:
                epObj.append(show.getEpisode(actual_season, curEp))

            result = self.getResult(epObj)
            result.url = url
            result.name = title
            result.quality = quality

            if len(epObj) == 1:
                epNum = epObj[0].episode
            elif len(epObj) > 1:
                epNum = MULTI_EP_RESULT
                logger.log(u"Separating multi-episode result to check for later - result contains episodes: " + str(parse_result.episode_numbers), logger.DEBUG)
            elif len(epObj) == 0:
                epNum = SEASON_RESULT
                result.extraInfo = [show]
                logger.log(u"Separating full season result to check for later", logger.DEBUG)

            if epNum in results:
                results[epNum].append(result)
            else:
                results[epNum] = [result]

        return results

    def findPropers(self, search_date=None):

        results = self.cache.listPropers(search_date)

        return [classes.Proper(x['name'], x['url'], datetime.datetime.fromtimestamp(x['time'])) for x in results]

    # Dictionary of blacklisted torrent urls.  Keys are the url, values are the 
    # timestamp when it was added
    url_blacklist = {}

    # How long does an entry stay in the URL_BLACKLIST?
    URL_BLACKLIST_EXPIRY_SECS = 172800  # 172800 = 2 days

    @classmethod
    def urlIsBlacklisted(cls, url):
        """
        Check if a url is blacklisted.  
        @param url: (string)
        @return: bool 
        """
        if url is None:
            return False
        if url.startswith('http://extratorrent.com/') or url.startswith('https://extratorrent.com/'):
            # This site is permanently blacklisted (no direct torrent links, just ads)
            return True
        if url in cls.url_blacklist:
            if time.time() - cls.url_blacklist[url] < cls.URL_BLACKLIST_EXPIRY_SECS:
                # still blacklisted
                return True
            else:
                # no longer blacklisted, remove it from the list
                del cls.url_blacklist[url]
        return False
    
    @classmethod
    def blacklistUrl(cls, url):
        """
        Add a url to the blacklist.  It stays there for URL_BLACKLIST_EXPIRY_SECS.
        @param url: (string) 
        """
        if url is not None: 
            cls.url_blacklist[url] = time.time()


class NZBProvider(GenericProvider):

    def __init__(self, name):

        GenericProvider.__init__(self, name)

        self.providerType = GenericProvider.NZB


# This is a list of sites that serve torrent files given the associated hash.
# They will be tried in order, so put the most reliable at the top.
MAGNET_TO_TORRENT_URLS = ['http://torrage.com/torrent/%s.torrent',
                          'http://zoink.it/torrent/%s.torrent',
                          'http://torcache.net/torrent/%s.torrent',
                          'http://torra.ws/torrent/%s.torrent',
                          'http://torrage.ws/torrent/%s.torrent',
                         ]


class TorrentProvider(GenericProvider):

    def __init__(self, name):

        GenericProvider.__init__(self, name)

        self.providerType = GenericProvider.TORRENT

    @classmethod
    def getHashFromCacheLink(cls, link):
        """
        Pulls the hash of a torrent from a link to an online torrent cache site
        (typically one of MAGNET_TO_TORRENT_URLS).

        Returns the 40 byte hex string on success, None on failure.
        """
        for m_to_u in MAGNET_TO_TORRENT_URLS:
            m_to_u.replace('%%s', '([0-9A-Z]{40})', re.I)
            hash_search = re.search(m_to_u, link)
            if hash_search:
                return hash_search.group(1).upper()

        return None

    @classmethod
    def getHashFromMagnet(cls, magnet):
        """
        Pull the hash from a magnet link (if possible).
        Handles the various possible encodings etc.
        (returning a 40 byte hex string).

        Returns None on failure
        """
        logger.log('magnet: ' + magnet, logger.DEBUG)
        info_hash_search = re.search('btih:([0-9A-Z]+)', magnet, re.I)
        if info_hash_search:
            torrent_hash = info_hash_search.group(1)

            # hex hashes will be 40 characters long, base32 will be 32 chars long
            if len(torrent_hash) == 32:
                # convert the base32 to base 16
                logger.log('base32_hash: ' + torrent_hash, logger.DEBUG)
                torrent_hash = base64.b16encode(base64.b32decode(torrent_hash, True))
            elif len(torrent_hash) != 40:
                logger.log('Torrent hash length (%d) is incorrect (should be 40), returning None' % (len(torrent_hash)), logger.DEBUG)
                return None

            logger.log('torrent_hash: ' + torrent_hash, logger.DEBUG)
            return torrent_hash.upper()
        else:
            # failed to pull info hash
            return None

    @classmethod
    def magnetToTorrent(cls, magnet):
        """
        This returns a single (best guess) url for a torrent file for the 
        passed-in magnet link.
        For now it just uses the first entry from MAGNET_TO_TORRENT_URLS.
        If there's any problem with the magnet link, this will return None.
        """
        torrent_hash = cls.getHashFromMagnet(magnet)
        if torrent_hash:
            return MAGNET_TO_TORRENT_URLS[0] % torrent_hash.upper()
        else:
            # failed to pull info hash
            return None

    @classmethod
    def cacheLinkToMagnet(cls, link):
        """
        Turns a link like http://torrage.com/torrent/FF5DC60F2D63339D5F1E1D53B4F099DD0C833658.torrent
        into a magnet link like magnet:?xt=urn:btih:FF5DC60F2D63339D5F1E1D53B4F099DD0C833658

        Returns a magnet link (a string) on success, or None on failure (i.e.
        if 'link' isn't a link to a torrent cache site)
        """
        the_hash = cls.getHashFromCacheLink(link)
        if the_hash:
            return 'magnet:?xt=urn:btih:' + the_hash

        return None

    def getURL(self, url, headers=None):
        """
        Overridden to deal with possible magnet links (but still best to not
        pass magnet links to this - downloadResult has better handling with fallbacks)
        """
        if url and url.startswith('magnet:'):
            torrent_url = self.magnetToTorrent(url)
            if torrent_url:
                logger.log(u"Changed magnet %s to %s" % (url, torrent_url), logger.DEBUG)
                url = torrent_url
            else:
                logger.log(u"Failed to handle magnet url %s, skipping..." % url, logger.DEBUG)
                return None

        # magnet link fixed, just call the base class
        return GenericProvider.getURL(self, url, headers)

    def downloadResult(self, result):
        """
        Overridden to handle magnet links (using multiple fallbacks), and now libtorrent
        downloads also.
        """
        logger.log(u"Downloading a result from " + self.name + " at " + result.url)

        if sickbeard.USE_LIBTORRENT:
            # libtorrent can download torrent files from urls, but it's probably safer for us
            # to do it first so that we can report errors immediately.
            if result.url and (result.url.startswith('http://') or result.url.startswith('https://')):
                torrent = self.getURL(result.url)
                # and now that we have it, we can check the torrent file too!
                if not self.is_valid_torrent_data(torrent):
                    logger.log(u'The torrent retrieved from "%s" is not a valid torrent file.' % (result.url), logger.ERROR)
                    self.blacklistUrl(result.url)
                    return False
            else:
                torrent = result.url

            if torrent:
                return downloader.download_from_torrent(torrent=torrent, filename=result.name,
                                                        episodes=result.episodes, originalTorrentUrl=result.url,
                                                        blacklistOrigUrlOnFailure=True)
            else:
                logger.log(u'Failed to retrieve torrent from "%s"' % (result.url), logger.ERROR)
                return False
        else:
            # Ye olde way, using blackhole ...

            if result.url and result.url.startswith('magnet:'):
                torrent_hash = self.getHashFromMagnet(result.url)
                if torrent_hash:
                    urls = [url_fmt % torrent_hash for url_fmt in MAGNET_TO_TORRENT_URLS]
                else:
                    logger.log(u"Failed to handle magnet url %s, skipping..." % torrent_hash, logger.DEBUG)
                    self.blacklistUrl(result.url)
                    return False
            else:
                urls = [result.url]

            # use the result name as the filename
            fileName = ek.ek(os.path.join, sickbeard.TORRENT_DIR, helpers.sanitizeFileName(result.name) + '.' + self.providerType)

            for url in urls:
                logger.log(u"Trying d/l url: " + url, logger.DEBUG)
                data = self.getURL(url)

                if data == None:
                    logger.log(u"Got no data for " + url, logger.DEBUG)
                    # fall through to next iteration
                elif not self.is_valid_torrent_data(data):
                    logger.log(u"d/l url %s failed, not a valid torrent file" % (url), logger.MESSAGE)
                    self.blacklistUrl(url)
                else:
                    try:
                        fileOut = open(fileName, 'wb')
                        fileOut.write(data)
                        fileOut.close()
                        helpers.chmodAsParent(fileName)
                    except IOError, e:
                        logger.log("Unable to save the file: "+ex(e), logger.ERROR)
                        return False

                    logger.log(u"Success with url: " + url, logger.DEBUG)
                    return True
            else:
                logger.log(u"All d/l urls have failed.  Sorry.", logger.MESSAGE)
                return False

        return False

    def _get_title_and_url(self, item):
        """
        Retrieves the title and URL data from the item XML node.
        Overridden here so that we can have a preference for magnets.

        @see rant in GenericProvider._get_title_and_url
        (yes, this is lazy coding for now)

        item: An xml.dom.minidom.Node representing the <item> tag of the RSS feed
        Returns: A tuple containing two strings representing title and URL respectively
        """
        if isinstance(item, xml.dom.minidom.Node):
            title = helpers.get_xml_text(item.getElementsByTagName('title')[0], mini_dom=True)
            url = None
            try:
                if sickbeard.PREFER_MAGNETS:
                    try:
                        url = helpers.get_xml_text(item.getElementsByTagName('magnetURI')[0], mini_dom=True)
                        torrent_hash = self.getHashFromMagnet(url)
                        if not torrent_hash:
                            logger.log(u'magnetURI "%s" found for "%s", but it has no valid hash - ignoring' % (url, title),
                                       logger.WARNING)
                            url = None
                    except Exception:
                        pass
                if url is None:
                    url = helpers.get_xml_text(item.getElementsByTagName('link')[0], mini_dom=True)
                    if url:
                        url = url.replace('&amp;', '&')
            except IndexError:
                url = None
        else:
            title = helpers.get_xml_text(item.find('title'))
            url = None
            if sickbeard.PREFER_MAGNETS:
                url = helpers.get_xml_text(item.find('{http://xmlns.ezrss.it/0.1/}torrent/{http://xmlns.ezrss.it/0.1/}magnetURI'))
                if url:
                    torrent_hash = self.getHashFromMagnet(url)
                    if not torrent_hash:
                        logger.log(u'magnetURI "%s" found for "%s", but it has no valid hash - ignoring' % (url, title),
                                   logger.WARNING)
                        url = None
            if not url:
                url = helpers.get_xml_text(item.find('link'))
                if url:
                    url = url.replace('&amp;', '&')

        return (title, url)

    def _verify_download(self, file_name=None):
        """
        Checks the saved file to see if it was actually valid, if not then consider the download a failure.
        Returns a Boolean
        """
        logger.log(u"Verifying Download %s" % file_name, logger.DEBUG)
        try:
            with open(file_name, "rb") as f:
                magic = f.read(16)
                if self.is_valid_torrent_data(magic):
                    return True
                else:
                    logger.log("Magic number for %s is neither 'd8:announce' nor 'd12:_info_length', got '%s' instead" % (file_name, magic), logger.WARNING)
                    #logger.log(f.read())
                    return False
        except Exception, eparser:
            logger.log("Failed to read magic numbers from file: "+ex(eparser), logger.ERROR)
            logger.log(traceback.format_exc(), logger.DEBUG)
            return False

    @classmethod
    def is_valid_torrent_data(cls, torrent_file_contents):
        # According to /usr/share/file/magic/archive, the magic number for
        # torrent files is 
        #    d8:announce
        # So instead of messing with buggy parsers (as was done here before)
        # we just check for this magic instead.
        # Note that a significant minority of torrents have a not-so-magic of "d12:_info_length",
        # which while not explicit in the spec is valid bencode and works with Transmission and uTorrent.
        return torrent_file_contents is not None and \
            (torrent_file_contents.startswith("d8:announce") or \
             torrent_file_contents.startswith("d12:_info_length"))


class VODProvider(GenericProvider):
    """
    Video-On-Demand provider
    """

    def __init__(self, name):
        GenericProvider.__init__(self, name)
        self.providerType = GenericProvider.VOD
