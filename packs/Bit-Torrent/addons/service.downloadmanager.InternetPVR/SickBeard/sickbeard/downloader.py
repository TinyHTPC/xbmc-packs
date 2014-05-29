'''
Created on Apr 24, 2013

@author: Dermot Buckley, dermot@buckley.ie

@todo: this is a terrible mess.  Implement proper locking and abstraction.
'''
from __future__ import with_statement # This isn't required in Python 2.6

import time
import os.path
import pickle
import hashlib
import threading
import traceback

from sickbeard import logger
from sickbeard import version
from sickbeard import helpers
from sickbeard import encodingKludge as ek
from sickbeard.exceptions import ex
from sickbeard.helpers import isMediaFile
from sickbeard import postProcessor
from sickbeard import exceptions
from sickbeard.tv import TVEpisode, TVShow
from sickbeard.common import SNATCHED, WANTED, Quality
import sickbeard

LIBTORRENT_AVAILABLE = False

try:
    #http://www.rasterbar.com/products/libtorrent/manual.html
    import libtorrent as lt
    if (lt.version_major, lt.version_minor) < (0, 16):
        logger.log(u'The version of libtorrent you have installed "' +
                   lt.version + '", is too old for use with sickbeard.  ' +
                   'Version 0.16 or later required.', logger.MESSAGE)
    else:
        logger.log('libtorrent import succeeded, libtorrent is available', logger.MESSAGE)
        LIBTORRENT_AVAILABLE = True
except ImportError:
    logger.log('libtorrent import failed, functionality will not be available', logger.MESSAGE)

# the number of seconds we wait after adding a torrent to see signs of download beginning
TORRENT_START_WAIT_TIMEOUT_SECS = 120

# The actual running lt session.  Obtain it by calling _get_session() - which
# will create it if needed.
_lt_sess = None

# a list of running torrents, each entry being a dict with torrent properties.
running_torrents = []


def get_running_torrents():
    """
    This is just a public accessor for running_torrents.
    @return: (list)
    """
    global running_torrents
    return running_torrents


def _make_key_from_torrent(torrent):
    """
    Will attempt to return the hash from the torrent if it is reasonably obtainable (i.e. without
    having to download the torrent file), otherwise it will return an md5 of the link to the torrent
    file.
    
    @param torrent: (string) url (http or https) to a torrent file, a raw torrent file, or a magnet link
    @return: (string) a key
    """
    if torrent.startswith('magnet:'):
        from sickbeard.providers.generic import TorrentProvider
        return TorrentProvider.getHashFromMagnet(torrent)
    elif torrent.startswith('http://') or torrent.startswith('https://'):
        return md5(torrent)
    else:
        torrent_info = lt.torrent_info(lt.bdecode(torrent))
        return str(torrent_info.info_hash())


def _torrent_has_any_media_files(torrent_info):
    """
    Internal function to check if a torrent has any useful media files.
    @param torrent_info: (a libtorrent torrent_info object)
    @return: (bool) True if any useful media is found, false otherwise.
    """
    for f in torrent_info.files():
        if isMediaFile(f.path):
            return True
    return False

def _blacklist_torrent_url(torrentUrl):
    logger.log(u'Blacklisting the url "%s"' % (torrentUrl), logger.MESSAGE)
    from sickbeard.providers.generic import GenericProvider
    GenericProvider.blacklistUrl(torrentUrl)

