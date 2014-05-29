import urllib
import socket
import json
import settings

timeout = 45
socket.setdefaulttimeout(timeout)

# Sickbeard class which mas all API calls to Sickbeard
class SB:
  # Get the show ID numbers
  def GetShowIds(self):
      show_ids=[]
      result=json.load(urllib.urlopen(settings.__url__+"?cmd=shows"))
      for each in result['data']:
          show_ids.append(each)
      return show_ids

  # Get show info dict, key:show_name value:tvdbid
  def GetShowInfo(self, show_ids):
      show_info={}
      for id in show_ids:
          result=json.load(urllib.urlopen(settings.__url__+'?cmd=show&tvdbid='+id))
          name=result['data']['show_name']
          paused=result['data']['paused']
          show_info[name] = [id, paused]
      return show_info
    
  # Returns the details of a show from Sickbeard 
  def GetShowDetails(self, show_id):
      result=json.load(urllib.urlopen(settings.__url__+'?cmd=show&tvdbid='+show_id))
      details=result['data']
      
      result=json.load(urllib.urlopen(settings.__url__+'?cmd=show.stats&tvdbid='+show_id))
      total=result['data']['total']
      
      return details, total
    
  # Return a list of season numbers
  def GetSeasonNumberList(self, show_id):
      result=json.load(urllib.urlopen(settings.__url__+'?cmd=show.seasonlist&tvdbid='+show_id))
      season_number_list = result['data']
      season_number_list.sort()
      return season_number_list

  # Get the list of episodes ina given season
  def GetSeasonEpisodeList(self, show_id, season):
      season = str(season)
      result=json.load(urllib.urlopen(settings.__url__+'?cmd=show.seasons&tvdbid='+show_id+'&season='+season))
      season_episodes = result['data']
          
      for key in season_episodes.iterkeys():
          if int(key) < 10:
              newkey = '{0}'.format(key.zfill(2))
              if newkey not in season_episodes:
                  season_episodes[newkey] = season_episodes[key]
                  del season_episodes[key]
      
      return season_episodes
    
  # Gets the show banner from Sickbeard  
  def GetShowBanner(self, show_id):
    result = 'http://'+settings.__ip__+':'+settings.__port__+'/showPoster/?show='+str(show_id)+'&which=banner'
    return result

  # Check if there is a cached thumbnail to use, if not use Sickbeard poster
  def GetShowPoster(self, show_id):
      return 'http://'+settings.__ip__+':'+settings.__port__+'/showPoster/?show='+str(show_id)+'&which=poster'

  # Get list of upcoming episodes
  def GetFutureShows(self):
      result=json.load(urllib.urlopen(settings.__url__+'?cmd=future&sort=date&type=today|soon'))
      future_list = result['data']
      return future_list

  # Return a list of the last 20 snatched/downloaded episodes    
  def GetHistory(self):
      result=json.load(urllib.urlopen(settings.__url__+'?cmd=history&limit=20'))
      history = result['data']
      return history
  
  # Search the tvdb for a show using the Sickbeard API  
  def SearchShowName(self, name):
    search_results = []
    result=json.load(urllib.urlopen(settings.__url__+'?cmd=sb.searchtvdb&name='+name+'&lang=en'))
    for each in result['data']['results']:
      search_results.append(each)
    return search_results
  
  # Return a list of the default settings for adding a new show
  def GetDefaults(self):
    defaults_result = json.load(urllib.urlopen(settings.__url__+'?cmd=sb.getdefaults'))
    print defaults_result.keys()
    defaults_data = defaults_result['data']
    defaults = [defaults_data['status'], defaults_data['flatten_folders'], str(defaults_data['initial'])]
    return defaults
  
  # Return a list of the save paths set in Sickbeard
  def GetRoodDirs(self):
    directory_result = json.load(urllib.urlopen(settings.__url__+'?cmd=sb.getrootdirs'))
    directory_result = directory_result['data']
    return directory_result

  # Get the version of Sickbeard
  def GetSickbeardVersion(self):
    result=json.load(urllib.urlopen(settings.__url__+'?cmd=sb'))
    version = result['data']['sb_version']
    return version
  
  # Set the status of an episode
  def SetShowStatus(self, tvdbid, season, ep, status):
    result=json.load(urllib.urlopen(settings.__url__+'?cmd=episode.setstatus&tvdbid='+str(tvdbid)+'&season='+str(season)+'&episode='+str(ep)+'&status='+status))
    return result
  
  # Add a new show to Sickbeard
  def AddNewShow(self, tvdbid, location, status, use_folders, quality):
    result=json.load(urllib.urlopen(settings.__url__+'?cmd=show.addnew&tvdbid='+str(tvdbid)+'&location'+location+'&status='+status+'&season_folder='+str(use_folders)+'&initial='+quality))
    return result['result']

  # Return a list of the last 20 snatched/downloaded episodes    
  def ForceSearch(self):
      result=json.load(urllib.urlopen(settings.__url__+'?cmd=sb.forcesearch'))
      success = result['result']
      settings.messageWindow("Force Search", "Force search returned "+success)

  def SetPausedState(self, paused, show_id):
      result=json.load(urllib.urlopen(settings.__url__+'?cmd=show.pause&tvdbid='+show_id+'&pause='+paused))
      message = result['message']
      return message
  
  def ManualSearch(self, tvdbid, season, ep):
      result=json.load(urllib.urlopen(settings.__url__+'?cmd=episode.search&tvdbid='+str(tvdbid)+'&season='+str(season)+'&episode='+str(ep)))
      message = result['message']
      return message    
  
  def DeleteShow(self, tvdbid):
      result=json.load(urllib.urlopen(settings.__url__+'?cmd=show.delete&tvdbid='+str(tvdbid)))
      message = result['message']
      return message   