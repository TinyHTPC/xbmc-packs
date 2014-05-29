import sickbeard
import sys
import urllib
import xbmcplugin
import xbmcgui
import xbmc

Sickbeard = sickbeard.SB()

# Get the tvdbid and show names 
def GetShowInfo():
    show_ids = Sickbeard.GetShowIds()
    show_info = Sickbeard.GetShowInfo(show_ids)

    show_names = []
    for name, info in sorted(show_info.iteritems()):
      tvdbid, paused = info
      if paused == 0:
          paused = "Pause"
      else:
          paused = "Unpause"
      show_names.append([name, str(tvdbid), Sickbeard.GetShowPoster(tvdbid), paused])
      
    return show_names

# Parse through shows and add dirs for each
def menu():
      show_info = GetShowInfo()
      show_total = len(show_info)
      for show_name, tvdbid, thumbnail_path, paused in show_info:
        context_menu_items = [('Add New Show', 'XBMC.RunScript(special://home/addons/plugin.program.sickbeard/resources/lib/addshow.py)'),\
                              ('Delete Show', 'XBMC.RunScript(special://home/addons/plugin.program.sickbeard/resources/lib/deleteshow.py, '+tvdbid+', '+show_name+')'),\
                              ('Force Search', 'XBMC.RunScript(special://home/addons/plugin.program.sickbeard/resources/lib/forcesearch.py)'),\
                              (paused+' Show', 'XBMC.RunScript(special://home/addons/plugin.program.sickbeard/resources/lib/setpausestate.py, '+paused+', '+tvdbid+')'),\
                              ('Refresh Show List', 'XBMC.RunScript(special://home/addons/plugin.program.sickbeard/resources/lib/refresh.py)')]
        addShowDirectory(show_name, tvdbid, 4, thumbnail_path, show_total, context_menu_items)

# Add directory item
def addShowDirectory(show_name, tvdbid, menu_number, thumbnail_path, show_total, context_menu_items):
    return_url = sys.argv[0]+"?url="+urllib.quote_plus(str(tvdbid))+"&mode="+str(menu_number)+"&name="+urllib.quote_plus(show_name.encode( "utf-8" ))
    list_item = xbmcgui.ListItem(show_name, thumbnailImage=thumbnail_path)
    list_item.addContextMenuItems(context_menu_items)
    xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=return_url, listitem=list_item, isFolder=True, totalItems=show_total)  
