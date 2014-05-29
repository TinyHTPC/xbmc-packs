import xbmcplugin
import xbmcgui
import sys
import sickbeard

# Initialize Sickbeard Class
Sickbeard = sickbeard.SB()

# Get a list of episodes grabbed by Sickbeard
def GetHistoryItems():
  show_ids = Sickbeard.GetShowIds()
  show_info = Sickbeard.GetShowInfo(show_ids)

  show_names = {}
  for show_name, tvdbid in sorted(show_info.iteritems()):
    show_names[show_name] = str(tvdbid)
    
  history = Sickbeard.GetHistory()
  history_list = []
  for show in history:
    tvdbid = show_names[show['show_name']]
    history_list.append([str(tvdbid), show['show_name']+" "+str(show['season'])+"x"+str(show['episode'])+" "+show['date']+"    "+show['status']])
  
  return history_list

# Add directory items for each episode recently grabbed
def menu():
      history_list = GetHistoryItems()
      history_total = len(history_list)
      context_items = [('Refresh History', 'xbmc.executebuiltin("Container.Refresh")',)]
      for tvdbid, history_name in history_list:
        thumbnail_path = Sickbeard.GetShowPoster(tvdbid)
        addHistoryDirectory(history_name, thumbnail_path, history_total, context_items)

# Add history items to directory
def addHistoryDirectory(history_name, thumbnail_path, history_total, context_items):
    list_item = xbmcgui.ListItem(history_name, thumbnailImage=thumbnail_path)
    list_item.addContextMenuItems(context_items)
    xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url="", listitem=list_item, isFolder=True, totalItems=history_total)
