#
import os
import xbmc
import xbmcaddon
import time
import subprocess

__scriptname__ = "InternetPVR"
__author__     = "TinyHTPC.co.nz"
__url__        = "http://TinyHTPC.co.nz"
__settings__   = xbmcaddon.Addon(id='service.downloadmanager.InternetPVR')
__cwd__        = __settings__.getAddonInfo('path')
__start__      = xbmc.translatePath(os.path.join(__cwd__, 'bin', "InternetPVR.py") )
__stop__       = xbmc.translatePath(os.path.join(__cwd__, 'bin', "InternetPVR.stop") )

subprocess.call(['python', __start__])

while not xbmc.abortRequested:
    time.sleep(0.250)

subprocess.Popen(__stop__, shell=True, close_fds=True)
