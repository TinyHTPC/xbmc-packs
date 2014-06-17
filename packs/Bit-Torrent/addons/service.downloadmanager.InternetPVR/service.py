#
import os
import shutil
import time
import subprocess
import xbmcaddon
import xbmcgui
import xbmc
import socket
import fcntl
import struct
from xml.dom.minidom import parseString

def getAddonSetting(doc,id):
    for element in doc.getElementsByTagName('setting'):
        if element.getAttribute('id')==id:
            return element.getAttribute('value')

def check_connection():
        time.sleep(2)
        ifaces = ['eth0','eth1','wlan0','wlan1','wlan2','wlan3']
        connected = []
        i = 0
        for ifname in ifaces:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            try:
                socket.inet_ntoa(fcntl.ioctl(
                        s.fileno(),
                        0x8915,  # SIOCGIFADDR
                        struct.pack('256s', ifname[:15])
                )[20:24])
                connected.append(ifname)
                print "%s is connected" % ifname
            except:
                print "%s is not connected" % ifname
            i += 1
        return connected

__scriptname__ = "InternetPVR"
__author__     = "TinyHTPC.co.nz"
__url__        = "http://TinyHTPC.co.nz"
__settings__   = xbmcaddon.Addon(id='service.downloadmanager.InternetPVR')
__cwd__        = __settings__.getAddonInfo('path')
__start__      = xbmc.translatePath(os.path.join(__cwd__, 'bin', "InternetPVR.py") )
__stop__       = xbmc.translatePath(os.path.join(__cwd__, 'bin', "InternetPVR.stop") )
__addonname__  = __settings__.getAddonInfo('name')
__icon__       = __settings__.getAddonInfo('icon')
###
pAddonHome                    = os.path.expanduser("~/.xbmc/userdata/addon_data/service.downloadmanager.InternetPVR")
pSuiteSettings                = os.path.join(pAddonHome, "settings.xml")
pDefaultSuiteSettings         = os.path.expanduser("~/.xbmc/addons/service.downloadmanager.InternetPVR/settings-default.xml")

# create the settings file if missing
if not os.path.exists(pSuiteSettings):
   if not os.path.isdir(pAddonHome):
      os.makedirs(pAddonHome)
   shutil.copy(pDefaultSuiteSettings, pSuiteSettings)

#Get host IP:
connected_ifaces = check_connection()
if len(connected_ifaces) == 0:
    print 'not connected to any network'
    hostIP = "..."
