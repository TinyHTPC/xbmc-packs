# Initializes and launches Couchpotato V2, Sickbeard and Headphones

import os
import sys
import shutil
import time
import subprocess
import hashlib
import signal
from xml.dom.minidom import parseString
import logging
import traceback
import platform

#fix
logging.basicConfig(filename="InternetPVR.log",
                    filemode='w',
                    format='%(asctime)s InternetPVR: %(message)s',
                    level=logging.WARNING)

# helper functions
# ----------------

def createDir(dir):
    if not os.path.isdir(dir):
        os.makedirs(dir)

def getAddonSetting(doc,id):
    for element in doc.getElementsByTagName('setting'):
        if element.getAttribute('id')==id:
            return element.getAttribute('value')

def ensure_dir(f):
    print "Checking for location: "+f
    d = os.path.dirname(f)
    if not os.path.exists(d):
        os.makedirs(d)
	print "Not Found! Creating: "+d

def media_link(link, dest):
    print "Checking for location: "+link
    rm = "rm "+link
    ln = "ln -s "+dest+" "+link
    if not os.path.exists(link):
        subprocess.check_output(ln, shell=True)
	print "Not Found! Creating: "+link
    elif os.path.exists(link):
	print "Link Already Found!"
        subprocess.check_output(rm, shell=True)
	print "Removing: "+link
        subprocess.check_output(ln, shell=True)
	print "Creating: "+link

# define some things that we're gonna need, mainly paths
# ------------------------------------------------------

# addon
pAddon                        = os.path.expanduser("~/.xbmc/addons/service.downloadmanager.InternetPVR")
pAddonHome                    = os.path.expanduser("~/.xbmc/userdata/addon_data/service.downloadmanager.InternetPVR")
pAddonlog                     = os.path.expanduser("~/.xbmc/userdata/addon_data/service.downloadmanager.InternetPVR/log")
pUdat                         = os.path.expanduser("~/.xbmc/userdata")

# settings
pDefaultSuiteSettings         = os.path.join(pAddon, "settings-default.xml")
pSuiteSettings                = os.path.join(pAddonHome, "settings.xml")
pXbmcSettings                 = os.path.join(pUdat, "guisettings.xml")
pSickBeardSettings            = os.path.join(pAddonHome, 'sickbeard.ini')
pCouchPotatoServerSettings    = os.path.join(pAddonHome, 'couchpotatoserver.ini')
pHeadphonesSettings           = os.path.join(pAddonHome, 'headphones.ini')
pTransmission_Addon_Settings  = os.path.expanduser("~/.xbmc/userdata/addon_data/service.downloadmanager.transmission/settings.xml")
pTransmission_Settings_New    = os.path.expanduser("~/.xbmc/userdata/addon_data/service.downloadmanager.transmission/settings2.xml")
pTransmission_DIR             = os.path.expanduser("~/.xbmc/addons/service.downloadmanager.transmission")
pTransmission_Stop            = os.path.expanduser("~/.xbmc/addons/service.downloadmanager.transmission/bin/transmission.stop")
pTransmission_Start           = os.path.expanduser("~/.xbmc/addons/service.downloadmanager.transmission/bin/transmission.start")

# service commands
sickBeard                     = ['python', os.path.join(pAddon, 'SickBeard/SickBeard.py'),
                                 '--daemon', '--datadir', pAddonHome, '--config', pSickBeardSettings]
couchPotatoServer             = ['python', os.path.join(pAddon, 'CouchPotatoServer/CouchPotato.py'),
                                 '--daemon', '--pid_file', os.path.join(pAddonHome, 'couchpotato.pid'), '--config_file', pCouchPotatoServerSettings]
headphones                    = ['python', os.path.join(pAddon, 'Headphones/Headphones.py'),
                                 '-d', '--datadir', pAddonHome, '--config', pHeadphonesSettings]

# create directories and settings if missing
# -----------------------------------------------

sbfirstLaunch = not os.path.exists(pSickBeardSettings)
cpfirstLaunch = not os.path.exists(pCouchPotatoServerSettings)
hpfirstLaunch = not os.path.exists(pHeadphonesSettings)
if sbfirstLaunch or cpfirstLaunch or hpfirstLaunch:
    createDir(pAddonHome)
    createDir(pAddonlog)

