#
import xbmc
import xbmcaddon
import time
import subprocess

__scriptname__ = "InternetPVR"
__author__     = "TinyHTPC.co.nz"
__url__        = "http://TinyHTPC.co.nz"
__addon__      = xbmcaddon.Addon(id='service.downloadmanager.InternetPVR')
__addonpath__  = __addon__.getAddonInfo('path')
__start__      = xbmc.translatePath(__addonpath__ + '/resources/InternetPVR.py')
__stop__       = xbmc.translatePath(__addonpath__ + '/resources/InternetPVR.stop.py')
__kill__       = xbmc.translatePath(__addonpath__ + '/resources/InternetPVR.kill.py')

xbmc.executebuiltin('XBMC.RunScript(%s)' % __start__, True)

while not xbmc.abortRequested:
    time.sleep(0.250)

#xbmc.executebuiltin('XBMC.RunScript(%s)' % __stop__, True)
#subprocess.Popen(__kill__, shell=True, close_fds=True)
xbmc.executebuiltin('XBMC.RunScript(%s)' % __kill__, True)
