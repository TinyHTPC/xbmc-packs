import xbmcgui
import xbmc
from resources.lib.service import service
from xbmcaddon import Addon
from resources.lib.utils import *
import os
import shutil
import resources.lib.extract as extract
import subprocess
import sys
import time

__addonID__ = "os.linux.tiny"
ADDON     = Addon( __addonID__ )
ADDON_DATA  = xbmc.translatePath( "special://profile/addon_data/%s/" % __addonID__ )
ADDON_DIR = ADDON.getAddonInfo( "path" )
LangXBMC  = xbmc.getLocalizedString
ROOTDIR            = ADDON_DIR
FILES = xbmc.translatePath( ADDON_DIR + "/resources/files/" )
DEST = xbmc.translatePath( "special://home/" )
src=None

def ensure_dir(f):
    print "Checking for location: "+f
    d = os.path.dirname(f)
    if not os.path.exists(d):
        os.makedirs(d)
	print "Not Found! Creating: "+d

def SETUP():
        dialog = xbmcgui.Dialog()      
        dp = xbmcgui.DialogProgress()
        promptsetup = dialog.yesno("InternetPVR Setup Wizzard", "This First Run Wizard will walk you through the setup process.", "Please ensure you have your USB device connected.", "Would you like to continue?")
        
        dialog.ok("InternetPVR Setup Wizzard", "","", "[COLOR red]Brought To You By TinyHTPC[/COLOR]")
        if promptsetup:
		media="n"
		while (media == "") or (media == "n"):
			#Open External Device
			location = dialog.browse(3, 'XBMC', 'files', '', False, False, '/media/')
			print "Location: "+location
			device = location.replace('/media','')
			print "Device: "+device
			cmd = "df | grep -w "+device[1:-1]+" | awk {'print $1'}"
			print "cmd: "+cmd
			media = subprocess.check_output(cmd, shell=True).rstrip('\n')
			print "MEDIA : " + media
			if (media == "") or (media == "n"):
				dialog.ok("ERROR", "Could not find valid USB device. Please try again", "", "[B]HINT:[/B] The path you select needs to be the root of the USB device.")
				return
		else:
			#Select HDD Format or Keep data
			wipe = dialog.select("External Device Setup",['[B]Keep my data.[/B] - (Current files will be saved.)', '[B]Format my USB.[/B] - (Fresh install, all data will be lost.)', '[B]Cancel.[/B]'])
			if wipe == 0:
			    dp = xbmcgui.DialogProgress()
			    
			    #Begin Operation
			    dp.create("External USB Device Setup", "Installing... ", '', 'Please Wait')
			    dp.update(0)
			    dp.update(0,"", "Checking USB...  Please Wait")
			    time.sleep(3)
			    dp.update(10,"", "Copying Files to USB...  Please Wait")
			    print device
			    ensure_dir("/media"+device+"Downloads/complete/*")
			    dp.update(20)
			    ensure_dir("/media"+device+"Downloads/incoming/*")
			    dp.update(20)
			    ensure_dir("/media"+device+"Downloads/scripts/*")
			    dp.update(20)
			    ensure_dir("/media"+device+"Downloads/torrents/*")
			    dp.update(30)
			    ensure_dir("/media"+device+"TVShows/*")
			    dp.update(40)
			    ensure_dir("/media"+device+"Movies/*")
			    dp.update(50)
			    ensure_dir("/media"+device+"Music/*")
			    dp.update(60)
			    ensure_dir("/media"+device+"XBMCBackups/*")
			    dp.update(60)
			    
			    #dp.update(70,"", "Setting up Library Links to USB...  Please Wait")
			    #time.sleep(3)
			    
			    dp.update(100,"", "Copying Files to USB...  Please Wait")
			    dialog.ok("External USB Device Setup", "All Done","", "[COLOR green]Brought To You By TinyHTPC[/COLOR]")
			elif wipe == 1:
			    prompt = dialog.yesno("WARNING!!!", "Clicking [B]'Yes'[/B] will erase all data on your device.", "Would you like to continue?")
			    if (prompt):
			        dp = xbmcgui.DialogProgress()

			        #Set shell commands
			        timestr = time.strftime("%Y%m%d-%H%M%S")
			        label = "XBMCMEDIA_"+timestr
			        print "lable: "+label
			        unmount = "umount "+media
			        print "unmount: "+unmount
			        mkfs = "mkfs.ntfs -f "+media+" -L "+label
			        print "mkfs: "+mkfs
			        nwmountpoint = "/media/"+label
			        print "nwmountpoint: "+nwmountpoint
			        mkmountdir = "mkdir /media/"+label
			        print "mkmountdir: "+mkmountdir
			        mount = "mount -t ntfs "+media+" /media/"+label
			        print "mount: "+mount
			        rmmountdir = "rmdir /media/"+label
			        print "rmmountdir: "+rmmountdir
			        
			        #Begin Operation
			        dp.create("External USB Device Setup", "Installing... ", '', 'Please Wait')
			        time.sleep(1)
			        
			        dp.update(0,"", "Unmounting USB...  Please Wait")
			        if os.path.exists(location):
			            subprocess.check_output(unmount, shell=True)
			        time.sleep(1)
			        
			        dp.update(0,"", "Formatting...  Please Wait")
			        subprocess.check_output(mkfs, shell=True)
			        if not os.path.exists(nwmountpoint):
			        	subprocess.check_output(mkmountdir, shell=True)
			        subprocess.check_output(mount, shell=True)
			        time.sleep(1)
			        
			        dp.update(0,"", "Checking USB...  Please Wait")
			        time.sleep(3)
			        dp.update(10,"", "Copying Files to USB...  Please Wait")
			        print device
			        ensure_dir(nwmountpoint+"/Downloads/complete/*")
			        dp.update(20)
			        ensure_dir(nwmountpoint+"/Downloads/incomming/*")
			        dp.update(20)
			        ensure_dir(nwmountpoint+"/Downloads/scripts/*")
			        dp.update(30)
			        ensure_dir(nwmountpoint+"/TVShows/*")
			        dp.update(40)
			        ensure_dir(nwmountpoint+"/Movies/*")
			        dp.update(50)
			        ensure_dir(nwmountpoint+"/Music/*")
			        dp.update(60)
			        ensure_dir(nwmountpoint+"/XBMCBackups/*")
			        dp.update(70)
			        
			        #dp.update(70,"", "Setting up Library Links to USB...  Please Wait")
			        #time.sleep(3)
			        
			        dp.update(90,"", "Cleaning Up...  Please Wait")
			        subprocess.check_output(unmount, shell=True)
			        subprocess.check_output(rmmountdir, shell=True)
			        time.sleep(3)
			        dp.update(100,"", "")
			        dialog.ok("External USB Device Setup", "All Done","", "[COLOR red]Brought To You By TinyHTPC[/COLOR]")
			    else:
			        return
			elif wipe == 2:
			    return
			else:
			    return

			#elif (wipe == "no"):
			#	return
			#elif (wipe == "back"):
			#	return
			#else:
			#	dialog.ok("ERROR", "All Done","", "[COLOR red]Brought To You By TinyHTPC[/COLOR]")
			#	return
	else:
		return
        
        #dp.create("InternetPVR Setup Wizzard","Installing ",'', 'Please Wait')
        
        keyword      =  'firstrun'
        src = FILES+keyword+'.zip'
        
        path         =  xbmc.translatePath(os.path.join('special://home/addons','packages'))
        lib          =  os.path.join(path, keyword+'.zip')
        addonfolder  =  xbmc.translatePath(os.path.join('special://home',''))
        
	shutil.copy2(src, path)
        
        dp.update(0,"", "Extracting Zip... Please Wait")
        extract.all(lib,addonfolder,dp)
        
        #Setup Home dir 
        dp.update(70,"", "Setting up folders... Please Wait")
        ensure_dir("/root/Downloads/complete/*")
        ensure_dir("/root/Downloads/incoming/*")
        ensure_dir("/root/Downloads/scripts/*")
        ensure_dir("/root/Downloads/torrents/*")
        ensure_dir("/root/XBMCBackups/*")
        
        #Link to External Media 
        ln = "ln -s /media/ /root/ExternalDevices"
        subprocess.check_output(ln, shell=True)
        
	#Restart XBMC
        dp.update(100,"", "Reloading XBMC")
	time.sleep(3)
	xbmc.executebuiltin('RestartApp')


class firstrun(service):
    def onStart(self):
        #Apply firstrun        
        firstlock100 = os.path.join(ADDON_DATA,'.firstrun')
        if not os.path.isfile(firstlock100) :
        	        if not os.path.exists(ADDON_DATA):
                            os.mkdir(ADDON_DATA)

			if src==None or len(src)<1:
				SETUP()
			
			open(firstlock100,'w').close()			