# create the settings file if missing
if not os.path.exists(pSuiteSettings):
    shutil.copy(pDefaultSuiteSettings, pSuiteSettings)

# read addon and xbmc settings
# ----------------------------

# Transmission-Daemon
if os.path.exists(pTransmission_Addon_Settings):
    fTransmission_Addon_Settings = open(pTransmission_Addon_Settings, 'r')
    data = fTransmission_Addon_Settings.read()
    fTransmission_Addon_Settings.close
    transmission_addon_settings = parseString(data)
    transuser                          = getAddonSetting(transmission_addon_settings, 'TRANSMISSION_USER')
    transpwd                           = getAddonSetting(transmission_addon_settings, 'TRANSMISSION_PWD')
    transauth                          = getAddonSetting(transmission_addon_settings, 'TRANSMISSION_AUTH')
    transdl                            = getAddonSetting(transmission_addon_settings, 'TRANSMISSION_DL_DIR')
    transinc                           = getAddonSetting(transmission_addon_settings, 'TRANSMISSION_INC_DIR')
    transwatch                         = getAddonSetting(transmission_addon_settings, 'TRANSMISSION_WATCH_DIR')
else:
    transauth                          = 'false'

# InternetPVR
fSuiteSettings = open(pSuiteSettings, 'r')
data = fSuiteSettings.read()
fSuiteSettings.close
suiteSettings = parseString(data)
user                          = getAddonSetting(suiteSettings, 'InternetPVR_USER')
pwd                           = getAddonSetting(suiteSettings, 'InternetPVR_PWD')
host                          = getAddonSetting(suiteSettings, 'InternetPVR_IP')
sickbeard_launch              = getAddonSetting(suiteSettings, 'SICKBEARD_LAUNCH')
couchpotato_launch            = getAddonSetting(suiteSettings, 'COUCHPOTATO_LAUNCH')
headphones_launch             = getAddonSetting(suiteSettings, 'HEADPHONES_LAUNCH')
simplemode                    = getAddonSetting(suiteSettings, 'InternetPVR_MODE')
sickbeard_watch_dir           = getAddonSetting(suiteSettings, 'TVSHOW_DIR')
couchpotato_watch_dir         = getAddonSetting(suiteSettings, 'MOVIES_DIR')
headphones_watch_dir          = getAddonSetting(suiteSettings, 'MUSIC_DIR')
transmission_dl_dir           = getAddonSetting(suiteSettings, 'TRANSMISSION_DL_DIR')

# Downloads directories
pHomeDownloadsDir              = transmission_dl_dir
pInternetPVRComplete           = transmission_dl_dir + "complete"
pInternetPVRCompleteTV         = transmission_dl_dir + "complete/tvshows"
pInternetPVRCompleteMov        = transmission_dl_dir + "complete/movies"
pInternetPVRCompleteMus        = transmission_dl_dir + "complete/music"
pInternetPVRWatchDir           = transmission_dl_dir + "torrents"

# merge defaults
fDefaultSuiteSettings         = open(pDefaultSuiteSettings, 'r')
data = fDefaultSuiteSettings.read()
fDefaultSuiteSettings.close
DefaultSuiteSettings = parseString(data)
if not sickbeard_launch:
    sickbeard_launch          = getAddonSetting(DefaultSuiteSettings, 'SICKBEARD_LAUNCH')
if not couchpotato_launch:
    couchpotato_launch        = getAddonSetting(DefaultSuiteSettings, 'COUCHPOTATO_LAUNCH')
if not headphones_launch:
    headphones_launch         = getAddonSetting(DefaultSuiteSettings, 'HEADPHONES_LAUNCH')

# XBMC
fXbmcSettings                 = open(pXbmcSettings, 'r')
data                          = fXbmcSettings.read()
fXbmcSettings.close
xbmcSettings                  = parseString(data)
xbmcServices                  = xbmcSettings.getElementsByTagName('services')[0]
xbmcPort                      = xbmcServices.getElementsByTagName('webserverport')[0].firstChild.data
try:
    xbmcUser                      = xbmcServices.getElementsByTagName('webserverusername')[0].firstChild.data
except:
    xbmcUser                      = ''
try:
    xbmcPwd                       = xbmcServices.getElementsByTagName('webserverpassword')[0].firstChild.data
except:
    xbmcPwd                       = ''