def download_from_torrent(torrent, filename=None, postProcessingDone=False, start_time=None, key=None, episodes=[],
                          originalTorrentUrl=None, blacklistOrigUrlOnFailure=False):
    """
    Download the files from a magnet link or torrent url.
    Returns True if the download begins.
    Note: This function will block until the download gives some indication that it
    has started correctly (or TORRENT_START_WAIT_TIMEOUT_SECS is reached).
    
    @param torrent: (string) url (http or https) to a torrent file, a raw torrent file, or a magnet link.
    @param filename: (string) Filename to use while retrieving metadata (only used for urls)
    @param postProcessingDone: (bool) If true, the torrent will be flagged as "already post processed".
    @param start_time: (int) Start time timestamp.  If None (the default), the current timestamp is used. 
    @param key: (string) Unique key to identify torrent.  Just used internally.  If none, a default is generated. 
    @param episodes: ([TVEpisode]) list of TVEpisode objects for which the download applies.
    @param originalTorrentUrl: (string) the url that the torrent was originally pulled from (used for blacklisting)
    @param blacklistOrigUrlOnFailure: (bool) blacklist the 'originalTorrentUrl' (via a call to 
                    GenericProvider.blacklistUrl) if a failure occurs (such as no media files in torrent).  This
                    param has no effect if 'originalTorrentUrl' is not set.
    @return: (bool) True if the download *starts*, False otherwise.
    """
    global running_torrents
    
    try:
        key_to_use = _make_key_from_torrent(torrent) if key is None else key
        if _find_running_torrent_by_field('key', key_to_use):
            logger.log(u'Attempt to add the same torrent twice: ' + key_to_use, logger.ERROR)
            return False
    except Exception, ea:
        logger.log(u'Error in initial parse of torrent ' + ex(ea), logger.ERROR)
        return False
    
    #logger.log(u'episodes: %s' % (repr(episodes)), logger.DEBUG)
    
    try:
        sess = _get_session()
        atp = {}    # add_torrent_params
        atp["save_path"] = _get_save_path(True)
        atp["storage_mode"] = lt.storage_mode_t.storage_mode_sparse
        atp["paused"] = False
        atp["auto_managed"] = True
        atp["duplicate_is_error"] = True
        have_torrentFile = False
        checkedForMedia = False
        if torrent.startswith('magnet:') or torrent.startswith('http://') or torrent.startswith('https://'):
            logger.log(u'Adding torrent to session: %s' % (torrent), logger.DEBUG)
            atp["url"] = torrent.encode('ascii', 'ignore')
            name_to_use = filename
            total_size_to_use = -1
        else:
            e = lt.bdecode(torrent)
            info = lt.torrent_info(e)
            name_to_use = info.name()
            total_size_to_use = info.total_size()
            logger.log(u'Adding torrent to session: %s' % (name_to_use), logger.DEBUG)
            have_torrentFile = True
                
            try:
                atp["resume_data"] = open(os.path.join(atp["save_path"], name_to_use + '.fastresume'), 'rb').read()
            except:
                pass

            if not _torrent_has_any_media_files(info):
                logger.log(u'The torrent %s has no media files.  Not downloading.' % (name_to_use), logger.ERROR)
                if blacklistOrigUrlOnFailure and originalTorrentUrl:
                    _blacklist_torrent_url(originalTorrentUrl)
                    return False
            else:
                checkedForMedia = True
    
            atp["ti"] = info
        
        start_time = time.time()
        h = sess.add_torrent(atp)
    
        #handles.append(h)
        running_torrents.append({
            'lock': threading.Lock(),
            'name': name_to_use,
            'torrent': torrent,
            'key': key_to_use,
            'handle': h,
            'post_processed': postProcessingDone,
            'have_torrentFile': have_torrentFile,
            'start_time': time.time() if start_time is None else start_time,
            'status': 'added',
            'progress': -1.0,  # i.e. unknown
            'rate_down': -1,
            'rate_up': -1,
            'total_size': total_size_to_use,
            'ratio': 0.0,
            'paused': False,
            'error': None,
            'episodes': episodes,
            'checkedForMedia': checkedForMedia,
            'originalTorrentUrl': originalTorrentUrl,
            'blacklistOrigUrlOnFailure': blacklistOrigUrlOnFailure,
        })
        running_torrent_ptr = running_torrents[len(running_torrents) - 1]

        h.set_max_connections(128)
        h.set_max_uploads(-1)

        startedDownload = False
        while not startedDownload:
            time.sleep(0.5)

            if not h.is_valid():
                logger.log(u'Torrent handle is no longer valid.', logger.DEBUG)
                if _find_running_torrent_by_field('handle', h):
                    _remove_torrent_by_handle(h)
                return False

            s = h.status()

            if h.has_metadata():
                i = h.get_torrent_info()
                name = i.name()

                if not running_torrent_ptr['checkedForMedia']:
                    with running_torrent_ptr['lock']:
                        # Torrent has metadata, but hasn't been checked for valid media yet.  Do so now.
                        if not _torrent_has_any_media_files(i):
                            logger.log(u'Torrent %s has no media files! Deleting it.' % (name), logger.ERROR)
                            _on_failed_torrent(running_torrent_ptr['key'], removeFromRunningTorrents=True,
                                               markEpisodesWanted=True)
                            return False
                        running_torrent_ptr['checkedForMedia'] = True

                running_torrent_ptr['status'] = str(s.state)
                running_torrent_ptr['name'] = name
                running_torrent_ptr['total_size'] = i.total_size()
                running_torrent_ptr['paused'] = s.paused
                running_torrent_ptr['error'] = s.error
                if s.state in [lt.torrent_status.seeding,
                               lt.torrent_status.downloading,
                               lt.torrent_status.finished,
                               lt.torrent_status.downloading_metadata]:
                    logger.log(u'Torrent "%s" has state "%s" (%s), interpreting as snatched' % (name, s.state, repr(s.state)), 
                               logger.MESSAGE)
                    return True
            elif s.state is lt.torrent_status.downloading_metadata and torrent.startswith('magnet:'):
                # if it's a magnet, 'downloading_metadata' is considered a success
                logger.log(u'Torrent has state downloading_metadata, interpreting as snatched', 
                               logger.MESSAGE)
                return True
            else:
                # no metadata and not a magnet?  Definitely not started yet then!
                pass
            
            # check for timeout
            if time.time() - start_time > TORRENT_START_WAIT_TIMEOUT_SECS:
                logger.log(u'Torrent has failed to start within timeout %d secs.  Removing' % (TORRENT_START_WAIT_TIMEOUT_SECS),
                           logger.WARNING)
                _remove_torrent_by_handle(h)
                return False
                
    except Exception, e:
        logger.log('Error trying to download via libtorrent: ' + ex(e), logger.ERROR)
        logger.log(traceback.format_exc(), logger.DEBUG)
        try:
            # remove the entry from running_torrents if it's there
            theEntry = _find_running_torrent_by_field('key', key_to_use)
            if theEntry: running_torrents.remove(theEntry)
        except Exception:
            pass
        return False
    
