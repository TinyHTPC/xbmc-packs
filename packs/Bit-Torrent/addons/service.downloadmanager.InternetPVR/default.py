#
import os
import xbmc
import xbmcaddon

__scriptname__ = "InternetPVR"
__author__     = "TinyHTPC.co.nz"
__url__        = "http://TinyHTPC.co.nz"
__settings__   = xbmcaddon.Addon(id='service.downloadmanager.InternetPVR')
__cwd__        = __settings__.getAddonInfo('path')
__start__      = xbmc.translatePath( os.path.join( __cwd__, 'bin', "InternetPVR.py") )
__stop__       = xbmc.translatePath( os.path.join( __cwd__, 'bin', "InternetPVR.stop") )

#Open settings dialog
if __name__ == '__main__':
    __settings__.openSettings()