# prepare execution environment
# -----------------------------
signal.signal(signal.SIGCHLD, signal.SIG_DFL)
pPylib                        = os.path.join(pAddon, 'pylib')
if "true" in sickbeard_launch:
    pnamemapper                   = os.path.join(pPylib, 'Cheetah/_namemapper.so')
    if not os.path.exists(pnamemapper):
        try:
            parch                         = platform.machine()
            if parch.startswith('arm'):
                parch = 'arm'
            pmultiarch                    = os.path.join(pPylib, 'multiarch/_namemapper.so.' + parch)
            shutil.copy(pmultiarch, pnamemapper)
            logging.debug('Copied _namemapper.so for ' + parch)
        except Exception,e:
            logging.error('Error Copying _namemapper.so for ' + parch)
            logging.exception(e)
        
os.environ['PYTHONPATH']      = str(os.environ.get('PYTHONPATH')) + ':' + pPylib
sys.path.append(pPylib)
from lib.configobj import ConfigObj

# Create media directories if missing
ensure_dir(sickbeard_watch_dir+"/*")
ensure_dir(couchpotato_watch_dir+"/*")
ensure_dir(headphones_watch_dir+"/*")
ensure_dir(pInternetPVRCompleteTV+"/*")
ensure_dir(pInternetPVRCompleteMov+"/*")
ensure_dir(pInternetPVRCompleteMus+"/*")

# Edit Transmission settings and restart.
print "Edit Transmission settings and restart."
infile = open(pTransmission_Addon_Settings)
outfile = open(pTransmission_Settings_New, 'w')

replacements = {transdl:transmission_dl_dir+'complete', transinc:transmission_dl_dir+'incoming', transwatch:transmission_dl_dir+'torrents'}

for line in infile:
    for src, target in replacements.iteritems():
        line = line.replace(src, target)
    outfile.write(line)
infile.close()
outfile.close()

from os import remove
from shutil import move

remove(pTransmission_Addon_Settings)
move(pTransmission_Settings_New, pTransmission_Addon_Settings)


print "Restarting Transmission..."
subprocess.Popen("chmod -R +x " + pTransmission_DIR + "/bin/*" , shell=True, close_fds=True)
subprocess.Popen(pTransmission_Stop, shell=True, close_fds=True)
time.sleep(15)
subprocess.Popen(pTransmission_Start, shell=True, close_fds=True)
time.sleep(1)

