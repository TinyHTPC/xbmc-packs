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
#
# @author: Dermot Buckley <dermot@buckley.ie>

import re
import subprocess
import threading
import time
import tempfile
import os
import glob
import shutil

import sickbeard
import generic

from sickbeard import logger
from sickbeard import tvcache
from sickbeard.common import Quality
from sickbeard.helpers import listMediaFiles, isMediaFile
from sickbeard.processTV import processDir
from sickbeard.name_parser.parser import NameParser

FIELD_SEP = '|||'   # field separator used when spliting fields

IPLAYER_LIST_FIELDNAMES =  [ 
   'pid', 'index', 'name', 'seriesnum', 'episode', 
   'episodenum', 'versions', 'type',
   'categories',
   # 'desc',  'thumbnail', 
   #'web', 'channel', 'categories',  'duration', 
   #  'available', 'timeadded' 
   ]

"""
The time we will wait (in secs) for get_iplayer to completed a snatch
(i.e. start a download)
"""
IPLAYER_SNATCH_TIMEOUT_SECS = 60 

# eg. 1114354.601 kB / 3545.09 sec (99.9%)
IPLAYER_DL_PROGRESS_PATTERN = '^(?P<size>\d*\.?\d* kB) / (?P<time>\d*\.?\d*) sec \((?P<perc>\d*\.?\d*)%\).*'