def delete_torrent(key, deleteFilesToo=True):
    """
    Delete a running torrent by key.
    @return: (bool, string) Tuple with (success, errorMessage)
    """
    global running_torrents
    theEntry = _find_running_torrent_by_field('key', key)
    if theEntry:
        _remove_torrent_by_handle(theEntry['handle'], deleteFilesToo)
        return (True, u'')
    else:
        return (False, u'Torrent not found')
    
def set_max_dl_speed(max_dl_speed):
    """
    Set the download rate limit for libtorrent if it's running
    @param max_dl_speed: integer.  Rate in kB/s 
    """
    sess = _get_session(False)
    if sess:
        sess.set_download_rate_limit(max_dl_speed * 1024)

def set_max_ul_speed(max_ul_speed):
    """
    Set the upload rate limit for libtorrent if it's running
    @param max_ul_speed: integer.  Rate in kB/s 
    """
    sess = _get_session(False)
    if sess:
        sess.set_upload_rate_limit(max_ul_speed * 1024)
    
def _get_session(createIfNeeded=True):
    global _lt_sess
    if _lt_sess is None and createIfNeeded:
        _lt_sess = lt.session()
        _lt_sess.set_download_rate_limit(sickbeard.LIBTORRENT_MAX_DL_SPEED * 1024)
        _lt_sess.set_upload_rate_limit(sickbeard.LIBTORRENT_MAX_UL_SPEED * 1024)
        
        settings = lt.session_settings()
        settings.user_agent = 'sickbeard_bricky-%s/%s' % (version.SICKBEARD_VERSION.replace(' ', '-'), lt.version)
        settings.rate_limit_utp = True # seems this is rqd, otherwise uTP connections don't obey the rate limit
        
        settings.active_downloads = 8
        settings.active_seeds = 12
        settings.active_limit = 20
        
        _lt_sess.listen_on(sickbeard.LIBTORRENT_PORT_MIN, sickbeard.LIBTORRENT_PORT_MAX)
        _lt_sess.set_settings(settings)
        _lt_sess.set_alert_mask(lt.alert.category_t.error_notification |
                                #lt.alert.category_t.port_mapping_notification |
                                lt.alert.category_t.storage_notification |
                                #lt.alert.category_t.tracker_notification |
                                lt.alert.category_t.status_notification |
                                #lt.alert.category_t.port_mapping_notification |
                                lt.alert.category_t.performance_warning
                                )
        try:
            state = {} # @todo: save/restore this
            _lt_sess.start_dht(state)
            _lt_sess.add_dht_router('router.bittorrent.com', 6881)
            _lt_sess.add_dht_router('router.utorrent.com', 6881)
            _lt_sess.add_dht_router('router.bitcomet.com', 6881)
        except Exception, ex:
            # just ignore any dht errors, this is just for bootstrapping
            logger.log(u'Exception starting dht: ' + str(ex), logger.WARNING)
        
    return _lt_sess

