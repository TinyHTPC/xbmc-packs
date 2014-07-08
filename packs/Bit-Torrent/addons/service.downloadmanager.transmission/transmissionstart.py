# Initializes and launches Transmission if directories are found

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
        time.sleep(3)
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

__settings__   = xbmcaddon.Addon(id='service.downloadmanager.transmission')
__cwd__        = __settings__.getAddonInfo('path')
__start__      = xbmc.translatePath( os.path.join( __cwd__, 'bin', "transmission.start") )
__stop__       = xbmc.translatePath( os.path.join( __cwd__, 'bin', "transmission.stop") )
__addonname__  = __settings__.getAddonInfo('name')
__icon__       = __settings__.getAddonInfo('icon')

pAddon                        = os.path.expanduser("~/.xbmc/addons/service.downloadmanager.transmission")
pAddonHome                    = os.path.expanduser("~/.xbmc/userdata/addon_data/service.downloadmanager.transmission")
pTransmission_Addon_Settings  = os.path.join(pAddonHome, "settings.xml")
pDefaultSuiteSettings         = os.path.join(pAddon, "settings-default.xml")

# create the settings file if missing
if not os.path.exists(pTransmission_Addon_Settings):
   if not os.path.isdir(pAddonHome):
      os.makedirs(pAddonHome)
      os.makedirs(pAddonHome+'/torrents')
   shutil.copy(pDefaultSuiteSettings, pTransmission_Addon_Settings)

#Get host IP:
connected_ifaces = check_connection()
if len(connected_ifaces) == 0:
    print 'not connected to any network'
    hostIP = "Port"
else:
    hostIP = ([(s.connect(('8.8.8.8', 80)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1])
    print hostIP

#Create Strings for notifications:
started   = 'Service started on '+hostIP+':9091'
waiting   = 'Looking for download folders...'
disabled  = 'Service disabled for this session'

#Get Transmission-Daemon settings:
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

dlLOC = transinc.replace('/incoming','')
dialog = xbmcgui.Dialog()
#Start Transmission only if download location exists:
while (dlLOC != ""):
	print "Location: "+dlLOC
	if not os.path.exists(dlLOC):
		promptstart = dialog.yesno(__addonname__, "Transmission could not find your download location.", "Check that your location settings are correct.", "[B]Would you like to disable Transmission for this session?[/B]")
		if promptstart:
			dialog.ok("Transmission", "Transmission has been disabled for this session", "", "[B]To use Transmission, restart XBMC[/B]")
			subprocess.Popen("chmod -R +x " + __cwd__ + "/bin/*" , shell=True, close_fds=True)
			subprocess.Popen(__stop__, shell=True, close_fds=True)
			xbmc.executebuiltin('XBMC.Notification('+ __addonname__ +','+ disabled +',5000,'+ __icon__ +')')
			break
		else:
			subprocess.Popen("chmod -R +x " + __cwd__ + "/bin/*" , shell=True, close_fds=True)
			subprocess.Popen(__stop__, shell=True, close_fds=True)
			xbmc.executebuiltin('XBMC.Notification('+ __addonname__ +','+ waiting +',5000,'+ __icon__ +')')
		time.sleep(20)
	else:
		subprocess.Popen("chmod -R +x " + __cwd__ + "/bin/*" , shell=True, close_fds=True)
		subprocess.Popen(__start__, shell=True, close_fds=True)
		xbmc.executebuiltin('XBMC.Notification('+ __addonname__ +','+ started +',5000,'+ __icon__ +')')
		break