class Iplayer:
    """
    Common interface to get_iplayer calls and utils
    """
    
    @classmethod
    def get_iplayer_path(cls):
        """
        Get the full path to the get_iplayer perl script
        """
        if sickbeard.IPLAYER_GETIPLAYER_PATH and sickbeard.IPLAYER_GETIPLAYER_PATH is not '':
            return sickbeard.IPLAYER_GETIPLAYER_PATH
        else:
            # use our included get_iplayer script if no path is set in config.ini
            return os.path.join(sickbeard.PROG_DIR, 'lib', 'get_iplayer', 'get_iplayer')

    @classmethod
    def iplayer_quality_to_sb_quality(cls, iplayer_q):
        """
        iplayer ref: http://beebhack.wikia.com/wiki/IPlayer_TV#Comparison_Table
        SB ref: https://code.google.com/p/sickbeard/wiki/QualitySettings
        
        @param iplayer_q: (string) quality, one of flashhd,flashvhigh,flashhigh,flashstd,flashnormal,flashlow,n95_wifi
        @return: (int) one of the sickbeard.common.Quality values 
        """
        if iplayer_q == 'flashhd':
            return Quality.HDWEBDL
        if iplayer_q == 'flashvhigh':
            return Quality.HDTV
        if iplayer_q in ('flashhigh', 'iphone', 'flashlow', 'flashstd', 'flashnormal', 'n95_wifi', 'n95_3g'):
            return Quality.SDTV
        else:
            # everything else is unknown for now
            return Quality.UNKNOWN
    
    @classmethod
    def iplayer_quality_to_sb_quality_string(cls, iplayer_q):
        """
        Given an iPlayer quality, returns a string which SB will think is about the same quality.
        (per rules in sickbeard.common.Quality.nameQuality)
        """
        if iplayer_q == 'flashhd':
            return '720p.web.dl'
        if iplayer_q == 'flashvhigh':
            return 'hr.ws.pdtv.x264'
        if iplayer_q in ('flashhigh', 'iphone', 'flashlow', 'flashstd', 'flashnormal', 'n95_wifi', 'n95_3g'):
            return 'HDTV.XviD'
        else:
            return iplayer_q
        
    @classmethod
    def download_pid(cls, pid, with_subs=True, with_metadata=True):
        """
        Start the download of a pid.  Return True if the download *starts* successfully.
        This method will block for a while until the download starts (or times out)
        
        @param pid: (string) BBC pid (a short string)
        @param with_subs: (bool) True to include subs if available.
        @param with_metadata: (bool) True to include xbmc metadata (if available)
        @return: (bool) True => Snatched.
        """
        
        def _finish_download_process():
            """
            Finish downloading a pid
            (this is a closure, called in another thread)
            """
            
            last_reported_perc = 0.0
            
            while p.poll() is None:
                line = p.stdout.readline()
                if line:
                    line = line.rstrip()
                    match = re.match(IPLAYER_DL_PROGRESS_PATTERN, line, re.IGNORECASE)
                    if match:
                        dlSize = match.group('size')
                        dlTime = match.group('time')
                        dlPerc = float(match.group('perc'))
                        if dlPerc - last_reported_perc >= 10.0:
                            # only report progress every 10% or so.
                            logger.log(u"RUNNING iPLAYER: "+line, logger.DEBUG)
                            last_reported_perc = dlPerc
                    else:
                        # not a progress line, echo it to debug
                        logger.log(u"RUNNING iPLAYER: "+line, logger.DEBUG)
                            
                        
            
            logger.log(u"RUNNING iPLAYER: process has ended, returncode was " + 
                       repr(p.returncode) , logger.DEBUG)
            
            # We will need to rename some of the files in the folder to ensure 
            # that sb is comfortable with them.
            videoFiles = listMediaFiles(tmp_dir)
            for videoFile in videoFiles:
                filePrefix, fileExt = os.path.splitext(videoFile)
                if fileExt and fileExt[0] == '.': 
                    fileExt = fileExt[1:]
                
                # split again to get the quality
                filePrePrefix, fileQuality = os.path.splitext(filePrefix)   
                if fileQuality and fileQuality[0] == '.': 
                    fileQuality = fileQuality[1:]   
                qual_str = cls.iplayer_quality_to_sb_quality_string(fileQuality)
                
                # reassemble the filename again, with new quality
                newFilePrefix = filePrePrefix + '.' + qual_str
                newFileName = newFilePrefix + '.' + fileExt
                
                if newFileName != videoFile:    # just in case!
                    logger.log('Renaming %s to %s' % (videoFile, newFileName), logger.DEBUG)
                    os.rename(videoFile, newFileName)
                    
                    # Also need to rename any associated files (nfo and srt)
                    for otherFile in glob.glob(newFilePrefix + '.*'):
                        if otherFile == newFileName:
                            continue
                        otherFilePrefix, otherFileExt = os.path.splitext(otherFile)
                        newOtherFile = newFilePrefix + otherFileExt
                        logger.log('Renaming %s to %s' % (otherFile, newOtherFile), logger.DEBUG)
                        os.rename(otherFile, newOtherFile)
                    
            
            # Ok, we're done with *our* post-processing, so let SB do its own.
            processResult = processDir(tmp_dir)
            #logger.log(u"processDir returned " + processResult , logger.DEBUG) - this is long, and quite useless!
            
            files_remaining = os.listdir(tmp_dir)
            can_delete = True
            for filename in files_remaining:
                fullFilePath = os.path.join(tmp_dir, filename)
                isVideo = isMediaFile(fullFilePath)
                if isVideo:
                    can_delete = False # keep the folder - something prob went wrong
                    logger.log('Found a media file after processing, something probably went wrong: ' + fullFilePath, logger.MESSAGE)
                else:
                    logger.log('Extra file left over (will be deleted if no media found): ' + fullFilePath, logger.DEBUG)
            
            # tidy up - delete our temp dir
        
            if can_delete and os.path.isdir(tmp_dir):
                logger.log('Removing temp dir: ' + tmp_dir, logger.DEBUG)
                shutil.rmtree(tmp_dir)
                
        
        
        tmp_dir = tempfile.mkdtemp()
        iplayer_path = cls.get_iplayer_path()
        
        if iplayer_path is None: 
            return False
        
        cmd = [ iplayer_path,
                '--get',
                '--pid=' + pid,
                '--nocopyright', 
                '--attempts=10',
                '--modes=best',
                '--force',  # stop complaints about already being downloaded
                '--file-prefix="<nameshort>-<senum>-<pid>.<mode>"',
                '--output="' + tmp_dir + '"',   # we save to tmp_dir first
                ]
        
        if with_subs:
            cmd.append('--subtitles')
        
        if with_metadata:
            cmd.append('--metadata=xbmc')
            
        if sickbeard.IPLAYER_EXTRA_PARAMS:
            cmd.append(sickbeard.IPLAYER_EXTRA_PARAMS)
            
        cmd = " ".join(cmd) 
            
        logger.log(u"get_iplayer (cmd) = "+repr(cmd), logger.DEBUG)
        
        start_time = time.time()
        
        # we need a shell b/c it's a perl script and it will need to find the 
        # interpreter
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, 
                             stderr=subprocess.STDOUT, 
                             shell=True, universal_newlines=True) 
        
        while p.poll() is None:
            line = p.stdout.readline()
            while line:
                line = line.rstrip()
                logger.log(u"RUNNING iPLAYER: " + line, logger.DEBUG)
                
                # download progress lines look like:
                # 1114354.601 kB / 3545.09 sec (99.9%)
                match = re.match(IPLAYER_DL_PROGRESS_PATTERN, line, re.IGNORECASE)
                if match:
                    logger.log(u"RUNNING iPLAYER: Got a progress line, d/l started", logger.DEBUG)
                    
                    # ok, we can hand this off to the monitoring thread, and 
                    # return True (for SNATCHED)
                    
                    logger.log(u"Forking new thread to monitor, and returning True (for snatched)", logger.DEBUG)
                    t = threading.Thread(target=_finish_download_process)
                    t.start() 
                    
                    return True
                
                line = p.stdout.readline()
                
            if time.time() - start_time > IPLAYER_SNATCH_TIMEOUT_SECS:
                # Timeout!
                logger.log(u"RUNNING iPLAYER: process timeout after %d secs, killing"%IPLAYER_SNATCH_TIMEOUT_SECS, 
                           logger.WARNING)
                p.terminate()
                return False
            
            # give the process a little time to do stuff before checking again
            time.sleep(0.05)
        
        # process has ended - must be an error
        logger.log(u"RUNNING iPLAYER: process has ended too soon (failure), returncode was " + 
                   repr(p.returncode) , logger.WARNING)
        lines = p.stdout.read()
        if lines:
            logger.log(u"RUNNING iPLAYER: last data was: " + lines, logger.WARNING)
        return False

    
            
    @classmethod
    def get_available_downloads(cls, since=None):
        """
        Get a list of available downloads from get_iplayer.
        
        @param since: added since (number of hours - same as 'since' switch to 
                      get_iplayer).  If None, this is omitted
        @return: Returns a list of dicts, each dict being a pid available for 
                 download.  Each dict will have the keys from 
                 IPLAYER_LIST_FIELDNAMES
        """
        iplayer_path = cls.get_iplayer_path()
        if iplayer_path is None:
            return []
        
        cmd = [ iplayer_path,
                '--listformat',
                '"<' + (('>' + FIELD_SEP + '<').join(IPLAYER_LIST_FIELDNAMES)) + '>"', 
                '--nocopyright', 
                '--refresh',   # Refresh cache
                '--since 24', # only shows added in the last 24 hours
                ]
        
        if sickbeard.IPLAYER_EXTRA_PARAMS:
            cmd.append(sickbeard.IPLAYER_EXTRA_PARAMS)
        
        cmd = " ".join(cmd) # not quite sure why, but Popen doesn't like the list
        
        logger.log(u"get_iplayer (cmd) = "+repr(cmd), logger.DEBUG)
        
        # we need a shell b/c it's a perl script and it will need to find the 
        # interpreter
        os.environ['PYTHONIOENCODING'] = 'utf-8'
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, 
                             shell=True, universal_newlines=True) 
        out, err = p.communicate()
        
        #logger.log(u"get_iplayer (out) = "+repr(out), logger.DEBUG)
        logger.log(u"get_iplayer (err) = "+repr(err), logger.DEBUG)
        
        results = []
        
        for line in out.splitlines():
            line = line.decode('utf-8')
            logger.log(u"Got line: "+repr(line), logger.DEBUG)
            fields = line.split(FIELD_SEP)
            
            if len(fields) != len(IPLAYER_LIST_FIELDNAMES):
                logger.log(u"Ignoring line '%s', it has the wrong number of fields"%line, 
                           logger.DEBUG)
                continue
            
            fkeyed = dict((fieldname, fields[IPLAYER_LIST_FIELDNAMES.index(fieldname)]) 
                          for fieldname in IPLAYER_LIST_FIELDNAMES)
            
            # Sometimes pid is preceeded with 'Added: ', if so we remove it
            if fkeyed['pid'].startswith(u'Added: '):
                fkeyed['pid'] = fkeyed['pid'][7:]
            
            results.append(fkeyed)
            
        return results
    
    @classmethod
    def get_available_downloads_for_showname(cls, showName):
        """
        Get a list of available downloads from get_iplayer.
        
        @param showName: search term (the show, um, name)
        @return: Returns a list of dicts, each dict being a pid available for 
                 download.  Each dict will have the keys from 
                 IPLAYER_LIST_FIELDNAMES
        """
        iplayer_path = cls.get_iplayer_path()
        if iplayer_path is None:
            return []
        
        cmd = [ iplayer_path,
                '--listformat',
                '"<' + (('>' + FIELD_SEP + '<').join(IPLAYER_LIST_FIELDNAMES)) + '>"', 
                '--nocopyright', 
                '"' + showName + '"',
                ]
        
        if sickbeard.IPLAYER_EXTRA_PARAMS:
            cmd.append(sickbeard.IPLAYER_EXTRA_PARAMS)
        
        cmd = " ".join(cmd) # not quite sure why, but Popen doesn't like the list
        
        logger.log(u"get_iplayer (cmd) = "+repr(cmd), logger.DEBUG)
        
        # we need a shell b/c it's a perl script and it will need to find the 
        # interpreter
        os.environ['PYTHONIOENCODING'] = 'utf-8'
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, 
                             shell=True, universal_newlines=True) 
        out, err = p.communicate()
        
        #logger.log(u"get_iplayer (out) = "+repr(out), logger.DEBUG)
        logger.log(u"get_iplayer (err) = "+repr(err), logger.DEBUG)
        
        results = []
        
        for line in out.splitlines():
            line = line.decode('utf-8')
            logger.log(u"Got line: "+repr(line), logger.DEBUG)
            fields = line.split(FIELD_SEP)
            
            if len(fields) != len(IPLAYER_LIST_FIELDNAMES):
                logger.log(u"Ignoring line '%s', it has the wrong number of fields"%line, 
                           logger.DEBUG)
                continue
            
            fkeyed = dict((fieldname, fields[IPLAYER_LIST_FIELDNAMES.index(fieldname)]) 
                          for fieldname in IPLAYER_LIST_FIELDNAMES)
            
            # Sometimes pid is preceeded with 'Added: ', if so we remove it
            if fkeyed['pid'].startswith(u'Added: '):
                fkeyed['pid'] = fkeyed['pid'][7:]
            
            results.append(fkeyed)
            
        return results
            