def _get_save_path(ensureExists=False):
    """
    Get the save path for torrent data
    """
    pth = os.path.join(sickbeard.LIBTORRENT_WORKING_DIR, 'data')
    if ensureExists and not os.path.exists(pth):
            os.makedirs(pth)
    return pth

def _get_running_path(ensureExists=False):
    """
    Get the save path for running torrent info
    """
    pth = os.path.join(sickbeard.LIBTORRENT_WORKING_DIR, 'running')
    if ensureExists and not os.path.exists(pth):
            os.makedirs(pth)
    return pth

# def add_suffix(val):
#     prefix = ['B', 'kB', 'MB', 'GB', 'TB']
#     for i in range(len(prefix)):
#         if abs(val) < 1000:
#             if i == 0:
#                 return '%5.3g%s' % (val, prefix[i])
#             else:
#                 return '%4.3g%s' % (val, prefix[i])
#         val /= 1000
# 
#     return '%6.3gPB' % val

def md5(string):
    hasher = hashlib.md5()
    hasher.update(string)
    return hasher.hexdigest()

def _remove_torrent_by_handle(h, deleteFilesToo=True):
    global running_torrents
    sess = _get_session(False)
    if sess:
        theEntry = _find_running_torrent_by_field('handle', h)
        running_torrents.remove(theEntry)
        try:
            fr_file = os.path.join(_get_save_path(),
                                   theEntry['handle'].get_torrent_info().name() + '.fastresume')
            os.remove(fr_file)
        except Exception:
            pass
        sess.remove_torrent(theEntry['handle'], 1 if deleteFilesToo else 0)
        
def _find_running_torrent_by_field(fieldname, value):
    global running_torrents
    #theEntry = next(d for d in running_torrents if d['handle'] == h) -- requires python 2.6
    matches = [d for d in running_torrents if d[fieldname] == value]
    if len(matches):
        return matches[0]
    else:
        return False
        
def _get_running_torrents_pickle_path(createDirsIfNeeded=False):
    torrent_save_dir = _get_running_path(createDirsIfNeeded)
    return os.path.join(torrent_save_dir, 'running_torrents.pickle')
        
def _load_saved_torrents(deleteSaveFile=True):
    torrent_save_file = _get_running_torrents_pickle_path(False)
    if os.path.isfile(torrent_save_file):
        try:
            data_from_pickle = pickle.load(open(torrent_save_file, "rb"))
            for td in data_from_pickle:
                if 'episodes' not in td:  # older pickles won't have these...
                    td['episodes'] = []
                if 'originalTorrentUrl' not in td:
                    td['originalTorrentUrl'] = None
                if 'blacklistOrigUrlOnFailure' not in td:
                    td['blacklistOrigUrlOnFailure'] = False

                tvEpObjs = []
                for ep in td['episodes']:
                    shw = helpers.findCertainShow(sickbeard.showList, ep['tvdbid'])
                    tvEpObjs.append(TVEpisode(show=shw, season=ep['season'], episode=ep['episode']))
                download_from_torrent(torrent=td['torrent'],
                                      postProcessingDone=td['post_processed'],
                                      start_time=td['start_time'],
                                      key=td['key'],
                                      episodes=tvEpObjs,
                                      originalTorrentUrl=td['originalTorrentUrl'],
                                      blacklistOrigUrlOnFailure=td['blacklistOrigUrlOnFailure'])
        except Exception, e:
            logger.log(u'Failure while reloading running torrents: %s' % (ex(e)), logger.ERROR)
        if deleteSaveFile:
            os.remove(torrent_save_file)


def _save_running_torrents():
    global running_torrents
    if len(running_torrents):
        data_to_pickle = []
        for torrent_data in running_torrents:

            # we can't pickle TVEpisode objects, so we just pickle the useful info
            # from them, namely the show, season, and episode.
            eps = []
            for ep in torrent_data['episodes']:
                eps.append({'tvdbid': ep.show.tvdbid, 'season': ep.season, 'episode': ep.episode })

            data_to_pickle.append({
                'torrent'           : torrent_data['torrent'],
                'post_processed'    : torrent_data['post_processed'],
                'start_time'        : torrent_data['start_time'],
                'key'               : torrent_data['key'],
                'episodes'          : eps,
                'originalTorrentUrl': torrent_data['originalTorrentUrl'],
                'blacklistOrigUrlOnFailure': torrent_data['blacklistOrigUrlOnFailure'],
            })
            #logger.log(repr(data_to_pickle), logger.DEBUG)
        torrent_save_file = _get_running_torrents_pickle_path(True)
        logger.log(u'Saving running torrents to "%s"' % (torrent_save_file), logger.DEBUG)
        pickle.dump(data_to_pickle, open(torrent_save_file, "wb"))


