#
import xbmcaddon

__scriptname__ = "InternetPVR"
__author__     = "TinyHTPC.co.nz"
__url__        = "http://TinyHTPC.co.nz"
__addon__   = xbmcaddon.Addon(id='service.downloadmanager.InternetPVR')

#Open settings dialog
if __name__ == '__main__':
    __addon__.openSettings()