class IplayerProvider(generic.VODProvider):

    def __init__(self):
        generic.VODProvider.__init__(self, "iPlayer")
        self.supportsBacklog = True
        self.cache = IplayerCache(self)
        self.url = 'http://www.bbc.co.uk/iplayer'

    def isEnabled(self):
        return sickbeard.IPLAYER
    
    def downloadResult(self, result):
        """
        Overridden to handle iplayer snatch.
        The .url property of result should be an iplayer pid.
        """
        logger.log(u"Downloading a result from " + self.name+" at " + result.url)
        return Iplayer.download_pid(result.url, True, True)
    
    def findSeasonResults(self, show, season):
        results = {}
        if show.air_by_date:
            logger.log(u"iplayer doesn't support air-by-date backlog (or at least this implementation doesn't)", logger.WARNING)
            return results  
        results = generic.VODProvider.findSeasonResults(self, show, season)
        return results
    
    
    def _doSearch(self, search_params, show=None):
        """
        A little hackish perhaps, but the only search term we use is the show.name
        from the show param.
        """
        if show is None: 
            return []
        
        logger.log(u"Search for show: " + show.name, logger.DEBUG)
        
        items = Iplayer.get_available_downloads_for_showname(show.name)
        if not items:
            return []
        
        logger.log(u"Got items: " + repr(items), logger.DEBUG)
        
        results = []
        for curItem in items:
            fakeFilename, fakeUrl, season, episode, qual, tvdb_id = IplayerProvider.sickbeardify_iplayer_result(curItem)
            results.append({
                'filename': fakeFilename,
                'url': fakeUrl,
                'season': season,
                'episode': episode,
                'quality': qual,
                'tvdb_id': tvdb_id,
                            }) 

        return results
    
    def _get_title_and_url(self, item):
        """
        Retrieves the title and URL data from a key-pair iplayer result line
        (this shouldn't really be necessary, but I couldn't be bothered rewriting
        all the crap that uses it. sorry)
        """
        return (item['filename'], item['url'])
    
    def getQuality(self, item):
        """
        Figures out the quality of the key-pair iplayer result line
        (again, makes little sense now)
        """
        return item['quality']
    
    @classmethod
    def sickbeardify_iplayer_result(cls, item):
        """
        Turn an iplayer result (with keys: episodenum, seriesnum, name, episode, categories, pid)
        into something that sickbeard would understand, a list with:
        filename, url, season, episode, quality, and tvdb_id
        """
        if item['episodenum'] is u'':
            episode = None
        else:
            episode = int(item['episodenum'])
        
        # if the seriesnum is blank, make is series 1 (that's how tvdb works)
        if item['seriesnum'] is u'':
            season = 1
        else:
            season = int(item['seriesnum'])
            
        # often the 'name' will have the series number tagged onto the end
        match = re.match('^(?P<showname>.*): Series ' + item['seriesnum'] + '$', item['name'], re.IGNORECASE)
        if match:
            item['name'] = match.group('showname')
        
        if episode is None:
            filename = None
        else:
            filename = u'%s S%dE%d - %s' % (item['name'], season, episode, item['episode'])
        fakeUrl = item['pid']
        
        # it looks like anything available in HD has 'HD' in the categories.
        # so use that as our quality flag
        cats = item['categories'].split(',')
        if u'HD' in cats:
            qual = Quality.HDWEBDL
        else:
            qual = Quality.SDTV
            
        # get the tvdb_id also (SB has some trouble identifying the series here otherwise)
        tvdb_id = NameParser.series_name_to_tvdb_id(item['name'])

        return filename, fakeUrl, season, episode, qual, tvdb_id


class IplayerCache(tvcache.TVCache):

    def __init__(self, provider):
        tvcache.TVCache.__init__(self, provider)
        self.minTime = 15

    def updateCache(self):

        if not self.shouldUpdate():
            return

        # @todo: put in a reasonable 'since' value here, prob calc'ed from self.lastUpdate
        results = Iplayer.get_available_downloads()
        self._clearCache()
        
        for fkeyed in results:
            fakeFilename, fakeUrl, season, episode, qual, tvdb_id = IplayerProvider.sickbeardify_iplayer_result(fkeyed) 
            if fakeFilename is None:
                continue # can't add without at least a filename
            self._addCacheEntry(name=fakeFilename, url=fakeUrl, season=season,
                                episodes=[episode], quality=qual,
                                tvdb_id=tvdb_id)
            
        self.setLastUpdate()  # record the feed as being updated

provider = IplayerProvider()