def _on_failed_torrent(key, removeFromRunningTorrents=True, markEpisodesWanted=False):
    rTorr = _find_running_torrent_by_field('key', key)
    if not rTorr:
        logger.log(u'Failed to locate torrent with key "%s"' % (key), logger.MESSAGE)
        return False

    if rTorr['blacklistOrigUrlOnFailure'] and rTorr['originalTorrentUrl']:
        _blacklist_torrent_url(rTorr['originalTorrentUrl'])

    if markEpisodesWanted:
        if rTorr['episodes']:
            for ep in rTorr['episodes']:
                # fucked up no?  We need to do this b/c there's no way to *refresh* from the db without
                # actually creating a new TVEpisode object!
                epTemp = TVEpisode(show=ep.show, season=ep.season, episode=ep.episode)
                if epTemp.status in Quality.SNATCHED + Quality.SNATCHED_PROPER:
                    logger.log(u'Changing episode %s status from SNATCHED to WANTED' % (epTemp.prettyName()),
                               logger.MESSAGE)
                    epTemp.status = WANTED
                    epTemp.saveToDB()
                else:
                    logger.log(u'NOT Changing episode %s status to WANTED b/c current '
                               'status is not SNATCHED (actual status is %s)' % (
                                        epTemp.prettyName(), str(epTemp.status)),
                               logger.MESSAGE)
        else:
            logger.log(u'Cannot markEpisodesWanted b/c entry has no episodes',
                   logger.DEBUG)
    else:
        logger.log(u'Not marking episodes as wanted b/c markEpisodesWanted was False',
                   logger.DEBUG)

    if removeFromRunningTorrents:
        _remove_torrent_by_handle(rTorr['handle'], deleteFilesToo=True)

    return True