# SickBeard start
try:
    # write SickBeard settings
    # ------------------------
    sickBeardConfig = ConfigObj(pSickBeardSettings,create_empty=True)
    defaultConfig = ConfigObj()
    defaultConfig['General'] = {}
    defaultConfig['General']['launch_browser']      = '0'
    defaultConfig['General']['version_notify']      = '0'
    defaultConfig['General']['web_port']            = '8082'
    defaultConfig['General']['web_host']            = host
    defaultConfig['General']['web_username']        = user
    defaultConfig['General']['web_password']        = pwd
    defaultConfig['General']['cache_dir']           = pAddonHome + '/sbcache'
    defaultConfig['General']['log_dir']             = pAddonHome + '/logs'
    defaultConfig['XBMC'] = {}
    defaultConfig['XBMC']['use_xbmc']               = '1'
    defaultConfig['XBMC']['xbmc_host']              = '127.0.0.1:' + xbmcPort
    defaultConfig['XBMC']['xbmc_username']          = xbmcUser
    defaultConfig['XBMC']['xbmc_password']          = xbmcPwd

    if 'true' in simplemode:
        defaultConfig['General']['tv_download_dir']       = pInternetPVRComplete
        defaultConfig['General']['use_api']               = '1'
        defaultConfig['General']['api_key']               = 'eff2ebc240c91e342e14418874cc7a4f'
        defaultConfig['General']['naming_pattern']        = 'Season %0S/%S.N.S%0SE%0E.%Q.N-%RG'
        defaultConfig['General']['naming_abd_pattern']    = '%SN - %A-D - %EN'
        defaultConfig['General']['metadata_xbmc']         = '0|0|0|0|0|0'
        defaultConfig['General']['keep_processed_dir']    = '0'
        defaultConfig['General']['use_banner']            = '1'
        defaultConfig['General']['rename_episodes']       = '1'
        defaultConfig['General']['naming_ep_name']        = '0'
        defaultConfig['General']['naming_use_periods']    = '1'
        defaultConfig['General']['naming_sep_type']       = '1'
        defaultConfig['General']['naming_ep_type']        = '1'
        defaultConfig['General']['root_dirs']             = '0|' + sickbeard_watch_dir
        defaultConfig['General']['process_automatically'] = '1'
        defaultConfig['Blackhole'] = {}
        defaultConfig['Blackhole']['torrent_dir']         = pInternetPVRWatchDir
        defaultConfig['KAT'] = {}
        defaultConfig['KAT']['kat']                   = '1'
        defaultConfig['Womble'] = {}
        defaultConfig['Womble']['womble']                 = '0'
        defaultConfig['XBMC']['xbmc_notify_ondownload']   = '1'
        defaultConfig['XBMC']['xbmc_notify_onsnatch']     = '1'
        defaultConfig['XBMC']['xbmc_update_library']      = '1'
        defaultConfig['XBMC']['xbmc_update_full']         = '1'

    if sbfirstLaunch:
        defaultConfig['General']['tv_download_dir']       = pInternetPVRComplete
        defaultConfig['General']['use_api']               = '1'
        defaultConfig['General']['api_key']               = 'eff2ebc240c91e342e14418874cc7a4f'
        defaultConfig['General']['naming_pattern']        = 'Season %0S/%S.N.S%0SE%0E.%Q.N-%RG'
        defaultConfig['General']['naming_abd_pattern']    = '%SN - %A-D - %EN'
        defaultConfig['General']['metadata_xbmc']         = '0|0|0|0|0|0'
        defaultConfig['General']['keep_processed_dir']    = '0'
        defaultConfig['General']['use_banner']            = '1'
        defaultConfig['General']['rename_episodes']       = '1'
        defaultConfig['General']['naming_ep_name']        = '0'
        defaultConfig['General']['naming_use_periods']    = '1'
        defaultConfig['General']['naming_sep_type']       = '1'
        defaultConfig['General']['naming_ep_type']        = '1'
        defaultConfig['General']['root_dirs']             = '0|' + sickbeard_watch_dir
        defaultConfig['General']['process_automatically'] = '1'
        defaultConfig['Blackhole'] = {}
        defaultConfig['Blackhole']['torrent_dir']         = pInternetPVRWatchDir
        defaultConfig['KAT'] = {}
        defaultConfig['KAT']['kat']                   = '1'
        defaultConfig['Womble'] = {}
        defaultConfig['Womble']['womble']                 = '0'
        defaultConfig['XBMC']['xbmc_notify_ondownload']   = '1'
        defaultConfig['XBMC']['xbmc_notify_onsnatch']     = '1'
        defaultConfig['XBMC']['xbmc_update_library']      = '1'
        defaultConfig['XBMC']['xbmc_update_full']         = '1'

    sickBeardConfig.merge(defaultConfig)
    sickBeardConfig.write()

    # launch SickBeard
    # ----------------
    if "true" in sickbeard_launch:
        subprocess.call(sickBeard,close_fds=True)
except Exception,e:
    logging.exception(e)
    print 'SickBeard: exception occurred:', e
    print traceback.format_exc()
# SickBeard end