else:
    GetIP = ([(s.connect(('8.8.8.8', 80)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1])
    hostIP = ' on '+GetIP
    print hostIP

#Create Strings for notifications:
started   = 'Service started'+hostIP
waiting   = 'Looking for Media download folders...'
disabled  = 'Service disabled for this session'

#Get InternetPVR Suite settings:
if os.path.exists(pSuiteSettings):
    fTransmission_Addon_Settings = open(pSuiteSettings, 'r')
    data = fTransmission_Addon_Settings.read()
    fTransmission_Addon_Settings.close
    transmission_addon_settings = parseString(data)
    ipvrmov                     = getAddonSetting(transmission_addon_settings, 'MOVIES_DIR')
    ipvrmus                     = getAddonSetting(transmission_addon_settings, 'MUSIC_DIR')
    ipvrtv                      = getAddonSetting(transmission_addon_settings, 'TVSHOW_DIR')
    ipvrtransdl                 = getAddonSetting(transmission_addon_settings, 'TRANSMISSION_DL_DIR')
else:
    ipvrdirs                    = 'false'
    createDir(pAddonHome)
    shutil.copy(pDefaultSuiteSettings, pSuiteSettings)
    fTransmission_Addon_Settings = open(pSuiteSettings, 'r')
    data = fTransmission_Addon_Settings.read()
    fTransmission_Addon_Settings.close
    transmission_addon_settings = parseString(data)
    ipvrmov                     = getAddonSetting(transmission_addon_settings, 'MOVIES_DIR')
    ipvrmus                     = getAddonSetting(transmission_addon_settings, 'MUSIC_DIR')
    ipvrtv                      = getAddonSetting(transmission_addon_settings, 'TVSHOW_DIR')
    ipvrtransdl                 = getAddonSetting(transmission_addon_settings, 'TRANSMISSION_DL_DIR')
    
    #
    #from services.firstrun import firstrun
    #firstrun_thread = firstrun()     
    #firstrun_thread.onStart()
    #

movDIR = not os.path.exists(ipvrmov)
musDIR = not os.path.exists(ipvrmus)
tvDIR  = not os.path.exists(ipvrtv)
dlDIR  = not os.path.exists(ipvrtransdl)
print dlDIR
#xbmc.executebuiltin('XBMC.Notification('+ __addonname__ +','+ movDIR + musDIR + tvDIR + dlDIR +',5000,'+ __icon__ +')')
#Start Internet PVR Suite only if folder locations exists:
dialog = xbmcgui.Dialog()
while (movDIR != "") or (musDIR != "") or (tvDIR != "") or (dlDIR != ""):
	movDIR = not os.path.exists(ipvrmov)
	musDIR = not os.path.exists(ipvrmus)
	tvDIR  = not os.path.exists(ipvrtv)
	dlDIR  = not os.path.exists(ipvrtransdl)
	if movDIR or musDIR or tvDIR or dlDIR:
		promptstart = dialog.yesno(__addonname__, "Could not find your directories.", "Check that your location settings are correct.", "[B]Would you like to disable "+__addonname__+" for this session?[/B]")
		if promptstart:
			#dialog.ok(__addonname__, __addonname__+" has been disabled for this session", "", "[B]To use "+__addonname__+", restart XBMC[/B]")
			subprocess.Popen("chmod -R +x " + __cwd__ + "/bin/*" , shell=True, close_fds=True)
			subprocess.Popen(__stop__, shell=True, close_fds=True)
			#xbmc.executebuiltin('XBMC.Notification('+ __addonname__ +','+ disabled +',5000,'+ __icon__ +')')
			break
		else:
			subprocess.Popen("chmod -R +x " + __cwd__ + "/bin/*" , shell=True, close_fds=True)
			subprocess.Popen(__stop__, shell=True, close_fds=True)
			xbmc.executebuiltin('XBMC.Notification('+ __addonname__ +','+ waiting +',5000,'+ __icon__ +')')
		time.sleep(20)
	else:
		subprocess.Popen("chmod -R +x " + __cwd__ + "/bin/*" , shell=True, close_fds=True)
		subprocess.call(['python', __start__])
		xbmc.executebuiltin('XBMC.Notification('+ __addonname__ +','+ started +',5000,'+ __icon__ +')')
		break


#Start force Shutdown of InternetPVR Suite if External Device is removed:
while not xbmc.abortRequested:
    movDIR = not os.path.exists(ipvrmov)
    musDIR = not os.path.exists(ipvrmus)
    tvDIR  = not os.path.exists(ipvrtv)
    dlDIR  = not os.path.exists(ipvrtransdl)
    if movDIR or musDIR or tvDIR or dlDIR:
        subprocess.Popen("chmod -R +x " + __cwd__ + "/bin/*" , shell=True, close_fds=True)
        subprocess.Popen(__stop__, shell=True, close_fds=True)
        dialog.ok(__addonname__, "Device Removal Detected!", __addonname__+" has been disabled for this session.", "[B]To use "+__addonname__+" again, restart XBMC[/B]")
        xbmc.executebuiltin('XBMC.Notification('+ __addonname__ +','+ disabled +',5000,'+ __icon__ +')')
        break
    else:
        time.sleep(0.250)

subprocess.Popen("chmod -R +x " + __cwd__ + "/bin/*" , shell=True, close_fds=True)
subprocess.Popen(__stop__, shell=True, close_fds=True)
