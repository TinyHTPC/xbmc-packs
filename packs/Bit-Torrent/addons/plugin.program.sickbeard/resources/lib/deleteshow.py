import xbmc
import xbmcgui
import sickbeard

tvdbid = sys.argv[1]
show_name = sys.argv[2]

# Initialize Sickbeard Class
Sickbeard = sickbeard.SB()

def confirmDialog(show_name):
    dialog = xbmcgui.Dialog()
    ret = dialog.yesno('Sickbeard XBMC', 'Are you sure you want to delete '+show_name+"?")
    return ret

def deleteShow(tvdbid):
    ret = Sickbeard.DeleteShow(tvdbid)
    dialog = xbmcgui.Dialog()
    dialog.ok('Sickbeard XBMC', ret)
    xbmc.executescript('special://home/addons/plugin.program.sickbeard/resources/lib/refresh.py')
    return ret

if confirmDialog(show_name) == 1:
    deleteShow(tvdbid)