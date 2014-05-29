import xbmcplugin
import xbmcgui
import sys
import sickbeard

# Initialize Sickbeard Class
Sickbeard = sickbeard.SB()

# Get episodes for the selected show and season
def GetSeasonEpisodes(tvdbid, season_number):
    season_episode_list = []
    season_episodes = Sickbeard.GetSeasonEpisodeList(tvdbid, season_number)
    temp = season_episodes.keys()
    temp = sorted(temp)
    for each in temp:
      season_episode_list.append([each, season_episodes[each]['name'], season_episodes[each]['status'], tvdbid, season_number])

    return season_episode_list

# Add directory items for each episode
def menu(tvdbid, season_number):
      episode_list = GetSeasonEpisodes(tvdbid, season_number)
      episode_total = len(episode_list)
      for ep_number, ep_name, ep_status, ep_tvdbid, ep_season in episode_list:
        addEpisodeDirectory(ep_number, ep_name, ep_status, ep_tvdbid, ep_season, "", episode_total)

# Add episode directory items
def addEpisodeDirectory(ep_number, ep_name, ep_status, ep_tvdbid, ep_season, thumb, episode_total):
    season_numbers = []
    episode_status_args = ", "+ep_tvdbid+", "+ep_season+", "+ep_number
    
    for number in range(0, episode_total):
      season_numbers.append(str(number+1))
    season_status_args = ", "+ep_tvdbid+", "+ep_season+", "+"|".join(season_numbers)

    list_item = xbmcgui.ListItem(str(ep_number)+". "+ep_status+": "+ep_name, thumbnailImage=thumb)
    menu_items = [('Set Episode Status', 'XBMC.RunScript(special://home/addons/plugin.program.sickbeard/resources/lib/setstatus.py'+episode_status_args+')'),\
                  ('Set Season Status', 'XBMC.RunScript(special://home/addons/plugin.program.sickbeard/resources/lib/setstatus.py'+season_status_args+')'),\
                  ('Episode Manual Search', 'XBMC.RunScript(special://home/addons/plugin.program.sickbeard/resources/lib/manualsearch.py'+episode_status_args+')'),\
                  ('Refresh Episode List', 'XBMC.RunScript(special://home/addons/plugin.program.sickbeard/resources/lib/refresh.py)')]
    list_item.addContextMenuItems(menu_items)
    xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url='', listitem=list_item, isFolder=False, totalItems=episode_total)
