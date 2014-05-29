import xbmcplugin
import xbmcgui
import sys
import sickbeard

# Initialize Sickbeard Class
Sickbeard = sickbeard.SB()

# Translates the int returned from Sickbeard to a weekday string
def GetWeekDay(weekday):
    if weekday == 1:
        day = "Monday"
    elif weekday == 2:
        day = "Tuesday"
    elif weekday == 3:
        day = "Wednesday"
    elif weekday == 4:
        day = "Thursday"
    elif weekday == 5:
        day = "Friday"
    elif weekday == 6:
        day = "Saturday"
    elif weekday == 7:
        day = "Sunday"
    else:
        day = "None"
    return day

# Get upcoming episodes
def GetUpcomingEpisodes():
    coming_soon = Sickbeard.GetFutureShows()
    upcoming_episodes_list = []
    
    # Get todays coming eps
    if len(coming_soon["today"]) != 0:
      day = "Today"
      for show in coming_soon['today']:
          upcoming_episodes_list.append([str(show['tvdbid']), day+": "+show['show_name']+" - "+str(show['season'])+"x"+str(show['episode'])+" "+show['ep_name']])
          
    # Get coming soon eps      
    if len(coming_soon["soon"]) != 0:    
      show_list={}
      for show in coming_soon['soon']:
          if show['airdate'] not in show_list:
              show_list[show['airdate']] = []
              show_list[show['airdate']].append(show)
          else:
              show_list[show['airdate']].append(show)

      for k in sorted(show_list.iterkeys()):
          day = GetWeekDay(show_list[k][0]['weekday'])
          for show in show_list[k]: 
              upcoming_episodes_list.append([str(show['tvdbid']), day+": "+show['show_name']+" - "+str(show['season'])+"x"+str(show['episode'])+" "+show['ep_name']])

    return upcoming_episodes_list

# Add directory items for each upcoming episode
def menu():
      upcoming_episodes_list = GetUpcomingEpisodes()
      upcoming_total = len(upcoming_episodes_list)
      context_items = [('Refresh Shows', 'xbmc.executebuiltin("Container.Refresh")',)]
      for tvdbid, ep_name in upcoming_episodes_list:
        thumbnail_path = Sickbeard.GetShowPoster(tvdbid)
        addUpcomingDirectory(ep_name, thumbnail_path, upcoming_total, context_items)

# Add upcoming episode to the directory
def addUpcomingDirectory(ep_name, thumbnail_path, upcoming_total, context_items):
    list_item = xbmcgui.ListItem(ep_name, thumbnailImage=thumbnail_path)
    list_item.addContextMenuItems(context_items)
    xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url="", listitem=list_item, isFolder=False, totalItems=upcoming_total)