class TorrentProcessHandler():
    def __init__(self):
        self.shutDownImmediate = False
        self.loadedRunningTorrents = False
        self.amActive = False # just here to keep the scheduler class happy!
        self.lastTorrentStatusLogTS = 0 # timestamp of last log of torrent status
    
    def run(self):
        """
        Called every few seconds to handle any running/finished torrents
        """
        
        if not LIBTORRENT_AVAILABLE:
            return
        
        if not self.loadedRunningTorrents:
            torrent_save_file = _get_running_torrents_pickle_path(False)
            if os.path.isfile(torrent_save_file):
                logger.log(u'Saved torrents found in %s, loading' % (torrent_save_file), logger.DEBUG)
                _load_saved_torrents()
            
            self.loadedRunningTorrents = True    

        sess = _get_session(False)
        if sess is not None:
            while 1:
                a = sess.pop_alert()
                if not a: break
                
                if type(a) == str:
                    logger.log(a, logger.DEBUG)
                else:
                    logger.log(u'(%s): %s' % (type(a).__name__, ek.fixStupidEncodings(a.message(), True)), logger.DEBUG)
                    
            logTorrentStatus = (time.time() - self.lastTorrentStatusLogTS) >= 600
                
            for torrent_data in running_torrents:
                if torrent_data['handle'].has_metadata():
                    ti = torrent_data['handle'].get_torrent_info()
                    name = ti.name()
                    torrent_data['name'] = name
                    torrent_data['total_size'] = ti.total_size()
                    
                    if not torrent_data['have_torrentFile']:
                        # if this was a magnet or url, and we now have downloaded the metadata
                        # for it, best to save it locally in case we need to resume
                        ti = torrent_data['handle'].get_torrent_info()
                        torrentFile = lt.create_torrent(ti)
                        torrent_data['torrent'] = lt.bencode(torrentFile.generate())
                        torrent_data['have_torrentFile'] = True
                        logger.log(u'Created torrent file for %s as metadata d/l is now complete' % (name), logger.DEBUG)

                    if not torrent_data['checkedForMedia']:
                        with torrent_data['lock']:
                            # Torrent has metadata, but hasn't been checked for valid media yet.  Do so now.
                            if not _torrent_has_any_media_files(ti):
                                logger.log(u'Torrent %s has no media files! Deleting it.' % (name), logger.ERROR)
                                _on_failed_torrent(torrent_data['key'], removeFromRunningTorrents=True,
                                               markEpisodesWanted=True)
                                break  # continue here would be nice, but safer to break b/c we have modified the list

                            torrent_data['checkedForMedia'] = True

                else:
                    name = '-'
                    
                s = torrent_data['handle'].status()
                torrent_data['status'] = str(s.state)
                torrent_data['progress'] = s.progress
                torrent_data['rate_down'] = s.download_rate
                torrent_data['rate_up'] = s.upload_rate
                torrent_data['paused'] = s.paused
                torrent_data['error'] = s.error
                
                #currentRatio = 0.0 if s.total_download == 0 else float(s.total_upload)/float(s.total_download)
                currentRatio = 0.0 if s.all_time_download == 0 else float(s.all_time_upload)/float(s.all_time_download)
                torrent_data['ratio'] = currentRatio
                
                if s.state in [lt.torrent_status.seeding,
                               lt.torrent_status.finished]:
                    with torrent_data['lock']:
                        # this is the post-processing & removing code, so make sure that there's
                        # only one thread doing either here, as the two could easily interfere with
                        # one another
                        if not torrent_data['post_processed']:
                            # torrent has just completed download, so we need to do
                            # post-processing on it.
                            ti = torrent_data['handle'].get_torrent_info()
                            any_file_success = False
                            for f in ti.files():
                                fullpath = os.path.join(sickbeard.LIBTORRENT_WORKING_DIR, 'data', f.path)
                                logger.log(u'Post-processing "%s"' % (fullpath), logger.DEBUG)
                                if isMediaFile(fullpath):
                                    logger.log(u'this is a media file', logger.DEBUG)
                                    try:
                                        processor = postProcessor.PostProcessor(fullpath, name)
                                        if processor.process(forceKeepOriginalFiles=True):
                                            logger.log(u'Success post-processing "%s"' % (fullpath), logger.DEBUG)
                                            any_file_success = True
                                    except exceptions.PostProcessingFailed, e:
                                        logger.log(u'Failed post-processing file "%s" with error "%s"' % (fullpath, ex(e)), 
                                                   logger.ERROR)
                                        
                            if not any_file_success:
                                logger.log(u'When post-processing the completed torrent %s, no useful files were found.' % (name), logger.ERROR)
                                
                            torrent_data['post_processed'] = True
                        else:
                            # post-processing has already been performed.  So we just 
                            # need to ensure check the ratio and delete the torrent
                            # if we're good.
                            if currentRatio >= sickbeard.LIBTORRENT_SEED_TO_RATIO:
                                logger.log(u'Torrent "%s" has seeded to ratio %f.  Removing it.' % (name, currentRatio), logger.MESSAGE)
                                deleteFilesToo = True
                                if not torrent_data['post_processed']:
                                    logger.log(u'Torrent has not been post_processed.  Keeping files.', logger.MESSAGE)
                                    deleteFilesToo = False
                                _remove_torrent_by_handle(torrent_data['handle'], deleteFilesToo)
                            else:
                                if logTorrentStatus:
                                    self.lastTorrentStatusLogTS = time.time()
                                    logger.log(u'"%s" seeding %0.3f' % (name, currentRatio), logger.DEBUG)
                elif s.state == lt.torrent_status.downloading:
                    if logTorrentStatus:
                        self.lastTorrentStatusLogTS = time.time()
                        logger.log(u'"%s" downloading %0.2f' % (name, s.progress * 100.0), logger.DEBUG)
                        
            if self.shutDownImmediate:
                # there's an immediate shutdown waiting to happen, save any running torrents
                # and get ready to stop
                logger.log(u"Torrent shutdown immediate", logger.DEBUG)
                sess.pause()
                for torrent_data in running_torrents:
                    h = torrent_data['handle']
                    if not h.is_valid() or not h.has_metadata():
                        continue
                    data = lt.bencode(torrent_data['handle'].write_resume_data())
                    save_path = _get_save_path(True)
                    tname = h.get_torrent_info().name()
                    logger.log(u'Saving fastresume data for "%s"' % (tname), logger.DEBUG)
                    open(os.path.join(save_path, tname + '.fastresume'), 'wb').write(data)
                
                _save_running_torrents()
                
                # We do this to encourage cleanup of the session (in particular
                # closing any open file handles).
                del sess
                _lt_sess = None
                
                # normally this wouldn't matter of course, because we'd be truly
                # shutting down, but often the case is that sickbeard is actually
                # restarting, so we don't benefit from the cleanup associated with
                # stopping the main thread.
                