# CouchPotatoServer start
try:
    # empty password hack
    if pwd == '':
        md5pwd = ''
    else:
        #convert password to md5
        md5pwd =  hashlib.md5(str(pwd)).hexdigest()

    # write CouchPotatoServer settings
    # --------------------------
    couchPotatoServerConfig = ConfigObj(pCouchPotatoServerSettings,create_empty=True, list_values=False)
    defaultConfig = ConfigObj()
    defaultConfig['core'] = {}
    defaultConfig['core']['username']               = user
    defaultConfig['core']['password']               = md5pwd
    defaultConfig['core']['port']                   = '8083'
    defaultConfig['core']['launch_browser']         = '0'
    defaultConfig['core']['host']                   = host
    defaultConfig['core']['data_dir']               = pAddonHome
    defaultConfig['core']['show_wizard']            = '0'
    defaultConfig['core']['debug']                  = '0'
    defaultConfig['core']['development']            = '0'
    defaultConfig['updater'] = {}
    defaultConfig['updater']['enabled']             = '0'
    defaultConfig['updater']['notification']        = '0'
    defaultConfig['updater']['automatic']           = '0'
    defaultConfig['xbmc'] = {}
    defaultConfig['xbmc']['enabled']                = '1'
    defaultConfig['xbmc']['host']                   = '127.0.0.1:' + xbmcPort
    defaultConfig['xbmc']['username']               = xbmcUser
    defaultConfig['xbmc']['password']               = xbmcPwd

    if 'true' in simplemode:
        defaultConfig['manage'] = {}
        defaultConfig['manage']['enabled']                = '1'
        defaultConfig['manage']['library']                = couchpotato_watch_dir
        defaultConfig['transmission'] = {}
        defaultConfig['transmission']['host']             = 'localhost:9091'
        defaultConfig['transmission']['directory']        = pInternetPVRCompleteMov
        defaultConfig['transmission']['enabled']          = '1'
        defaultConfig['renamer'] = {}
        defaultConfig['renamer']['enabled']               = '1'
        defaultConfig['renamer']['from']                  = pInternetPVRCompleteMov
        defaultConfig['renamer']['to']                    = couchpotato_watch_dir
        defaultConfig['renamer']['separator']             = '.'
        defaultConfig['renamer']['cleanup']               = '1'
        defaultConfig['renamer']['file_action']           = 'move'
        defaultConfig['renamer']['run_every']             = '1'
        defaultConfig['subtitle'] = {}
        defaultConfig['subtitle']['languages']            = 'en'
        defaultConfig['subtitle']['enabled']              = '1'
        defaultConfig['searcher'] = {}
        defaultConfig['searcher']['preferred_method']     = 'torrent'
        defaultConfig['searcher']['required_words']       = '720p, 1080p'
        defaultConfig['searcher']['preferred_words']      = 'YIFY, x264, BrRip'
        defaultConfig['nzbindex'] = {}
        defaultConfig['nzbindex']['enabled']              = '0'
        defaultConfig['newznab'] = {}
        defaultConfig['newznab']['enabled']               = '0'
        defaultConfig['thepiratebay'] = {}
        defaultConfig['thepiratebay']['enabled']          = '1'
        defaultConfig['yify'] = {}
        defaultConfig['yify']['enabled']                  = '1'
        defaultConfig['yify']['extra_score']              = '30000'

    if 'true' in transauth:
        defaultConfig['transmission'] = {}
        defaultConfig['transmission']['username']         = transuser
        defaultConfig['transmission']['password']         = transpwd
        defaultConfig['transmission']['directory']        = pInternetPVRCompleteMov
        defaultConfig['transmission']['host']             = 'localhost:9091'

    if cpfirstLaunch:
        defaultConfig['core']['api_key']                  = 'f181f1fff3c34ba5bc27b0e1c846cfe4'
        defaultConfig['xbmc']['xbmc_update_library']      = '1'
        defaultConfig['xbmc']['xbmc_update_full']         = '1'
        defaultConfig['xbmc']['xbmc_notify_onsnatch']     = '1'
        defaultConfig['xbmc']['xbmc_notify_ondownload']   = '1'
        defaultConfig['xbmc']['force_full_scan']          = '1'
        defaultConfig['xbmc']['meta_enabled']             = '0'
        defaultConfig['xbmc']['on_snatch']                = '1'
        defaultConfig['blackhole'] = {}
        defaultConfig['blackhole']['directory']           = pInternetPVRWatchDir
        defaultConfig['blackhole']['use_for']             = 'torrent'
        defaultConfig['blackhole']['enabled']             = '0'
        defaultConfig['nzbindex'] = {}
        defaultConfig['nzbindex']['enabled']              = '0'
        defaultConfig['newznab'] = {}
        defaultConfig['newznab']['enabled']               = '0'
        defaultConfig['thepiratebay'] = {}
        defaultConfig['thepiratebay']['enabled']          = '1'
        defaultConfig['yify'] = {}
        defaultConfig['yify']['enabled']                  = '1'
        defaultConfig['mysterbin'] = {}
        defaultConfig['mysterbin']['enabled']             = '0'
        defaultConfig['core']['permission_folder']        = '0644'
        defaultConfig['core']['permission_file']          = '0644'
        defaultConfig['searcher'] = {}
        defaultConfig['searcher']['preferred_method']     = 'torrent'
        defaultConfig['searcher']['required_words']       = '720p, 1080p'
        defaultConfig['searcher']['preferred_words']      = 'YIFY, x264, BrRip'

    couchPotatoServerConfig.merge(defaultConfig)
    couchPotatoServerConfig.write()

    # launch CouchPotatoServer
    # ------------------
    if "true" in couchpotato_launch:
        subprocess.call(couchPotatoServer, close_fds=True)
