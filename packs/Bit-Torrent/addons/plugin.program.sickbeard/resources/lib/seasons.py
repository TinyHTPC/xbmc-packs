import xbmcplugin
import xbmcgui
import urllib
import sys
import sickbeard

# Initialize Sickbeard Class
Sickbeard = sickbeard.SB()

# Get season number list
def GetSeasons(tvdbid):
    season_list = Sickbeard.GetSeasonNumberList(tvdbid)
    
    for season_number in season_list:
      if season_number == 0:
        season_list[season_list.index(season_number)] = [0, "Extras"]
      else:
        season_list[season_list.index(season_number)] = [season_number, "Season "+str(season_number)]
    return season_list

# Add directory items for each season number
def menu(tvdbid):
      season_list = GetSeasons(tvdbid)
      season_total = len(season_list)
      context_items = [('Refresh Season List', 'XBMC.RunScript(special://home/addons/plugin.program.sickbeard/resources/lib/refresh.py)')]
      for season_number, season_text in season_list:
        addSeasonDirectory(season_number, season_text, tvdbid, 5, "", season_total, context_items)
      
# Add season directory items
def addSeasonDirectory(season_number, season_text, tvdbid, menu_number, thumbnail_path, season_total, context_items):
    return_url = sys.argv[0]+"?url="+urllib.quote_plus(tvdbid)+"&mode="+str(menu_number)+"&name="+urllib.quote_plus(str(season_number))
    list_item = xbmcgui.ListItem(season_text, thumbnailImage=thumbnail_path)
    list_item.addContextMenuItems(context_items)
    xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=return_url, listitem=list_item, isFolder=True, totalItems=season_total)
