import urllib
import sys
import xbmcgui
import xbmcplugin
import xbmcaddon
import resources.lib.settings

# Add the main directory folders
def mainMenu():
        addDirectory('Manage Shows', 1)
        addDirectory('Upcoming Episodes', 2)
        addDirectory('History', 3)

# Add directory item
def addDirectory(menu_item_name, menu_number):
        return_url = sys.argv[0]+"?url="+urllib.quote_plus("")+"&mode="+str(menu_number)+"&name="+urllib.quote_plus(menu_item_name)
        list_item = xbmcgui.ListItem(menu_item_name)
        xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=return_url, listitem=list_item, isFolder=True, totalItems=3)

# Get the parameters from the URL supplied as an arg to this script
def getParameters():
        param=[]
        try:
          paramstring=sys.argv[2]
          if len(paramstring)>=2:
                  params=sys.argv[2]
                  cleanedparams=params.replace('?','')
                  if (params[len(params)-1]=='/'):
                          params=params[0:len(params)-2]
                  pairsofparams=cleanedparams.split('&')
                  param={}
                  for i in range(len(pairsofparams)):
                          splitparams={}
                          splitparams=pairsofparams[i].split('=')
                          if (len(splitparams))==2:
                                  param[splitparams[0]]=splitparams[1]
          return param
        except:
          return param
 
# Initialize URL parameters
url = None
name = None
menu_number = None          
params = getParameters()

# Parse internal URL
try:
        url = urllib.unquote_plus(params["url"])
        print url
except:
        pass
try:
        name = urllib.unquote_plus(params["name"])
        print name
except:
        pass
try:
        menu_number = int(params["mode"])
        print menu_number
except:
        pass

# Open directories based on selection
if menu_number == None:
        mainMenu()
       
elif menu_number == 1:
        import resources.lib.shows as shows
        shows.menu()
        
elif menu_number == 2:
        import resources.lib.upcoming as upcoming
        upcoming.menu()
        
elif menu_number == 3:
        import resources.lib.history as history
        history.menu()

elif menu_number == 4:
        import resources.lib.seasons as seasons
        seasons.menu(url)

elif menu_number == 5:
        import resources.lib.episodes as episodes
        episodes.menu(url, name)

xbmcplugin.endOfDirectory(int(sys.argv[1]))        