except Exception, e:
    logging.exception(e)
    print 'CouchPotatoServer: exception occurred:', e
    print traceback.format_exc()
# CouchPotatoServer end

# Headphones start
try:
    # write Headphones settings
    # -------------------------
    headphonesConfig = ConfigObj(pHeadphonesSettings,create_empty=True)
    defaultConfig = ConfigObj()
    defaultConfig['General'] = {}
    defaultConfig['General']['launch_browser']            = '0'
    defaultConfig['General']['http_port']                 = '8084'
    defaultConfig['General']['http_host']                 = host
    defaultConfig['General']['http_username']             = user
    defaultConfig['General']['http_password']             = pwd
    defaultConfig['General']['check_github']              = '0'
    defaultConfig['General']['check_github_on_startup']   = '0'
    defaultConfig['General']['destination_dir']           = headphones_watch_dir
    defaultConfig['General']['cache_dir']                 = pAddonHome + '/hpcache'
    defaultConfig['General']['log_dir']                   = pAddonHome + '/logs'
    defaultConfig['General']['api_enabled']               = '1'
    defaultConfig['General']['api_key']                   = 'baf90d3054d3707e2c083d33137ba6eb'
    defaultConfig['General']['move_files']                = '1'
    defaultConfig['General']['piratebay']                 = '1'
    defaultConfig['General']['kat']                       = '1'
    defaultConfig['XBMC'] = {}
    defaultConfig['XBMC']['xbmc_enabled']                 = '1'
    defaultConfig['XBMC']['xbmc_host']                    = '127.0.0.1:' + xbmcPort
    defaultConfig['XBMC']['xbmc_username']                = xbmcUser
    defaultConfig['XBMC']['xbmc_password']                = xbmcPwd

    if 'true' in simplemode:
        defaultConfig['XBMC']['xbmc_update']                  = '1'
        defaultConfig['XBMC']['xbmc_notify']                  = '1'
        defaultConfig['General']['download_torrent_dir']      = pInternetPVRCompleteMus
        defaultConfig['General']['move_files']                = '1'
        defaultConfig['General']['rename_files']              = '1'
        defaultConfig['General']['correct_metadata']          = '1'
        defaultConfig['General']['cleanup_files']             = '1'
        defaultConfig['General']['folder_permissions']        = '0644'
        defaultConfig['General']['torrent_downloader']        = '1'
        defaultConfig['Transmission'] = {}
        defaultConfig['Transmission']['transmission_host']    = 'http://localhost:9091'

    if 'true' in transauth:
        defaultConfig['Transmission'] = {}
        defaultConfig['Transmission']['transmission_host']    = 'http://localhost:9091'
        defaultConfig['Transmission']['transmission_username']= transuser
        defaultConfig['Transmission']['transmission_password']= transpwd

    if hpfirstLaunch:
        defaultConfig['XBMC']['xbmc_update']                  = '1'
        defaultConfig['XBMC']['xbmc_notify']                  = '1'
        defaultConfig['General']['download_torrent_dir']      = pInternetPVRCompleteMus
        defaultConfig['General']['move_files']                = '1'
        defaultConfig['General']['rename_files']              = '1'
        defaultConfig['General']['correct_metadata']          = '1'
        defaultConfig['General']['cleanup_files']             = '1'
        defaultConfig['General']['folder_permissions']        = '0644'
        defaultConfig['General']['torrent_downloader']        = '1'
        defaultConfig['Transmission'] = {}
        defaultConfig['Transmission']['transmission_host']    = 'http://localhost:9091'

    headphonesConfig.merge(defaultConfig)
    headphonesConfig.write()

    # launch Headphones
    # -----------------
    if "true" in headphones_launch:
        subprocess.call(headphones,close_fds=True)
except Exception,e:
    logging.exception(e)
    print 'Headphones: exception occurred:', e
    print traceback.format_exc()
# Headphones end
