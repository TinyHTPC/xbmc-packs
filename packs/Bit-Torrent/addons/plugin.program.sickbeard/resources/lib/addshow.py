import xbmc
import xbmcgui
import sickbeard

# Initialize Sickbeard Class
Sickbeard = sickbeard.SB()

def showSearchDialog():
  # Get search text from user
  keyboard = xbmc.Keyboard('', 'Find a show on the TVDB', False)
  keyboard.doModal()
  if (keyboard.isConfirmed()):
    text = keyboard.getText() 
  return text  
  
# Add show main function. Shows the initial search window. 
def AddShow():
  text = showSearchDialog()
  # Search for the show using SB search API  
  search_results = Sickbeard.SearchShowName(text)
  if search_results == []:
    ShowMessage("Search Results", "No shows found")
    return
  else:
    selected_show = ShowSelectMessage(search_results)
  # 1. Need to get sb.getrootdirs and select one... No adding/deleting for now, would need to browse remote dir :(  
  root_dir = SelectRootDirMessage()
  # 2. sb.getdefaults for status of show eps.  Need to make each option selectable so you can change initial status, folders, quality.
  default_status, default_folders, default_quality = Sickbeard.GetDefaults()
  
  initial_status = SetInitialStatusMessage(default_status)
  use_season_folders = SetSeasonFolderMessage(default_folders)
  quality = SetQualityMessage(default_quality)
  
  tvdbid = search_results[selected_show]['tvdbid']
  ret = Sickbeard.AddNewShow(tvdbid, root_dir, initial_status, use_season_folders, quality)
  if ret == "success":
    ShowMessage("Add Show", "Successfully added "+search_results[selected_show]['name'])
  else:
    ShowMessage("Add Show", "Failed to add "+search_results[selected_show]['name'])
    
# Search results selection window
def ShowSelectMessage(shows):
  formatted_shows = []
  for show in shows:
    try:
      show_name = ""+show['name']
    except TypeError:
      continue
    try:
      first_aired = ""+show['first_aired']
    except TypeError:
      first_aired = "Unknown"
    formatted_shows.append(show_name+"  -  ("+first_aired+")")
  dialog = xbmcgui.Dialog()
  ret = dialog.select("Search Results", formatted_shows)
  return ret

# Basic show message window
def ShowMessage(header, text):
  dialog = xbmcgui.Dialog()
  dialog.ok(header, text)

# Gets the root dirs from SB then shows selection window
def SelectRootDirMessage():
  directory_result = Sickbeard.GetRoodDirs()
  directories = []
  for location in directory_result:
    directories.append(location['location'])
  dialog = xbmcgui.Dialog()
  ret = dialog.select("Pick the parent folder", directories)
  ret = directories[ret]
  return ret   

# Set initial status of show eps window
def SetInitialStatusMessage(status):
  status_list = ["wanted", "skipped", "archived", "ignored"]
  status_list_return = ["wanted", "skipped", "archived", "ignored"]
  for each in status_list:
    if each == status:
      index = status_list.index(status)
      status_list[index] = status+" (Default)"
  dialog = xbmcgui.Dialog()
  ret = dialog.select("Set initial status of episodes", status_list)
  return status_list_return[ret]

# Use season folders selection window
def SetSeasonFolderMessage(flatten_folders):
  if flatten_folders == 1:
    default = "No"
  else:
    default = "Yes"
    default = "No"
  dialog = xbmcgui.Dialog()
  ret = dialog.yesno("Use season folders?", "Default: "+default)
  return ret

# Set initial episode quality window
def SetQualityMessage(quality):
  if (quality.count("sddvd") > 0) or (quality.count("sdtv") > 0):
    quality_list = ["SD (Default)", "HD"]
  else:
    quality_list = ["SD", "HD (Default)"]
  dialog = xbmcgui.Dialog()
  ret = dialog.select("Set initial status of episodes", quality_list)
  if ret == 0:
    return "sdtv|sddvd"
  else:
    return "hdtv|hdwebdl|hdbluray"

# Execute the add show process
AddShow()

# Refresh the directory listing after adding a show
xbmc.executebuiltin("Container.Refresh")