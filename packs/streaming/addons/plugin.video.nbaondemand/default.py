# -*- coding: utf-8 -*-

'''
    NBA On-demand XBMC Addon
    Copyright (C) 2014 lambda,enen92

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

import urllib,urllib2,re,os,threading,datetime,time,base64,xbmc,xbmcplugin,xbmcgui,xbmcaddon,xbmcvfs
from operator import itemgetter
try:    import json
except: import simplejson as json
try:    import CommonFunctions
except: import commonfunctionsdummy as CommonFunctions
try:    import StorageServer
except: import storageserverdummy as StorageServer


action              = None
common              = CommonFunctions
language            = xbmcaddon.Addon().getLocalizedString
setSetting          = xbmcaddon.Addon().setSetting
getSetting          = xbmcaddon.Addon().getSetting
addonName           = xbmcaddon.Addon().getAddonInfo("name")
addonVersion        = xbmcaddon.Addon().getAddonInfo("version")
addonId             = xbmcaddon.Addon().getAddonInfo("id")
addonPath           = xbmcaddon.Addon().getAddonInfo("path")
addonFullId         = addonName + addonVersion
addonDesc           = language(30450).encode("utf-8")
cache               = StorageServer.StorageServer(addonFullId,1).cacheFunction
cache2              = StorageServer.StorageServer(addonFullId,24).cacheFunction
cache3              = StorageServer.StorageServer(addonFullId,720).cacheFunction
addonIcon           = os.path.join(addonPath,'icon.png')
addonFanart         = os.path.join(addonPath,'fanart.jpg')
addonArt            = os.path.join(addonPath,'resources/art')
addonImage          = os.path.join(addonPath,'resources/art/Image.jpg')
addonImage2         = os.path.join(addonPath,'resources/art/Image2.jpg')
addonGames          = os.path.join(addonPath,'resources/art/Games.png')
addonHighlights     = os.path.join(addonPath,'resources/art/Highlights.png')
addonTeams          = os.path.join(addonPath,'resources/art/Teams.png')
addonNext           = os.path.join(addonPath,'resources/art/Next.png')
dataPath            = xbmc.translatePath('special://profile/addon_data/%s' % (addonId))
viewData            = os.path.join(dataPath,'views.cfg')


class main:
    def __init__(self):
        global action
        index().container_data()
        params = {}
        splitparams = sys.argv[2][sys.argv[2].find('?') + 1:].split('&')
        for param in splitparams:
            if (len(param) > 0):
                splitparam = param.split('=')
                key = splitparam[0]
                try:    value = splitparam[1].encode("utf-8")
                except: value = splitparam[1]
                params[key] = value

        try:        action = urllib.unquote_plus(params["action"])
        except:     action = None
        try:        name = urllib.unquote_plus(params["name"])
        except:     name = None
        try:        url = urllib.unquote_plus(params["url"])
        except:     url = None
        try:        image = urllib.unquote_plus(params["image"])
        except:     image = None
        try:        date = urllib.unquote_plus(params["date"])
        except:     date = None
        try:        genre = urllib.unquote_plus(params["genre"])
        except:     genre = None
        try:        plot = urllib.unquote_plus(params["plot"])
        except:     plot = None
        try:        title = urllib.unquote_plus(params["title"])
        except:     title = None
        try:        show = urllib.unquote_plus(params["show"])
        except:     show = None
        try:        query = urllib.unquote_plus(params["query"])
        except:     query = None

        if action == None:                          root().get()
        elif action == 'item_play':                 contextMenu().item_play()
        elif action == 'item_random_play':          contextMenu().item_random_play()
        elif action == 'item_queue':                contextMenu().item_queue()
        elif action == 'item_play_from_here':       contextMenu().item_play_from_here(url)
        elif action == 'playlist_open':             contextMenu().playlist_open()
        elif action == 'settings_open':             contextMenu().settings_open()
        elif action == 'addon_home':                contextMenu().addon_home()
        elif action == 'view_videos':               contextMenu().view('videos')
        elif action == 'pages_games':               pages().games()
        elif action == 'pages_highlights':          pages().highlights()
        elif action == 'pages_teams':               pages().teams()
        elif action == 'pages_euroleague':          pages().euroleague()
        elif action == 'videos_added':              videos().added()
        elif action == 'videos_euroleague':         videos().all(url)
        elif action == 'videos_games':              videos().games(url)
        elif action == 'videos_highlights':         videos().highlights(url)
        elif action == 'videos_teams':              videos().teams(url)
        elif action == 'videos_parts':              videoparts().get(name, url, image, date, genre, plot, title, show)
        elif action == 'play':                      resolver().run(url)

        if action is None:
            pass
        elif action.startswith('videos'):
            xbmcplugin.setContent(int(sys.argv[1]), 'episodes')
            index().container_view('videos', {'skin.confluence' : 504})
        xbmcplugin.setPluginFanart(int(sys.argv[1]), addonFanart)
        xbmcplugin.endOfDirectory(int(sys.argv[1]))
        return

class getUrl(object):
    def __init__(self, url, close=True, proxy=None, post=None, mobile=False, referer=None, cookie=None, output='', timeout='10'):
        if not proxy is None:
            proxy_handler = urllib2.ProxyHandler({'http':'%s' % (proxy)})
            opener = urllib2.build_opener(proxy_handler, urllib2.HTTPHandler)
            opener = urllib2.install_opener(opener)
        if output == 'cookie' or not close == True:
            import cookielib
            cookie_handler = urllib2.HTTPCookieProcessor(cookielib.LWPCookieJar())
            opener = urllib2.build_opener(cookie_handler, urllib2.HTTPBasicAuthHandler(), urllib2.HTTPHandler())
            opener = urllib2.install_opener(opener)
        if not post is None:
            request = urllib2.Request(url, post)
        else:
            request = urllib2.Request(url,None)
        if mobile == True:
            request.add_header('User-Agent', 'Mozilla/5.0 (iPhone; U; CPU iPhone OS 4_0 like Mac OS X; en-us) AppleWebKit/532.9 (KHTML, like Gecko) Version/4.0.5 Mobile/8A293 Safari/6531.22.7')
        else:
            request.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:6.0) Gecko/20100101 Firefox/6.0')
        if not referer is None:
            request.add_header('Referer', referer)
        if not cookie is None:
            request.add_header('cookie', cookie)
        response = urllib2.urlopen(request, timeout=int(timeout))
        if output == 'cookie':
            result = str(response.headers.get('Set-Cookie'))
        elif output == 'geturl':
            result = response.geturl()
        else:
            result = response.read()
        if close == True:
            response.close()
        self.result = result

class uniqueList(object):
    def __init__(self, list):
        uniqueSet = set()
        uniqueList = []
        for n in list:
            if n not in uniqueSet:
                uniqueSet.add(n)
                uniqueList.append(n)
        self.list = uniqueList

class Thread(threading.Thread):
    def __init__(self, target, *args):
        self._target = target
        self._args = args
        threading.Thread.__init__(self)
    def run(self):
        self._target(*self._args)

class player(xbmc.Player):
    def __init__ (self):
        xbmc.Player.__init__(self)

    def run(self, url):
        item = xbmcgui.ListItem(path=url)
        xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, item)

    def onPlayBackStarted(self):
        return

    def onPlayBackEnded(self):
        return

    def onPlayBackStopped(self):
        return

class index:
    def infoDialog(self, str, header=addonName):
        try: xbmcgui.Dialog().notification(header, str, addonIcon, 3000, sound=False)
        except: xbmc.executebuiltin("Notification(%s,%s, 3000, %s)" % (header, str, addonIcon))

    def okDialog(self, str1, str2, header=addonName):
        xbmcgui.Dialog().ok(header, str1, str2)

    def selectDialog(self, list, header=addonName):
        select = xbmcgui.Dialog().select(header, list)
        return select

    def yesnoDialog(self, str1, str2, header=addonName, str3='', str4=''):
        answer = xbmcgui.Dialog().yesno(header, str1, str2, '', str4, str3)
        return answer

    def getProperty(self, str):
        property = xbmcgui.Window(10000).getProperty(str)
        return property

    def setProperty(self, str1, str2):
        xbmcgui.Window(10000).setProperty(str1, str2)

    def clearProperty(self, str):
        xbmcgui.Window(10000).clearProperty(str)

    def addon_status(self, id):
        check = xbmcaddon.Addon(id=id).getAddonInfo("name")
        if not check == addonName: return True

    def container_refresh(self):
        xbmc.executebuiltin("Container.Refresh")

    def container_data(self):
        if not xbmcvfs.exists(dataPath):
            xbmcvfs.mkdir(dataPath)
        if not xbmcvfs.exists(viewData):
            file = xbmcvfs.File(viewData, 'w')
            file.write('')
            file.close()

    def container_view(self, content, viewDict):
        try:
            skin = xbmc.getSkinDir()
            file = xbmcvfs.File(viewData)
            read = file.read().replace('\n','')
            file.close()
            view = re.compile('"%s"[|]"%s"[|]"(.+?)"' % (skin, content)).findall(read)[0]
            xbmc.executebuiltin('Container.SetViewMode(%s)' % str(view))
        except:
            try:
                id = str(viewDict[skin])
                xbmc.executebuiltin('Container.SetViewMode(%s)' % id)
            except:
                pass

    def rootList(self, rootList):
        total = len(rootList)
        for i in rootList:
            try:
                name = language(i['name']).encode("utf-8")
                image = '%s/%s' % (addonArt, i['image'])
                action = i['action']
                u = '%s?action=%s' % (sys.argv[0], action)

                cm = []

                item = xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=image)
                item.setInfo( type="Video", infoLabels={ "Label": name, "Title": name, "Plot": addonDesc } )
                item.setProperty("Fanart_Image", addonFanart)
                item.addContextMenuItems(cm, replaceItems=False)
                xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=item,totalItems=total,isFolder=True)
            except:
                pass

    def pageList(self, pageList):
        if pageList == None: return

        total = len(pageList)
        for i in pageList:
            try:
                name, url, image = i['name'], i['url'], i['image']
                sysname, sysurl, sysimage = urllib.quote_plus(name), urllib.quote_plus(url), urllib.quote_plus(image)

                if action == 'pages_games':
                    u = '%s?action=videos_games&url=%s' % (sys.argv[0], sysurl)
                elif action == 'pages_highlights':
                    u = '%s?action=videos_highlights&url=%s' % (sys.argv[0], sysurl)
                elif action == 'pages_teams':
                    u = '%s?action=videos_teams&url=%s' % (sys.argv[0], sysurl)
                elif action == 'pages_euroleague':
                    u = '%s?action=videos_euroleague&url=%s' % (sys.argv[0], sysurl)

                item = xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=image)
                item.setInfo( type="Video", infoLabels={ "Label": name, "Title": name, "Plot": addonDesc } )
                item.setProperty("Fanart_Image", addonFanart)
                item.addContextMenuItems([], replaceItems=False)
                xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=item,totalItems=total,isFolder=True)
            except:
                pass

    def videoList(self, videoList):
        if videoList == None: return

        total = len(videoList)
        for i in videoList:
            try:
                name, url, image, date, genre, plot, title, show = i['name'], i['url'], i['image'], i['date'], i['genre'], i['plot'], i['title'], i['show']
                if show == '': show = addonName
                if image == '': image = addonFanart
                if plot == '': plot = addonDesc
                if genre == '': genre = ' '
                if date == '': date = ' '

                if action == 'videos_euroleague': image = addonImage2
                else:  image = addonImage

                sysname, sysurl, sysimage, sysdate, sysgenre, sysplot, systitle, sysshow = urllib.quote_plus(name), urllib.quote_plus(url), urllib.quote_plus(image), urllib.quote_plus(date), urllib.quote_plus(genre), urllib.quote_plus(plot), urllib.quote_plus(title), urllib.quote_plus(show)
                u = '%s?action=videos_parts&name=%s&url=%s&image=%s&date=%s&genre=%s&plot=%s&title=%s&show=%s' % (sys.argv[0], sysname, sysurl, sysimage, sysdate, sysgenre, sysplot, systitle, sysshow)

                meta = {'label': title, 'title': title, 'studio': show, 'premiered': date, 'genre': genre, 'plot': plot}

                cm = []
                cm.append((language(30401).encode("utf-8"), 'RunPlugin(%s?action=item_play)' % (sys.argv[0])))
                cm.append((language(30404).encode("utf-8"), 'RunPlugin(%s?action=item_queue)' % (sys.argv[0])))
                cm.append((language(30410).encode("utf-8"), 'RunPlugin(%s?action=view_videos)' % (sys.argv[0])))
                cm.append((language(30407).encode("utf-8"), 'RunPlugin(%s?action=settings_open)' % (sys.argv[0])))
                cm.append((language(30408).encode("utf-8"), 'RunPlugin(%s?action=playlist_open)' % (sys.argv[0])))
                cm.append((language(30409).encode("utf-8"), 'RunPlugin(%s?action=addon_home)' % (sys.argv[0])))

                item = xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=image)
                item.setInfo( type="Video", infoLabels = meta )
                item.setProperty("IsPlayable", "true")
                item.setProperty("Video", "true")
                item.setProperty("Fanart_Image", addonFanart)
                item.addContextMenuItems(cm, replaceItems=True)
                xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=item,totalItems=total,isFolder=True)
            except:
                pass

    def videopartList(self, videopartList):
        if videopartList == None: return

        total = len(videopartList)
        for i in videopartList:
            try:
                name, url, image, date, genre, plot, title, show = i['name'], i['url'], i['image'], i['date'], i['genre'], i['plot'], i['title'], i['show']
                if show == '': show = addonName
                if image == '': image = addonFanart
                if plot == '': plot = addonDesc
                if genre == '': genre = ' '
                if date == '': date = ' '

                sysurl = urllib.quote_plus(url)
                u = '%s?action=play&url=%s' % (sys.argv[0], sysurl)

                meta = {'label': title, 'title': title, 'studio': show, 'premiered': date, 'genre': genre, 'plot': plot}

                cm = []
                cm.append((language(30405).encode("utf-8"), 'RunPlugin(%s?action=item_queue)' % (sys.argv[0])))
                cm.append((language(30403).encode("utf-8"), 'RunPlugin(%s?action=item_play_from_here&url=%s)' % (sys.argv[0], sysurl)))
                cm.append((language(30410).encode("utf-8"), 'RunPlugin(%s?action=view_videos)' % (sys.argv[0])))
                cm.append((language(30407).encode("utf-8"), 'RunPlugin(%s?action=settings_open)' % (sys.argv[0])))
                cm.append((language(30408).encode("utf-8"), 'RunPlugin(%s?action=playlist_open)' % (sys.argv[0])))
                cm.append((language(30409).encode("utf-8"), 'RunPlugin(%s?action=addon_home)' % (sys.argv[0])))

                item = xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=image)
                item.setInfo( type="Video", infoLabels = meta )
                item.setProperty("IsPlayable", "true")
                item.setProperty("Video", "true")
                item.setProperty("Fanart_Image", addonFanart)
                item.addContextMenuItems(cm, replaceItems=True)
                xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=item,totalItems=total,isFolder=False)
            except:
                pass

class contextMenu:
    def item_play(self):
        playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
        playlist.clear()
        xbmc.executebuiltin('Action(Queue)')
        playlist.unshuffle()
        xbmc.Player().play(playlist)

    def item_random_play(self):
        playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
        playlist.clear()
        xbmc.executebuiltin('Action(Queue)')
        playlist.shuffle()
        xbmc.Player().play(playlist)

    def item_queue(self):
        xbmc.executebuiltin('Action(Queue)')

    def item_play_from_here(self, url):
        playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
        playlist.clear()
        playlist.unshuffle()
        total = xbmc.getInfoLabel('Container.NumItems')
        for i in range(0, int(total)):
            i = str(i)
            label = xbmc.getInfoLabel('ListItemNoWrap(%s).Label' % i)
            if label == '': break

            params = {}
            path = xbmc.getInfoLabel('ListItemNoWrap(%s).FileNameAndPath' % i)
            path = urllib.quote_plus(path).replace('+%26+', '+&+')
            query = path.split('%3F', 1)[-1].split('%26')
            for i in query: params[urllib.unquote_plus(i).split('=')[0]] = urllib.unquote_plus(i).split('=')[1]
            u = '%s?action=play&url=%s' % (sys.argv[0], params["url"])

            meta = {'title': xbmc.getInfoLabel('ListItemNoWrap(%s).title' % i), 'studio': xbmc.getInfoLabel('ListItemNoWrap(%s).studio' % i), 'writer': xbmc.getInfoLabel('ListItemNoWrap(%s).writer' % i), 'director': xbmc.getInfoLabel('ListItemNoWrap(%s).director' % i), 'rating': xbmc.getInfoLabel('ListItemNoWrap(%s).rating' % i), 'duration': xbmc.getInfoLabel('ListItemNoWrap(%s).duration' % i), 'premiered': xbmc.getInfoLabel('ListItemNoWrap(%s).premiered' % i), 'plot': xbmc.getInfoLabel('ListItemNoWrap(%s).plot' % i)}
            poster, fanart = xbmc.getInfoLabel('ListItemNoWrap(%s).icon' % i), xbmc.getInfoLabel('ListItemNoWrap(%s).Property(Fanart_Image)' % i)

            item = xbmcgui.ListItem(label, iconImage="DefaultVideo.png", thumbnailImage=poster)
            item.setInfo( type="Video", infoLabels= meta )
            item.setProperty("IsPlayable", "true")
            item.setProperty("Video", "true")
            item.setProperty("Fanart_Image", fanart)
            playlist.add(u, item)
        xbmc.Player().play(playlist)

    def playlist_open(self):
        xbmc.executebuiltin('ActivateWindow(VideoPlaylist)')

    def settings_open(self):
        xbmc.executebuiltin('Addon.OpenSettings(%s)' % (addonId))

    def addon_home(self):
        xbmc.executebuiltin('Container.Update(plugin://%s/,replace)' % (addonId))

    def view(self, content):
        try:
            skin = xbmc.getSkinDir()
            skinPath = xbmc.translatePath('special://skin/')
            xml = os.path.join(skinPath,'addon.xml')
            file = xbmcvfs.File(xml)
            read = file.read().replace('\n','')
            file.close()
            try: src = re.compile('defaultresolution="(.+?)"').findall(read)[0]
            except: src = re.compile('<res.+?folder="(.+?)"').findall(read)[0]
            src = os.path.join(skinPath, src)
            src = os.path.join(src, 'MyVideoNav.xml')
            file = xbmcvfs.File(src)
            read = file.read().replace('\n','')
            file.close()
            views = re.compile('<views>(.+?)</views>').findall(read)[0]
            views = [int(x) for x in views.split(',')]
            for view in views:
                label = xbmc.getInfoLabel('Control.GetLabel(%s)' % (view))
                if not (label == '' or label is None): break
            file = xbmcvfs.File(viewData)
            read = file.read()
            file.close()
            file = open(viewData, 'w')
            for line in re.compile('(".+?\n)').findall(read):
                if not line.startswith('"%s"|"%s"|"' % (skin, content)): file.write(line)
            file.write('"%s"|"%s"|"%s"\n' % (skin, content, str(view)))
            file.close()
            viewName = xbmc.getInfoLabel('Container.Viewmode')
            index().infoDialog('%s%s%s' % (language(30301).encode("utf-8"), viewName, language(30302).encode("utf-8")))
        except:
            return

class root:
    def get(self):
        rootList = []
        rootList.append({'name': 30501, 'image': 'Latest.png', 'action': 'videos_added'})
        rootList.append({'name': 30502, 'image': 'Games.png', 'action': 'pages_games'})
        rootList.append({'name': 30503, 'image': 'Highlights.png', 'action': 'pages_highlights'})
        rootList.append({'name': 30504, 'image': 'Teams.png', 'action': 'pages_teams'})
        if getSetting("euroleague") == 'true':
            rootList.append({'name': 30505, 'image': 'Euroleague.png', 'action': 'pages_euroleague'})
        index().rootList(rootList)

class link:
    def __init__(self):
        self.livetv_base = 'http://livetv.sx'
        self.livetv_nba = 'http://livetv.sx/en/videotourney/3'
        self.livetv_nbateams = 'http://livetv.sx/en/tables/3'
        self.livetv_nbamatch = '/en/videotourney/3/'
        self.livetv_euroleague = 'http://livetv.sx/en/videotourney/41'

class pages:
    def __init__(self):
        self.list = []

    def games(self):
        self.list = self.livetv_list(link().livetv_nba, addonGames)
        index().pageList(self.list)

    def highlights(self):
        self.list = self.livetv_list(link().livetv_nba, addonHighlights)
        index().pageList(self.list)

    def teams(self):
        #self.list = self.livetv_list2(link().livetv_nbateams, addonTeams)
        self.list = cache2(self.livetv_list2, link().livetv_nbateams, addonTeams)
        index().pageList(self.list)

    def euroleague(self):
        self.list = self.livetv_list(link().livetv_euroleague, addonGames)
        index().pageList(self.list)

    def livetv_list(self, base, image):
        for i in range(0, 12):
            year = (datetime.datetime.utcnow() - datetime.timedelta(days = i*30)).strftime("%Y")
            month = (datetime.datetime.utcnow() - datetime.timedelta(days = i*30)).strftime("%m")
            monthDict = {'01': 'January', '02': 'February', '03': 'March', '04': 'April', '05': 'May', '06': 'June', '07': 'July', '08': 'August', '09': 'September', '10': 'October', '11': 'November', '12' : 'December'}

            name = '%s %s' % (monthDict[month], year)
            if any(name == i['name'] for i in self.list): continue
            name = name.encode('utf-8')
            url = '%s/%s%s' % (base, year, month)
            url = url.encode('utf-8')
            image = image.encode('utf-8')

            self.list.append({'name': name, 'url': url, 'image': image})

        return self.list

    def livetv_list2(self, base, image):
        try:
            result = getUrl(base).result
            result = result.decode('iso-8859-1').encode('utf-8')
            pages = re.compile('(<a href="/en/team/.+?">.+?</a>)').findall(result)
        except:
            return

        for page in pages:
            try:
                name = common.parseDOM(page, "a")[0]
                name = common.replaceHTMLCodes(name)
                name = name.encode('utf-8')

                if any(name == i['name'] for i in self.list): continue

                url = common.parseDOM(page, "a", ret="href")[0]
                url = '%s%svideo' % (link().livetv_base, url)
                url = common.replaceHTMLCodes(url)
                url = url.encode('utf-8')

                image = image.encode('utf-8')

                self.list.append({'name': name, 'url': url, 'image': image})
            except:
                pass

        self.list = sorted(self.list, key=itemgetter('name'))
        return self.list

class videos:
    def __init__(self):
        self.list = []

    def all(self, url):
        self.list = self.livetv_list(url)
        #self.list = cache(self.livetv_list, url)
        index().videoList(self.list)

    def added(self):
        self.list = self.livetv_list(link().livetv_nba)
        #self.list = cache(self.livetv_list, link().livetv_nba)
        index().videoList(self.list)

    def games(self, url):
        self.list = self.livetv_list(url)
        #self.list = cache(self.livetv_list, url)
        self.list = [i for i in self.list if any(x in json.loads(i['url']) for x in ['fullmatch', 'firsthalf', 'secondhalf'])]
        index().videoList(self.list)

    def highlights(self, url):
        self.list = self.livetv_list(url)
        #self.list = cache(self.livetv_list, url)
        self.list = [i for i in self.list if 'highlights' in json.loads(i['url'])]
        index().videoList(self.list)

    def teams(self, url):
        self.list = self.livetv_list2(url)
        #self.list = cache(self.livetv_list2, url)
        index().videoList(self.list)

    def livetv_list(self, url):
        try:
            videos = []
            result = getUrl(url).result
            result = result.decode('iso-8859-1').encode('utf-8')
            result = result.split('color: #2862a8; font-size: 14px;')
            year = common.parseDOM(result[0], "a", attrs = { "class": "mwhite" })
            year = [i for i in year if i.isdigit()][0]
            for i in result:
                try: videos += [re.compile('(<b>.+?</b>)').findall(i)[0] + x for x in common.parseDOM(i, "table", attrs = { "height": "27" })]
                except: pass
        except:
            return

        for video in videos:
            try:
                title = re.compile('<b>(.+?)</b>').findall(video)
                title = [i for i in title if '&ndash;' in i or '-' in i][-1]
                title = title.replace('&ndash;', '-')
                title = common.replaceHTMLCodes(title)
                title = title.encode('utf-8')

                monthDict = {'January': '01', 'February': '02', 'March': '03', 'April': '04', 'May': '05', 'June': '06', 'July': '07', 'August': '08', 'September': '09', 'October': '10', 'November': '11', 'December' : '12'}
                date = re.compile('<b>(.+?)</b>').findall(video)[0]
                date = re.findall('(\d+?) (.+?),', date, re.I)[0]
                date = '%s-%s-%s' % (year, monthDict[date[1]], '%02d' % int(date[0]))

                name = '%s (%s)' % (title, date)
                name = common.replaceHTMLCodes(name)
                name = name.encode('utf-8')

                url = {}
                try:
                    u = re.compile('.*href="(.+?)">Full match record<').findall(video)[0]
                    url.update({'fullmatch': link().livetv_base + u})
                except:
                    pass
                try:
                    u = re.compile('.*href="(.+?)">First Half<').findall(video)[0]
                    url.update({'firsthalf': link().livetv_base + u})
                except:
                    pass
                try:
                    u = re.compile('.*href="(.+?)">Second Half<').findall(video)[0]
                    url.update({'secondhalf': link().livetv_base + u})
                except:
                    pass
                try:
                    u = re.compile('.*href="(.+?)">Highlights<').findall(video)[0]
                    url.update({'highlights': link().livetv_base + u})
                except:
                    pass
                url = '{' + ', '.join('"%s": "%s"' % (k,v) for k,v in url.iteritems()) + '}'
                if url == '{}': raise Exception()
                url = common.replaceHTMLCodes(url)
                url = url.encode('utf-8')

                try:
                    plot = re.compile('<b>(\d+?:\d+?)</b>').findall(video)[0]
                    plot = ' (%s)' % plot
                except:
                    plot = ''
                plot = title + plot
                plot = common.replaceHTMLCodes(plot)
                plot = plot.encode('utf-8')

                self.list.append({'name': name, 'url': url, 'image': '', 'date': date, 'genre': 'Sports', 'plot': plot, 'title': title, 'show': ''})
            except:
                pass

        return self.list

    def livetv_list2(self, url):
        try:
            result = getUrl(url).result
            result = result.decode('iso-8859-1').encode('utf-8')
            result = result.split('class="main"')
            result = [i for i in result if i.startswith(' href="%s"' % link().livetv_nbamatch)][-1]
            videos = common.parseDOM(result, "table", attrs = { "height": "27" })
        except:
            return

        for video in videos:
            try:
                title = re.compile('<b>(.+?)</b>').findall(video)
                title = [i for i in title if '&ndash;' in i or '-' in i][-1]
                title = title.replace('&ndash;', '-')
                title = common.replaceHTMLCodes(title)
                title = title.encode('utf-8')

                date = common.parseDOM(video, "span", attrs = { "class": "date" })[0]
                date = re.findall('(\d+)[.](\d+)[.](\d+)', date, re.I)[0]
                date = '%s-%s-%s' % ('20' + '%02d' % int(date[2]), '%02d' % int(date[1]), '%02d' % int(date[0]))

                name = '%s (%s)' % (title, date)
                name = common.replaceHTMLCodes(name)
                name = name.encode('utf-8')

                url = {}
                try:
                    u = re.compile('.*href="(.+?)">Full match record<').findall(video)[0]
                    url.update({'fullmatch': link().livetv_base + u})
                except:
                    pass
                try:
                    u = re.compile('.*href="(.+?)">First Half<').findall(video)[0]
                    url.update({'firsthalf': link().livetv_base + u})
                except:
                    pass
                try:
                    u = re.compile('.*href="(.+?)">Second Half<').findall(video)[0]
                    url.update({'secondhalf': link().livetv_base + u})
                except:
                    pass
                try:
                    u = re.compile('.*href="(.+?)">Highlights<').findall(video)[0]
                    url.update({'highlights': link().livetv_base + u})
                except:
                    pass
                url = '{' + ', '.join('"%s": "%s"' % (k,v) for k,v in url.iteritems()) + '}'
                if url == '{}': raise Exception()
                url = common.replaceHTMLCodes(url)
                url = url.encode('utf-8')

                try:
                    plot = re.compile('<b>(\d+?:\d+?)</b>').findall(video)[0]
                    plot = ' (%s)' % plot
                except:
                    plot = ''
                plot = title + plot
                plot = common.replaceHTMLCodes(plot)
                plot = plot.encode('utf-8')

                self.list.append({'name': name, 'url': url, 'image': '', 'date': date, 'genre': 'Sports', 'plot': plot, 'title': title, 'show': ''})
            except:
                pass

        return self.list

class videoparts:
    def __init__(self):
        self.list = []

    def get(self, name, url, image, date, genre, plot, title, show):
        self.list = self.livetv_list(name, url, image, date, genre, plot, title, show)
        index().videopartList(self.list)

    def livetv_list(self, name, url, image, date, genre, plot, title, show):
        i = json.loads(url)
        try:
            self.list.append({'name': title, 'url': i['fullmatch'], 'image': image, 'date': date, 'genre': genre, 'plot': plot, 'title': title, 'show': show})
        except:
            pass
        try:
            self.list.append({'name': '%s (1)' % title, 'url': i['firsthalf'], 'image': image, 'date': date, 'genre': genre, 'plot': plot, 'title': title, 'show': show})
        except:
            pass
        try:
            self.list.append({'name': '%s (2)' % title, 'url': i['secondhalf'], 'image': image, 'date': date, 'genre': genre, 'plot': plot, 'title': title, 'show': show})
        except:
            pass
        try:
            self.list.append({'name': '%s (Highlights)' % title, 'url': i['highlights'], 'image': image, 'date': date, 'genre': genre, 'plot': plot, 'title': title, 'show': show})
        except:
            pass

        return self.list

class resolver:
    def run(self, url):
        try:
            url = self.livetv(url)
            if url is None: raise Exception()
            player().run(url)
            return url
        except:
            index().infoDialog(language(30303).encode("utf-8"))
            return

    def livetv(self, url):
        try:
            r = getUrl(url).result
            r = r.decode('iso-8859-1').encode('utf-8')
        except:
            return

        try:
            vk = re.compile('"(https://vk.com/.+?)"').findall(r)
            vk += re.compile('"(http://vk.com/.+?)"').findall(r)
            vk = common.replaceHTMLCodes(vk[0])
            vk = vk.replace('http://', 'https://')
            vk = vk.encode('utf-8')

            result = getUrl(vk).result
            url = None
            try: url = re.compile('url240=(.+?)&').findall(result)[0]
            except: pass
            try: url = re.compile('url360=(.+?)&').findall(result)[0]
            except: pass
            try: url = re.compile('url480=(.+?)&').findall(result)[0]
            except: pass
            if getSetting("quality") == 'true' or url is None:
                try: url = re.compile('url720=(.+?)&').findall(result)[0]
                except: pass

            if url == None: raise Exception()
            return url
        except:
            pass

        try:
            result = r.replace('\/', '/').replace('youtube.com/watch', 'youtube.com/embed/')

            youtube = re.compile('youtube.com/embed/(.+?)"').findall(result)[0]
            youtube = youtube.split("?v=")[-1].split("/")[-1].split("?")[0]

            url = 'plugin://plugin.video.youtube/?action=play_video&videoid=%s' % youtube
            if index().addon_status('plugin.video.youtube') is None:
                index().okDialog(language(30321).encode("utf-8"), language(30322).encode("utf-8"))
                return

            return url
        except:
            pass

        try:
            nba_com = re.compile('addVariable[(]"file".+?"(.+?)"').findall(r)[0]
            url = nba_com
            return url
        except:
            pass

main()