### ############################################################################################################
###	#	
### # Project: 			#		KissAnime.com - by The Highway 2013.
### # Author: 			#		The Highway
### # Version:			#		v0.6.5
### # Description: 	#		http://www.KissAnime.com
###	#	
### ############################################################################################################
### ############################################################################################################
_testing=True
_testing=False
##### Imports #####
import xbmc,xbmcplugin,xbmcgui,xbmcaddon,xbmcvfs
#import requests ### (Removed in v0.2.1b to fix scripterror on load on Mac OS.) ### 
import urllib,urllib2,re,os,sys,htmllib,string,StringIO,logging,random,array,time,datetime
import copy
import HTMLParser, htmlentitydefs
## ### ## 
#try: 		import StorageServer
#except: 
#	print "failed to import StorageServer"
#	import storageserverdummy as StorageServer
try:
	try: import StorageServer as StorageServer
	except: 
		try: import z_StorageServer as StorageServer
		except:
			try: import storageserverdummy as StorageServer
			except:
				try: import z_storageserverdummy as StorageServer
				except: pass
	#cache=StorageServer.StorageServer(plugin_id)
except: pass
## ### ## 
#try: 		from t0mm0.common.addon 				import Addon
#except: from t0mm0_common_addon 				import Addon
#try: 		from t0mm0.common.net 					import Net
#except: from t0mm0_common_net 					import Net
try: 			from addon.common.addon 				import Addon
except:
	try: 		from t0mm0.common.addon 				import Addon
	except: 
		try: from z_t0mm0_common_addon 				import Addon
		except: pass
try: 			from addon.common.net 					import Net
except:
	try: 		from t0mm0.common.net 					import Net
	except: 
		try: from z_t0mm0_common_net 					import Net
		except: pass
### 
import teh_tools as my_tools
from teh_tools 		import *
from config 			import *
##### /\ ##### Imports #####
### ############################################################################################################
### ############################################################################################################
### ############################################################################################################
__plugin__=ps('__plugin__'); __authors__=ps('__authors__'); __credits__=ps('__credits__'); _addon_id=ps('_addon_id'); _domain_url=ps('_domain_url'); _database_name=ps('_database_name'); _plugin_id=ps('_addon_id')
_database_file=os.path.join(xbmc.translatePath("special://database"),ps('_database_name')+'.db'); 
### 
_addon=Addon(ps('_addon_id'), sys.argv); addon=_addon; _plugin=xbmcaddon.Addon(id=ps('_addon_id')); 
try: cache=StorageServer.StorageServer(ps('_addon_id'))
except: debob("Error initializing cache=StorageServer."); 
### 
### ############################################################################################################
### ############################################################################################################
### ############################################################################################################
##### Paths #####
### # ps('')
_addonPath	=xbmc.translatePath(_plugin.getAddonInfo('path'))
_artPath		=xbmc.translatePath(os.path.join(_addonPath,ps('_addon_path_art')))
_datapath 	=xbmc.translatePath(_addon.get_profile()); _artIcon		=_addon.get_icon(); _artFanart	=_addon.get_fanart()
##### /\ ##### Paths #####
##### Important Functions with some dependencies #####
def art(f,fe=ps('default_art_ext')): return xbmc.translatePath(os.path.join(_artPath,f+fe)) ### for Making path+filename+ext data for Art Images. ###
##### /\ ##### Important Functions with some dependencies #####
##### Settings #####
_setting={}; _setting['enableMeta']	=	_enableMeta			=tfalse(addst("enableMeta"))
_setting['debug-enable']=	_debugging			=tfalse(addst("debug-enable")); _setting['debug-show']	=	_shoDebugging		=tfalse(addst("debug-show"))
_setting['meta.movie.domain']=ps('meta.movie.domain'); _setting['meta.movie.search']=ps('meta.movie.search')
_setting['meta.tv.domain']   =ps('meta.tv.domain');    _setting['meta.tv.search']   =ps('meta.tv.search')
_setting['meta.tv.page']=ps('meta.tv.page'); _setting['meta.tv.fanart.url']=ps('meta.tv.fanart.url'); _setting['meta.tv.fanart.url2']=ps('meta.tv.fanart.url2'); _setting['label-empty-favorites']=tfalse(addst('label-empty-favorites'))
CurrentPercent=0; CancelDownload=False

##### /\ ##### Settings #####
##### Variables #####
_art404=ps('img_hot') #'http://www.solarmovie.so/images/404.png' #_art404=art('404')
_art150=ps('img_hot') #'http://www.solarmovie.so/images/thumb150.png' #_art150=art('thumb150')
_artDead=ps('img_hot') #'http://www.solarmovie.so/images/deadplanet.png' #_artDead=art('deadplanet')
_artSun=ps('img_hot') #art('sun'); 
COUNTRIES=ps('COUNTRIES'); GENRES=ps('GENRES'); _default_section_=ps('default_section'); net=Net(); DB=_database_file; BASE_URL=_domain_url;
#_artFanart=xbmc.translatePath(os.path.join(_addonPath,'fanart5.jpg'))
##### /\ ##### Variables #####
deb('Addon Path',_addonPath);  deb('Art Path',_artPath); deb('Addon Icon Path',_artIcon); deb('Addon Fanart Path',_artFanart)

XBMCversion={}
XBMCversion['All']=xbmc.getInfoLabel("System.BuildVersion"); 
XBMCversion['Ver']=XBMCversion['All']; XBMCversion['Release']=''; XBMCversion['Date']=''; 
if ('Git:' in XBMCversion['All']) and ('-' in XBMCversion['All']): XBMCversion['Date']=XBMCversion['All'].split('Git:')[1].split('-')[0]
if ' ' in XBMCversion['Ver']: XBMCversion['Ver']=XBMCversion['Ver'].split(' ')[0]
if '-' in XBMCversion['Ver']: XBMCversion['Release']=XBMCversion['Ver'].split('-')[1]; XBMCversion['Ver']=XBMCversion['Ver'].split('-')[0]
if len(XBMCversion['Ver']) > 1: XBMCversion['two']=str(XBMCversion['Ver'][0])+str(XBMCversion['Ver'][1])
else: XBMCversion['two']='00'
if len(XBMCversion['Ver']) > 3: XBMCversion['three']=str(XBMCversion['Ver'][0])+str(XBMCversion['Ver'][1])+str(XBMCversion['Ver'][3])
else: XBMCversion['three']='000'
deb('Version All',XBMCversion['All']); deb('Version Number',XBMCversion['Ver']); deb('Version Release Name',XBMCversion['Release']); deb('Version Date',XBMCversion['Date']); 
try: sDevice=addst("device");
except: sDevice="NORMAL"; 
CurDate=time.strftime("%Y-%m-%d"); CurTime24=time.strftime("%H:%M"); CurTime12=time.strftime("%I:%M"); 
sOS=str(get_xbmc_os()); deb('OS',sOS); 

#print os.system()
#print os.name()
#print os.uname()
#print sys.platform()

### ############################################################################################################
def eod(): _addon.end_of_directory()
def deadNote(header='',msg='',delay=5000,image=_artDead): _addon.show_small_popup(title=header,msg=msg,delay=delay,image=image)
def sunNote( header='',msg='',delay=5000,image=_artSun):
	header=cFL(header,ps('cFL_color')); msg=cFL(msg,ps('cFL_color2'))
	_addon.show_small_popup(title=header,msg=msg,delay=delay,image=image)
def messupText(t,_html=False,_ende=False,_a=False,Slashes=False):
	if (_html==True): t=ParseDescription(HTMLParser.HTMLParser().unescape(t))
	if (_ende==True): t=t.encode('ascii', 'ignore'); t=t.decode('iso-8859-1')
	if (_a==True): t=_addon.decode(t); t=_addon.unescape(t)
	if (Slashes==True): t=t.replace( '_',' ')
	return t
def name2path(name):  return (((name.lower()).replace('.','-')).replace(' ','-')).replace('--','-')
def name2pathU(name): return (((name.replace(' and ','-')).replace('.','-')).replace(' ','-')).replace('--','-')
### ############################################################################################################
### ############################################################################################################
##### Queries #####
_param={}
_param['mode']=addpr('mode',''); _param['url']=addpr('url',''); _param['pagesource'],_param['pageurl'],_param['pageno'],_param['pagecount']=addpr('pagesource',''),addpr('pageurl',''),addpr('pageno',0),addpr('pagecount',1)
_param['img']=addpr('img',''); _param['fanart']=addpr('fanart',''); _param['thumbnail'],_param['thumbnail'],_param['thumbnail']=addpr('thumbnail',''),addpr('thumbnailshow',''),addpr('thumbnailepisode','')
_param['section']=addpr('section','movies'); _param['title']=addpr('title',''); _param['year']=addpr('year',''); _param['genre']=addpr('genre','')
_param['by']=addpr('by',''); _param['letter']=addpr('letter',''); _param['showtitle']=addpr('showtitle',''); _param['showyear']=addpr('showyear',''); _param['listitem']=addpr('listitem',''); _param['infoLabels']=addpr('infoLabels',''); _param['season']=addpr('season',''); _param['episode']=addpr('episode','')
_param['pars']=addpr('pars',''); _param['labs']=addpr('labs',''); _param['name']=addpr('name',''); _param['thetvdbid']=addpr('thetvdbid','')
_param['plot']=addpr('plot',''); _param['tomode']=addpr('tomode',''); _param['country']=addpr('country','')
_param['thetvdb_series_id']=addpr('thetvdb_series_id',''); _param['dbid']=addpr('dbid',''); _param['user']=addpr('user','')
_param['subfav']=addpr('subfav',''); _param['episodetitle']=addpr('episodetitle',''); _param['special']=addpr('special',''); _param['studio']=addpr('studio','')

#_param['']=_addon.queries.get('','')
#_param['']=_addon.queries.get('','')
##_param['pagestart']=addpr('pagestart',0)
##### /\
### ############################################################################################################
### ############################################################################################################
ww6='[COLOR black]@[/COLOR]'; 
ww7='[COLOR mediumpurple]@[/COLOR]'; 
def wwA(t,ww): #for Watched State Display
	if   ww==7: t=ww7+t
	elif ww==6: t=ww6+t
	return t
def AFColoring(t): 
	if len(t)==0: return t
	elif len(t)==1: return cFL(t,'firebrick')
	else: return cFL(cFL_(t,'firebrick'),'mediumpurple')


### ############################################################################################################
### ############################################################################################################
### ############################################################################################################
##### Player Functions #####
def GetPlayerCore():
	try:
		PlayerMethod=addst("core-player")
		if   (PlayerMethod=='DVDPLAYER'): PlayerMeth=xbmc.PLAYER_CORE_DVDPLAYER
		elif (PlayerMethod=='MPLAYER'): PlayerMeth=xbmc.PLAYER_CORE_MPLAYER
		elif (PlayerMethod=='PAPLAYER'): PlayerMeth=xbmc.PLAYER_CORE_PAPLAYER
		else: PlayerMeth=xbmc.PLAYER_CORE_AUTO
	except: PlayerMeth=xbmc.PLAYER_CORE_AUTO
	return PlayerMeth

def PlayURL(url):
	play=xbmc.Player(GetPlayerCore()) ### xbmc.PLAYER_CORE_AUTO | xbmc.PLAYER_CORE_DVDPLAYER | xbmc.PLAYER_CORE_MPLAYER | xbmc.PLAYER_CORE_PAPLAYER
	try: _addon.resolve_url(url)
	except: t=''
	try: play.play(url)
	except: t=''

def PlayVideo(url,title='',studio='',img='',showtitle='',plot='',autoplay=False): #PlayVideo(url, infoLabels, listitem)
	WhereAmI('@ PlayVideo -- Getting ID From:  %s' % url)
	if (img==''): img=_artIcon
	try: visited_add(studio)
	except: pass
	infoLabels={"Studio":studio,"ShowTitle":showtitle,"Title":title,"Plot":plot}; debob(infoLabels); 
	if autoplay==True:
		_addon.addon.setSetting(id="LastAutoPlayItemUrl", value=url)
		_addon.addon.setSetting(id="LastAutoPlayItemName", value=title)
		_addon.addon.setSetting(id="LastAutoPlayItemImg", value=img)
		_addon.addon.setSetting(id="LastAutoPlayItemStudio", value=studio)
	else:
		_addon.addon.setSetting(id="LastVideoPlayItemUrl", value=url)
		_addon.addon.setSetting(id="LastVideoPlayItemName", value=title)
		_addon.addon.setSetting(id="LastVideoPlayItemImg", value=img)
		_addon.addon.setSetting(id="LastVideoPlayItemStudio", value=studio)
	if (autoplay==False): eod()
	## ### ## 
	deb('Device Option',sDevice); 
	#if sDevice=="NORMAL":
	if sDevice=="OUYA(Gotham)": debob("Using Alternative Play Method for "+str(sDevice)); PlayURL(url); return
	
	
	## ### ## 
	li=xbmcgui.ListItem(title,iconImage=img,thumbnailImage=img)
	li.setInfo(type="Video", infoLabels=infoLabels ); li.setProperty('IsPlayable', 'true')
	#xbmc.Player().stop()
	try: _addon.resolve_url(url)
	except: t=''
	play=xbmc.Player(GetPlayerCore()) ### xbmc.PLAYER_CORE_AUTO | xbmc.PLAYER_CORE_DVDPLAYER | xbmc.PLAYER_CORE_MPLAYER | xbmc.PLAYER_CORE_PAPLAYER
	#xbmcplugin.setResolvedUrl(int(sys.argv[1]), True)
	#try: html=nURL(url,method='head',headers={'Referer':_domain_url})
	#except: html=''
	#deb('length of html',str(len(html)))
	#from teh_tools import _SaveFile
	#_SaveFile(xbmc.translatePath(os.path.join(_addonPath,'resources','testing.txt')),html)
	#try: html=nURL('http://s10.histats.com/js15_gif.js',method='head',headers={'Referer':_domain_url})
	#except: html=''
	#xbmc.getIPAddress()
	#MyIP=xbmc.getIPAddress()
	#MyIP=""
	#MyIP="0.0.0.0"
	#deb('my ip',xbmc.getIPAddress())
	url2=url
	#url2=url2.replace('&ip=0.0.0.0&','&ip='+MyIP+'&')
	#url2=url2.replace('&cmo=sensitive_content=yes&','&')
	#url2=url2.replace('&sparams=id,itag,source,ip,ipbits,expire&','&sparams=expire,id,ip,ipbits,itag,source&')
	##url2=url2.replace('&itag=5&','&itag=34&')
	#url2=url2.replace('&key=lh1&','&key=cms1&')
	##url2+='&cpn='
	#url2+='&cms_redirect=yes'
	##url2+='&ms=nxu'
	##url2+='&mt='
	##url2+='&mv=m'
	##url2='http://redirector.googlevideo.com/videoplayback?id=f7b436d64b869da8&itag=34&source=picasa&ip=199.0.197.160&ipbits=0&expire=1385481949&sparams=expire,id,ip,ipbits,itag,source&signature=3155D80C58FF4E1C35F46C66957FF4625495D36E.52DED4EDC5079C8FFAA8AA04754F9347808D0B8B&key=cms1'
	##url2='http://redirector.googlevideo.com/videoplayback?id=2f676cc6a678c32e&itag=5&source=picasa&ip=199.0.197.160&ipbits=0&expire=1385483906&sparams=expire,id,ip,ipbits,itag,source&signature=12A862B470AFF570F006AB2AC81DA24A3FCEECFB.4BB4AE0D52D543E7054211500A12B1A34F11272E&key=lh1'
	##url2='http://redirector.googlevideo.com/videoplayback?id=2f676cc6a678c32e&itag=5&source=picasa&ip=199.0.197.160&ipbits=0&expire=1385483906&sparams=expire,id,ip,ipbits,itag,source&signature=12A862B470AFF570F006AB2AC81DA24A3FCEECFB.4BB4AE0D52D543E7054211500A12B1A34F11272E&key=cms1'
	deb('url2',url2)
	
	try:
		play.play(url2, li); 
		xbmcplugin.setResolvedUrl(handle=int(sys.argv[1]), succeeded=True, listitem=li)
	except: pass
	#try: play.play(url, li); 
	#xbmcplugin.setResolvedUrl(int(sys.argv[1]), True)
	#try: _addon.resolve_url(url)
	#except: t=''
	#xbmc.sleep(7000)

def PlayLibrary(section, url, showtitle='', showyear=''): ### Menu for Listing Hosters (Host Sites of the actual Videos)
	WhereAmI('@ Play Library: %s' % url); sources=[]; listitem=xbmcgui.ListItem()
	#eod()
	#_addon.resolve_url(url)
	if (url==''): return
	html=net.http_GET(url).content; html=html.encode("ascii", "ignore")
	##if (_debugging==True): print html
	#if  ( section == 'tv'): ## TV Show ## Title (Year) - Info
	#	match=re.compile(ps('LLinks.compile.show_episode.info'), re.MULTILINE | re.IGNORECASE | re.DOTALL).findall(html)[0] ### <title>Watch The Walking Dead Online for Free - Prey - S03E14 - 3x14 - SolarMovie</title>
	#	if (_debugging==True): print match
	#	if (match==None):  return
	#	ShowYear=_param['year'] #ShowYear=showyear
	#	ShowTitle=match[0].strip(); EpisodeTitle=match[1].strip(); Season=match[2].strip(); Episode=match[3].strip()
	#	ShowTitle=HTMLParser.HTMLParser().unescape(ShowTitle); ShowTitle=ParseDescription(ShowTitle); ShowTitle=ShowTitle.encode('ascii', 'ignore'); ShowTitle=ShowTitle.decode('iso-8859-1'); EpisodeTitle=HTMLParser.HTMLParser().unescape(EpisodeTitle); EpisodeTitle=ParseDescription(EpisodeTitle); EpisodeTitle=EpisodeTitle.encode('ascii', 'ignore'); EpisodeTitle=EpisodeTitle.decode('iso-8859-1')
	#	if ('<p id="plot_' in html):
	#		ShowPlot=(re.compile(ps('LLinks.compile.show.plot'), re.MULTILINE | re.IGNORECASE | re.DOTALL).findall(html)[0]).strip(); ShowPlot=HTMLParser.HTMLParser().unescape(ShowPlot); ShowPlot=ParseDescription(ShowPlot); ShowPlot=ShowPlot.encode('ascii', 'ignore'); ShowPlot=ShowPlot.decode('iso-8859-1')
	#	else: ShowPlot=''
	#	match=re.compile(ps('LLinks.compile.imdb.url_id'), re.MULTILINE | re.IGNORECASE | re.DOTALL).findall(html)[0]
	#	if (_debugging==True): print match
	#	(IMDbURL,IMDbID)=match; IMDbURL=IMDbURL.strip(); IMDbID=IMDbID.strip(); My_infoLabels={ "Studio": ShowTitle+'  ('+ShowYear+'):  '+Season+'x'+Episode+' - '+EpisodeTitle, "Title": ShowTitle, "ShowTitle": ShowTitle, "Year": ShowYear, "Plot": ShowPlot, 'Season': Season, 'Episode': Episode, 'EpisodeTitle': EpisodeTitle, 'IMDbURL': IMDbURL, 'IMDbID': IMDbID, 'IMDb': IMDbID }; listitem.setInfo(type="Video", infoLabels=My_infoLabels )
	#else:	#################### Movie ## Title (Year) - Info
	#	match=re.compile(ps('LLinks.compile.show.title_year'), re.MULTILINE | re.IGNORECASE | re.DOTALL).findall(html)[0]
	#	if (_debugging==True): print match
	#	if (match==None): return
	#	ShowYear=match[1].strip(); ShowTitle=match[0].strip(); ShowTitle=HTMLParser.HTMLParser().unescape(ShowTitle); ShowTitle=ParseDescription(ShowTitle); ShowTitle=ShowTitle.encode('ascii', 'ignore'); ShowTitle=ShowTitle.decode('iso-8859-1'); ShowPlot=(re.compile(ps('LLinks.compile.show.plot'), re.MULTILINE | re.IGNORECASE | re.DOTALL).findall(html)[0]).strip(); ShowPlot=HTMLParser.HTMLParser().unescape(ShowPlot); ShowPlot=ParseDescription(ShowPlot); ShowPlot=ShowPlot.encode('ascii', 'ignore'); ShowPlot=ShowPlot.decode('iso-8859-1'); match=re.compile(ps('LLinks.compile.imdb.url_id'), re.MULTILINE | re.IGNORECASE | re.DOTALL).findall(html)[0]
	#	if (_debugging==True): print match
	#	(IMDbURL,IMDbID)=match; IMDbURL=IMDbURL.strip(); IMDbID=IMDbID.strip(); My_infoLabels={ "Studio": ShowTitle+'  ('+ShowYear+')', "Title": ShowTitle, "ShowTitle": ShowTitle, "Year": ShowYear, "Plot": ShowPlot, 'IMDbURL': IMDbURL, 'IMDbID': IMDbID, 'IMDb': IMDbID }; listitem.setInfo(type="Video", infoLabels=My_infoLabels )
	### Both -Movies- and -TV Shows- ### Hosters
	try:		matchH=re.compile(ps('LLinks.compile.hosters2'), re.MULTILINE | re.DOTALL | re.IGNORECASE).findall(html)
	except:	matchH=''
	#deb('length of matchH',str(len(matchH)))
	#print matchH
	if (len(matchH) > 0):
		oList=[]; hList=[]; matchH=sorted(matchH, key=lambda item: item[3], reverse=True)
		for url, host, quality, age in matchH:
			url=url.strip(); host=host.strip(); quality=quality.strip(); age=age.strip()
			try:		mID=re.compile('/.+?/.+?/([0-9]+)/', re.DOTALL | re.IGNORECASE).findall(url)[0]
			except: mID=''
			#deb('Media Passed',str(host)+' | '+str(quality)+' | '+str(age)+' | '+str(url)+' | '+str(mID))
			if (mID is not ''):
				oList.append(host+'  ['+quality+']  ('+age+')')
				hList.append([url,host,quality,age,mID])
		try:		rt=askSelection(oList,'Select Source:')
		except:	rt=''
		print rt
		if (rt==None) or (rt=='none') or (rt==False) or (rt==''): return
		hItem=hList[rt]
		deb('ID',hItem[4])
		urlB='%s/link/play/%s/' % (ps('_domain_url'),hItem[4])
		html=net.http_GET(urlB).content
		try: url=re.compile('<iframe.+?src="(.+?)"', re.MULTILINE | re.DOTALL | re.IGNORECASE).findall(html)[0]
		except: url=''
		url=url.replace('/embed/', '/file/'); deb('hoster url',url)
		#oList=[]
		#for url, host, quality, age in match:
		#	url=url.strip(); host=host.strip(); quality=quality.strip(); age=age.strip()
		#	print 'Media Failed:  '+str(host)+' | '+str(quality)+' | '+str(age)+' | '+url
		#	if (urlresolver.HostedMediaFile(url=url.strip()).valid_url()):
		#		try:		MediaID=urlresolver.HostedMediaFile(url=url).get_media_url()
		#		except: MediaID=''
		#		try:		MediaHost=urlresolver.HostedMediaFile(url=url).get_host()
		#		except: MediaHost=''
		#		print 'Media Passed:  '+str(MediaHost)+' | '+str(MediaID)+' | '+url
		#		if (MediaHost is not '') and (MediaID is not ''):
		#			oList.append(urlresolver.HostedMediaFile(host=MediaHost, media_id=MediaID))
		##
		#
		#try: url=urlresolver.choose_source(oList)
		#except: return
		#
		#MediaID=urlresolver.HostedMediaFile(url=url).get_media_url()
		#MediaHost=urlresolver.HostedMediaFile(url=url).get_host()
		#print 'Media:  '+str(MediaHost)+' | '+str(MediaID)+' | '+url
		#print str(urlresolver.HostedMediaFile(url=url.strip()).valid_url())
		#if (urlresolver.HostedMediaFile(url=url.strip()).valid_url()):
		#
		#
		#
		#
		#videoId=match.group(1); deb('Solar ID',videoId); url=BASE_URL + '/link/play/' + videoId + '/' ## Example: http://www.solarmovie.so/link/play/1052387/ ##
		#html=net.http_GET(url).content; match=re.search( '<iframe.+?src="(.+?)"', html, re.IGNORECASE | re.MULTILINE | re.DOTALL); link=match.group(1); link=link.replace('/embed/', '/file/'); deb('hoster link',link)
		#
		deb('video',url)
		liz=xbmcgui.ListItem(_param['showtitle'], iconImage="DefaultVideo.png", thumbnailImage=_param['img'])
		if  ( section == 'tv'): ## TV Show ## Title (Year) - Info
			liz.setInfo( type="Video", infoLabels={ "Title": _param['showtitle']+'  ('+_param['showyear']+')', "Studio": 'SolarMovie.so' } )
		else:	#################### Movies ### Title (Year) - Info
			liz.setInfo( type="Video", infoLabels={ "Title": _param['showtitle']+'  ('+_param['showyear']+')', "Studio": 'SolarMovie.so' } )
		liz.setProperty("IsPlayable","true")
		##pl=xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
		##pl.clear()
		##pl.add(url, liz)
		##xbmc.Player().play(pl)
		play=xbmc.Player(GetPlayerCore()) ### xbmc.PLAYER_CORE_AUTO | xbmc.PLAYER_CORE_DVDPLAYER | xbmc.PLAYER_CORE_MPLAYER | xbmc.PLAYER_CORE_PAPLAYER
		print url
		stream_url = urlresolver.HostedMediaFile(url).resolve()
		print stream_url
		play.play(stream_url, liz)
		#play.play(url, liz)
		liz.setPath(url)
		xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, liz)
		_addon.resolve_url(url)
		_addon.resolve_url(stream_url)
		##
		##
		##
		##count=1
		##for url, host, quality, age in match:
		##	host=host.strip(); quality=quality.strip(); name=str(count)+". "+host+' - [[B]'+quality+'[/B]] - ([I]'+age+'[/I])'
		##	if urlresolver.HostedMediaFile(host=host, media_id='xxx'):
		##		img=ps('Hosters.icon.url')+host; My_infoLabels['quality']=quality; My_infoLabels['age']=age; My_infoLabels['host']=host; _addon.add_directory({'section': section, 'img': _param['img'], 'mode': 'PlayVideo', 'url': url, 'quality': quality, 'age': age, 'infoLabels': My_infoLabels, 'listitem': listitem}, {'title':  name}, img=img, is_folder=False); count=count+1 
		eod()
	else: return
	### ################################################################

def DownloadStop():  ## Testing ## Doesn't work yet.
	global CancelDownload
	CancelDownload=True
	#global CancelDownload
	eod()
	#download_method=addst('download_method') ### 'Progress|ProgressBG|Hidden'
	#if   (download_method=='Progress'):
	#	dp=xbmcgui.DialogProgress()   ## For Frodo and earlier.
	#	dp.close()
	#elif (download_method=='ProgressBG'):
	#	dp=xbmcgui.DialogProgressBG() ## Only works on daily build of XBMC.
	#	dp.close()
	#elif (download_method=='Test'):
	#	t=''
	#elif (download_method=='Hidden'):
	#	t=''
	#else: deb('Download Error','Incorrect download method.'); myNote('Download Error','Incorrect download method.'); return
	#try:		t=''
	#except: t=''

def DownloadStatus(numblocks, blocksize, filesize, dlg, download_method, start_time, section, url, img, LabelName, ext, LabelFile):
	if (CancelDownload==True):
		try:
			if   (download_method=='Progress'): ## For Frodo and earlier.
				dlg.close()
			elif (download_method=='ProgressBG'): ## Only works on daily build of XBMC.
				dlg.close()
			elif (download_method=='Test'): t=''
			elif (download_method=='Hidden'): t=''
		except: t=''
	try:
		percent = min(numblocks * blocksize * 100 / filesize, 100)
		currently_downloaded = float(numblocks) * blocksize / (1024 * 1024)
		kbps_speed = numblocks * blocksize / (time.time() - start_time)
		if kbps_speed > 0:	eta = (filesize - numblocks * blocksize) / kbps_speed
		else:								eta = 0
		kbps_speed /= 1024
		total = float(filesize) / (1024 * 1024)
		#if   (download_method=='Progress'): ## For Frodo and earlier.
		#	line1 = '%.02f MB of %.02f MB' % (currently_downloaded, total)
		#	line1 +='  '+percent+'%'
		#	line2 = 'Speed: %.02f Kb/s ' % kbps_speed
		#	line3 = 'ETA: %02d:%02d' % divmod(eta, 60)
		#	dlg.update(percent, line1, line2, line3)
		#elif (download_method=='ProgressBG'): ## Only works on daily build of XBMC.
		#	line1  ='%.02f MB of %.02f MB' % (currently_downloaded, total)
		#	line1 +='  '+percent+'%'
		#	line2  ='Speed: %.02f Kb/s ' % kbps_speed
		#	line2 +='ETA: %02d:%02d' % divmod(eta, 60)
		#	dlg.update(percent, line1, line2)
		#elif (download_method=='Test'):
		#	mbs = '%.02f MB of %.02f MB' % (currently_downloaded, total)
		#	spd = 'Speed: %.02f Kb/s ' % kbps_speed
		#	est = 'ETA: %02d:%02d' % divmod(eta, 60)
		#	Header=		ext+'  '+mbs+'  '+percent+'%'
		#	Message=	est+'  '+spd
		#elif (download_method=='Hidden'): t=''
		#if (time.time()==start_time) or (int(str(time.time())[-5:1]) == 0): # and (int(str(time.time())[-5:2]) < 10):
		#if (int(time.strptime(time.time(),fmt='%S')) == 0):
		#if (str(percent) in ['0','1','5','10','15','20','25','30','35','40','45','50','55','60','65','70','75','80','85','90','91','92','93','94','95','96','97','98','99','100']):
		#if (str(percent) == '0' or '1' or '5' or '10' or '15' or '20' or '25' or '30' or '35' or '40' or '45' or '50' or '55' or '60' or '65' or '70' or '75' or '80' or '85' or '90' or '91' or '92' or '93' or '94' or '95' or '96' or '97' or '98' or '99' or '100'):
		#if ('.' in str(percent)): pCheck=int(str(percent).split('.')[0])
		#else: pCheck=percent
		#pCheck=int(str(percent)[1:])
		#if (CurrentPercent is not pCheck):
		#	global CurrentPercent
		#	CurrentPercent=pCheck
		#	myNote(header=Header,msg=Message,delay=100,image=img)
		##myNote(header=Header,msg=Message,delay=1,image=img)
	except:
		percent=100
		if   (download_method=='Progress'): ## For Frodo and earlier.
			t=''
			dlg.update(percent)
		elif (download_method=='ProgressBG'): ## Only works on daily build of XBMC.
			t=''
			dlg.update(percent)
		elif (download_method=='Test'): t=''
		#myNote(header='100%',msg='Download Completed',delay=15000,image=img)
		elif (download_method=='Hidden'): t=''
	if   (download_method=='Progress'): ## For Frodo and earlier.
		line1 = '%.02f MB of %.02f MB' % (currently_downloaded, total)
		line1 +='  '+str(percent)+'%'
		line2 = 'Speed: %.02f Kb/s ' % kbps_speed
		line3 = 'ETA: %02d:%02d' % divmod(eta, 60)
		dlg.update(percent, line1, line2, line3)
	elif (download_method=='ProgressBG'): ## Only works on daily build of XBMC.
		line1  ='%.02f MB of %.02f MB' % (currently_downloaded, total)
		line1 +='  '+str(percent)+'%'
		line2  ='Speed: %.02f Kb/s ' % kbps_speed
		line2 +='ETA: %02d:%02d' % divmod(eta, 60)
		dlg.update(percent, line1, line2)
	elif (download_method=='Test'):
		mbs = '%.02f MB of %.02f MB' % (currently_downloaded, total)
		spd = 'Speed: %.02f Kb/s ' % kbps_speed
		est = 'ETA: %02d:%02d' % divmod(eta, 60)
		Header=		ext+'  '+mbs+'  '+str(percent)+'%'
		Message=	est+'  '+spd
	elif (download_method=='Hidden'): t=''
	if   (download_method=='Progress'): ## For Frodo and earlier.
		try:
			if dlg.iscanceled(): ## used for xbmcgui.DialogProgress() but causes an error with xbmcgui.DialogProgressBG()
				dlg.close()
				#deb('Download Error','Download canceled.'); myNote('Download Error','Download canceled.')
				#raise StopDownloading('Stopped Downloading')
		except: t=''
	elif (download_method=='ProgressBG'): ## Only works on daily build of XBMC.
		try:
			if (dlg.isFinished()): 
				dlg.close()
		except: t=''

def DownloadRequest(section,url,img,LabelName):
	if (LabelName=='') and     (_param['title'] is not ''): LabelName==_param['title']
	if (LabelName=='') and (_param['showtitle'] is not ''): LabelName==_param['showtitle']
	LabelFile=clean_filename(LabelName)
	deb('LabelName',LabelName)
	if (LabelName==''): deb('Download Error','Missing Filename String.'); myNote('Download Error','Missing Filename String.'); return
	if (section==ps('section.wallpaper')):	FolderDest=xbmc.translatePath(addst("download_folder_wallpapers"))
	elif (section==ps('section.tv')):				FolderDest=xbmc.translatePath(addst("download_folder_tv"))
	elif (section==ps('section.movie')):		FolderDest=xbmc.translatePath(addst("download_folder_movies"))
	else:																		FolderDest=xbmc.translatePath(addst("download_folder_movies"))
	if os.path.exists(FolderDest)==False: os.mkdir(FolderDest)
	if os.path.exists(FolderDest):
		if (section==ps('section.tv')) or (section==ps('section.movie')):
			### param >> url:  /link/show/1466546/
			#match=re.search( '/.+?/.+?/(.+?)/', url) ## Example: http://www.solarmovie.so/link/show/1052387/ ##
			#videoId=match.group(1); deb('Solar ID',videoId); url=BASE_URL + '/link/play/' + videoId + '/' ## Example: http://www.solarmovie.so/link/play/1052387/ ##
			#html=net.http_GET(url).content; match=re.search( '<iframe.+?src="(.+?)"', html, re.IGNORECASE | re.MULTILINE | re.DOTALL); link=match.group(1); link=link.replace('/embed/', '/file/'); deb('hoster link',link)
			#try: stream_url = urlresolver.HostedMediaFile(link).resolve()
			#except: stream_url=''
			stream_url=url
			if ('.mp4' in LabelName) or ('.mp4' in stream_url): ext='.mp4'
			elif ('.avi' in LabelName) or ('.avi' in stream_url): ext='.avi'
			elif ('.mkv' in LabelName) or ('.mkv' in stream_url): ext='.mkv'
			else: ext='.flv'
			ext=Download_PrepExt(stream_url,ext)
		else:
			stream_url=url
			if ('.png' in LabelName) or ('.png' in stream_url): ext='.png'
			else: ext='.jpg'
			ext=Download_PrepExt(stream_url,ext)
		t=1; c=1
		if os.path.isfile(xbmc.translatePath(os.path.join(FolderDest,LabelFile+ext))):
			t=LabelFile
			while t==LabelFile:
				if os.path.isfile(xbmc.translatePath(os.path.join(FolderDest,LabelFile+'['+str(c)+']'+ext)))==False:
					LabelFile=LabelFile+'['+str(c)+']'
				c=c+1
		start_time = time.time()
		deb('start_time',str(start_time))
		download_method=addst('download_method') ### 'Progress|ProgressBG|Hidden'
		urllib.urlcleanup()
		if   (download_method=='Progress'):
			dp=xbmcgui.DialogProgress(); dialogType=12 ## For Frodo and earlier.
			dp.create('Downloading', LabelFile+ext)
			urllib.urlretrieve(stream_url, xbmc.translatePath(os.path.join(FolderDest,LabelFile+ext)), lambda nb, bs, fs: DownloadStatus(nb, bs, fs, dp, download_method, start_time, section, url, img, LabelName, ext, LabelFile)) #urllib.urlretrieve(url, localfilewithpath)
			myNote('Download Complete',LabelFile+ext,15000)
		elif (download_method=='ProgressBG'):
			dp=xbmcgui.DialogProgressBG(); dialogType=13 ## Only works on daily build of XBMC.
			dp.create('Downloading', LabelFile+ext)
			urllib.urlretrieve(stream_url, xbmc.translatePath(os.path.join(FolderDest,LabelFile+ext)), lambda nb, bs, fs: DownloadStatus(nb, bs, fs, dp, download_method, start_time, section, url, img, LabelName, ext, LabelFile)) #urllib.urlretrieve(url, localfilewithpath)
			myNote('Download Complete',LabelFile+ext,15000)
		elif (download_method=='Test'):
			dp=xbmcgui.DialogProgress()
			myNote('Download Started',LabelFile+ext,15000)
			urllib.urlretrieve(stream_url, xbmc.translatePath(os.path.join(FolderDest,LabelFile+ext)), lambda nb, bs, fs: DownloadStatus(nb, bs, fs, dp, download_method, start_time, section, url, img, LabelName, ext, LabelFile)) #urllib.urlretrieve(url, localfilewithpath)
			myNote('Download Complete',LabelFile+ext,15000)
		elif (download_method=='Hidden'):
			dp=xbmcgui.DialogProgress()
			myNote('Download Started',LabelFile+ext,15000)
			urllib.urlretrieve(stream_url, xbmc.translatePath(os.path.join(FolderDest,LabelFile+ext)), lambda nb, bs, fs: DownloadStatus(nb, bs, fs, dp, download_method, start_time, section, url, img, LabelName, ext, LabelFile)) #urllib.urlretrieve(url, localfilewithpath)
			myNote('Download Complete',LabelFile+ext,15000)
		elif (download_method=='jDownloader (StreamURL)'):
			myNote('Download','sending to jDownloader plugin',15000)
			xbmc.executebuiltin("XBMC.RunPlugin(plugin://plugin.program.jdownloader/?action=addlink&url=%s)" % stream_url)
			#return
		elif (download_method=='jDownloader (Link)'):
			myNote('Download','sending to jDownloader plugin',15000)
			xbmc.executebuiltin("XBMC.RunPlugin(plugin://plugin.program.jdownloader/?action=addlink&url=%s)" % link)
			#return
		else: deb('Download Error','Incorrect download method.'); myNote('Download Error','Incorrect download method.'); return
		##
		##urllib.urlretrieve(stream_url, xbmc.translatePath(os.path.join(FolderDest,LabelFile+ext)), lambda nb, bs, fs: DownloadStatus(nb, bs, fs, dp, download_method, start_time, section, url, img, LabelName, ext, LabelFile)) #urllib.urlretrieve(url, localfilewithpath)
		##
		#myNote('Download Complete',LabelFile+ext,15000)
		##
		#### xbmc.translatePath(os.path.join(FolderDest,localfilewithpath+ext))
		_addon.resolve_url(url)
		_addon.resolve_url(stream_url)
		#
		#
	else:	deb('Download Error','Unable to create destination path.'); myNote('Download Error','Unable to create destination path.'); return

def PlayTrailer(url,_title,_year,_image): ### Not currently used ###
	WhereAmI('@ PlayVideo:  %s' % url) #; sources=[]; url=url.decode('base-64')
	#if ('<h2>Movie trailer</h2>' not in url): eod(); return
	EmbedID=''; html=net.http_GET(url).content #getURL(url)
	html=messupText(html,True,True,True,False)
	#print str(html)
	if ('traileraddict.com/emd/' in html):
		deb('Found','traileraddict.com/emd/')
		#EmbedID=re.compile('traileraddict.com/emd/(\d+)"', re.DOTALL).findall(html)[0].strip()
		try: 		EmbedID=re.compile('traileraddict.com/emd/(\d+)"', re.DOTALL).findall(html)[0].strip()
		except: EmbedID=''
	if (EmbedID==''):
		#print html
		#ImdbID=re.compile('<strong>IMDb ID:</strong>[\n]\s+<a href=".+?">(\d+)</a>"', re.MULTILINE | re.IGNORECASE | re.DOTALL).findall(html)[0].strip()
		try:		ImdbID=re.compile('%2Ftitle%2Ftt(\d+)%2F"', re.DOTALL).findall(html)[0].strip()
		except:	ImdbID=''
		if (ImdbID==''): eod(); deb('Error Playing Trailer','No Imdb ID.'); deadNote('Problem with the Trailer','Trailer is Unavailable.'); return
		deb('ImdbID',ImdbID)
		thtml=getURL('http://api.traileraddict.com/?imdb='+ImdbID)
		try: 		EmbedID=re.compile('"http://www.traileraddict.com/emd/([0-9]+)"', re.DOTALL).findall(thtml)[0].strip()
		except: EmbedID=''
	if (EmbedID==''): eod(); deb('Error Playing Trailer','No Embed Video ID.'); deadNote('Problem with the Trailer','Trailer is Unavailable.'); return
	deb('EmbedID',EmbedID)
	vhtml=getURL('http://www.traileraddict.com/fvar.php?tid='+EmbedID) #vhtml=getURL('http://www.traileraddict.com/fvarhd.php?tid='+EmbedID)
	#print vhtml
	if ('Error: Trailer is (Possibly Temporarily) Unavailable' in vhtml): deadNote('Problem with the Trailer','Trailer is Unavailable.'); return
	try:		thumb=re.compile('&image=(.+?)&', re.DOTALL).findall(vhtml)[0].strip()
	except:	thumb=_param['img']
	try: 		title=re.compile('&filmtitle=(.+?)&', re.DOTALL).findall(vhtml)[0].strip()
	except: title=_param['title']
	try: 			url=re.compile('&fileurl=(.+?)&', re.DOTALL).findall(vhtml)[0].strip()
	except: 
		try: 		url=re.compile('&fileurl=(.+?)[\n]\s+&', re.DOTALL).findall(vhtml)[0].strip()
		except: url=''
	if (url==''): eod(); deb('Error Playing Trailer','No Url was found from vhtml.'); deadNote('Problem with the Trailer','Trailer is Unavailable.'); return
	url=urllib.unquote_plus(url)
	deb('video',url)
	liz=xbmcgui.ListItem(_param['showtitle'], iconImage=thumb, thumbnailImage=_image)
	liz.setInfo( type="Video", infoLabels={ "Title": title, "Studio": _title+'  ('+_year+')' } )
	liz.setProperty("IsPlayable","true")
	play=xbmc.Player(GetPlayerCore()) ### xbmc.PLAYER_CORE_AUTO | xbmc.PLAYER_CORE_DVDPLAYER | xbmc.PLAYER_CORE_MPLAYER | xbmc.PLAYER_CORE_PAPLAYER
	play.play(url, liz)
	#liz.setPath(url)
	#xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, liz)
	_addon.resolve_url(url)
	#eod(); return

##### /\ ##### Player Functions #####
### ############################################################################################################
### ############################################################################################################
### ############################################################################################################
##### Weird, Stupid, or Plain up Annoying Functions. #####
def netURL(url): ### Doesn't seem to work.
	return net.http_GET(url).content
def remove_accents(input_str): ### Not even sure rather this one works or not.
	#nkfd_form = unicodedata.normalize('NFKD', unicode(input_str))
	#return u"".join([c for c in nkfd_form if not unicodedata.combining(c)])
	return input_str
##### /\ ##### Weird, Stupid, or Plain up Annoying Functions. #####
### ############################################################################################################
### ############################################################################################################
### ############################################################################################################
##### Menus #####
def mGetItemPage(url):
	deb('Fetching html from Url',url)
	try: html=net.http_GET(url).content
	except: html=''
	if (html=='') or (html=='none') or (html==None) or (html==False): return ''
	else:
		html=HTMLParser.HTMLParser().unescape(html); html=_addon.decode(html); html=_addon.unescape(html); html=ParseDescription(html); html=html.encode('ascii', 'ignore'); html=html.decode('iso-8859-1'); deb('Length of HTML fetched',str(len(html)))
	return html

def mdGetSplitFindGroup(html,ifTag='', parseTag='',startTag='',endTag=''): 
	if (ifTag=='') or (parseTag=='') or (startTag=='') or (endTag==''): return ''
	if (ifTag in html):
		html=(((html.split(startTag)[1])).split(endTag)[0]).strip()
		try: return re.compile(parseTag, re.MULTILINE | re.IGNORECASE | re.DOTALL).findall(html)
		except: return ''
	else: return ''

def listLinks(section, url, showtitle='', showyear=''): ### Menu for Listing Hosters (Host Sites of the actual Videos)
	WhereAmI('@ the Link List: %s' % url); sources=[]; listitem=xbmcgui.ListItem()
	if (url==''): return
	cookie_file=xbmc.translatePath(os.path.join(_addonPath,'temp.cache.txt'))
	#try: html=nURL(url)
	try: html=nURL(url,headers={'Referer':_domain_url},cookie_file=cookie_file,load_cookie=True)
	#try: html=net.http_GET(url).content
	except: html=''
	deb('length of html',str(len(html)))
	if (html==''): return
	try: html=html.encode("ascii", "ignore")
	except: t=''
	html=messupText(html,True,True,True,False)
	temp_file=xbmc.translatePath(os.path.join(_addonPath,'temp.html.links.txt'))
	if (_debugging==True) and (_testing==True):
		try: my_tools._SaveFile(temp_file,html)
		except: pass
	#
	##try: ## 
	#aLINKd=re.compile('<iframe .*?src="('+_domain_url+'/a'+'d'+'s/.*?)"').findall(html); debob(aLINKd); #deb('aLINKd',aLINKd); 
	#if len(aLINKd) > 0:
	#	for MaLINKdM in aLINKd:
	#		if (_domain_url not in MaLINKdM) and ('://' not in MaLINKdM): MaLINKdM=_domain_url+MaLINKdM
	#		t1a=nURL(MaLINKdM,headers={'Referer':url},cookie_file=cookie_file,load_cookie=True,save_cookie=True)
	#		deb('For Attempted Fix #2 - Fetching',MaLINKdM)
	##except: pass
	##
	#s='<img id="a'+'d'+'Check\d" src="(http://.+?.com/.*?.png\?id=\d+)"/>'
	#_mts=re.compile(s, re.DOTALL).findall(html); debob(_mts); 
	#for mts2 in _mts:
	#	try: t=nURL(mts2,headers={'Referer':url}); deb('For Attempted Fix #1 - Fetching',mts2); 
	#	except: pass
	###
	##s='<img .*?src="(.+?)"'
	##_mts3=re.compile(s, re.DOTALL).findall(html); debob(_mts3); 
	##for mts3 in _mts3:
	##	try: 
	##		if (_domain_url not in mts3) and ('://' not in mts3): mts3=_domain_url+mts3
	##		t=nURL(mts3,headers={'Referer':url}); deb('For Attempted Fix #3 - Fetching',mts3); 
	##	except: pass
	###
	#try: sTitle=re.compile('<head><title>\s*\n*\s*\n*\s*([0-9A-Za-z\s\n]+)\n*\s+-\s+Watch').findall(html)[0].replace('\n','').replace('\r','')
	#except: sTitle='Unknown'
	img=_param['img']
	if (img==''): img=re.compile('<meta\s*itemprop="thumbnailUrl"\s*content="(http://.+?\.jpg)"').findall(html)[0].replace(' ','%20')
	pimg=''+img; fimg=''+img; ptitle=_param['title']
	s='<a\s*\n*\s*target="_blank"\s*\n*\s*href="(http://redirector.googlevideo.com/videoplayback.+?)"\s*\n*\s*>((\d+)x(\d+)\.([0-9A-Za-z]+))</a>'
	#s='<a\s*\n*\s*href="(http://redirector.googlevideo.com/videoplayback.+?)"\s*\n*\s*>((\d+)x(\d+)\.([0-9A-Za-z]+))</a>'
	#s="%7C(http.+?redirector.googlevideo.com.+?%3fid%3d([A-Za-z0-9]+)%26itag%3d(((\d+)))%.+?)%7C"
	try: matches=re.compile(s, re.DOTALL).findall(html)
	except: matches=''
	debob(matches)
	try: contentURL=re.compile('<meta\s*itemprop="contentURL"\s*content="(http://.+?)"\s*/*>').findall(html)[0]
	except: contentURL=''
	try: fTitle=re.compile('<meta\s*itemprop="contentURL"\s*content="http://.+?(&title=.*?)"\s*/*>').findall(html)[0]
	except: fTitle=''
	if (tfalse(addst("enable-autoplay"))==True) and (addst("autoplay-select")=='Default'): #and (tfalse(addst("enable-autoplay2"))==False):
		play=xbmc.Player(GetPlayerCore())
		deb('LastAutoPlayItemUrl',addst("LastAutoPlayItemUrl"))
		deb('LastAutoPlayItemName',addst("LastAutoPlayItemName"))
		if (play.isPlayingVideo()==False):
			_addon.addon.setSetting(id="LastAutoPlayItemUrl", value=contentURL)
			_addon.addon.setSetting(id="LastAutoPlayItemName", value=ptitle)
			PlayVideo(contentURL, title='[Auto Play] Default URL', studio=ptitle, img=pimg, showtitle=showtitle,autoplay=True)
			xbmc.executebuiltin("XBMC.Container.Update(%s)" % _addon.build_plugin_url({'mode':'GetEpisodes','url':addst("LastShowListedURL"),'img':addst("LastShowListedIMG")}))
		else: myNote('A Video is currently playing.','Try stopping the current video first.')
		return
	### _addon.addon.setSetting(id="LastShowListedURL", value=url)
	### _addon.addon.setSetting(id="LastShowListedIMG", value=img)
	### xbmc.executebuiltin("XBMC.RunPlugin(%s)" % _addon.build_plugin_url({'mode':'GetTitles','url':url,'pageno':'1','pagecount':addst('pages')}))
	### xbmc.executebuiltin("XBMC.Container.Update(%s)" % _addon.build_plugin_url({'mode':'GetTitles','url':url,'pageno':'1','pagecount':addst('pages')}))
	#try: embedURL=re.compile("var\s+embedCode\s*=\s*'(http://.+?)'").findall(html)[0]
	#except: embedURL=''
	#try: testURL=re.compile("'(http://.+?)'").findall(html); print 'testURL1'; print testURL
	#except: testURL=''
	#try: testURL=re.compile('"(http://.+?)"').findall(html); print 'testURL2'; print testURL
	#except: testURL=''
	#try: testURL=re.compile('\n.+?(http://.+?)\n', re.DOTALL).findall(html); print 'testURL3'; print testURL
	#except: testURL=''
	#try: fmtURLs=re.compile('(\d+)%7C(http%3a%2f%2fredirector.googlevideo.com%2fvideoplayback%3fid%3d[0-9A-Za-z]+%26itag%3d(\d+)%26source%3d[0-9A-Za-z\-_]+%26cmo%3d[0-9A-Za-z\-_]+%3dyes%26ip%3d0.0.0.0%26ipbits%3d0%26expire%3d\d+%26sparams%3did%252Citag%252Csource%252Cip%252Cipbits%252Cexpire%26signature%3d[0-9A-Za-z]+\.[0-9A-Za-z]+%26key%3d[0-9A-Za-z]+)').findall(html)
	#except: fmtURLs=''
	# print 'testURL4'; print fmtURLs
	#
	#if (len(fmtURLs) > 0):
	#	count=1; ItemCount=len(fmtURLs); #match=sorted(match, key=lambda item: (item[3],item[2],item[1]))
	##	deb('No. of matches',str(ItemCount))
	#	#print matches
	#	MaxNoLinks=int(addst('linksmaxshown'))
	#	try: mmNames=re.compile('(\d+)%2F(\d+x\d+)').findall(html)
	#	except: mmNames=None
	#	for mID1,mUrl,mID2 in fmtURLs:
	#		mUrl=urllib.unquote_plus(mUrl)
	#		#mUrl=unescape_(mUrl)
	#		#deb('mUrl',mUrl)
	#		#try: mName=re.compile(mID1+'%2F(\d+x\d+)').findall(html)[0]+'-'+mID2
	#		#except: mName=''+mID1
	#		try: mName=mID2+'-['+mmNames[int(count-1)][1]+']-'+mmNames[int(count-1)][0]
	#		except: mName=''+mID1
	#		#if   (mFileExt.lower()=='mkv'): img=art('mkv') #'http://convertmkvtomp4.info/images/mkv.png'
	#		#elif (mFileExt.lower()=='mp4'): img=art('mp4') #'http://zamzar.files.wordpress.com/2013/03/mp4.png?w=480'
	#		#elif (mFileExt.lower()=='flv'): img=art('flv') #'http://images.wikia.com/fileformats/images/a/ab/Icon_FLV.png'
	#		contextMenuItems=[]; labs={}
	#		#if (fTitle not in mUrl): mUrl+=fTitle
	#		#if (fTitle not in mUrl): mUrl2=fTitle
	#		#else: mUrl2=''+mUrl
	#		pars={'img':pimg,'mode':'PlayVideo','url':mUrl,'title':mName,'studio':ptitle}
	#		#pars2={'img':pimg,'mode':'PlayVideo','url':mUrl2,'title':mName,'studio':ptitle}
	#		deb('gv redirector url',mUrl)
	#		##pars2={'img':img,'mode':'Download','url':url,'title':mName,'studio':ptitle}
	#		##contextMenuItems.append(('Download', 'XBMC.RunPlugin(%s)' % _addon.build_plugin_url(pars2)))
	#		##contextMenuItems.append(('jDownloader', ps('cMI.jDownloader.addlink.url') % (urllib.quote_plus(url))))
	#		labs['title']=''+mName #+'  (Testing)'
	#		_addon.add_directory(pars,labs,img=img,fanart=fimg,is_folder=False,contextmenu_items=contextMenuItems,total_items=ItemCount)
	#		#_addon.add_directory(pars2,labs,img=img,fanart=fimg,is_folder=False,contextmenu_items=contextMenuItems,total_items=ItemCount)
	#		count=count+1
	#if (len(embedURL) > 0):
	#	deb('embedURL',embedURL)
	#	contextMenuItems=[]; labs={}; labs['title']='[ Embed URL ]' +'  [I]<-- Play This One Only[/I]'
	#	pars={'img':pimg,'mode':'PlayVideo','url':embedURL,'title':'Default URL','studio':ptitle}
	#	_addon.add_directory(pars,labs,img=img,fanart=fimg,is_folder=False,contextmenu_items=contextMenuItems)
	#
	if (len(contentURL) > 0):
		deb('contentURL',contentURL)
		contextMenuItems=[]; labs={}; labs['title']='[ Default URL ]' #+'  [I]<-- Play This One[/I]' #
		pars={'img':pimg,'mode':'PlayVideo','url':contentURL,'title':'Default URL','studio':ptitle}
		_addon.add_directory(pars,labs,img=img,fanart=fimg,is_folder=False,contextmenu_items=contextMenuItems)
	if (len(matches) > 0):
		count=1; ItemCount=len(matches); #match=sorted(match, key=lambda item: (item[3],item[2],item[1]))
		deb('No. of matches',str(ItemCount))
		#print matches
		MaxNoLinks=int(addst('linksmaxshown'))
		if (tfalse(addst("enable-autoplay"))==True) and (addst("autoplay-select")=='Next'):
			play=xbmc.Player(GetPlayerCore())
			if (play.isPlayingVideo()==False):
				_addon.addon.setSetting(id="LastAutoPlayItemUrl", value=contentURL)
				_addon.addon.setSetting(id="LastAutoPlayItemName", value=ptitle)
				(mUrl,mName,mWidth,mHeight,mFileExt)=matches[0]
				PlayVideo(mUrl, title='[Auto Play] '+mName, studio=ptitle, img=pimg, showtitle=showtitle,autoplay=True)
				xbmc.executebuiltin("XBMC.Container.Update(%s)" % _addon.build_plugin_url({'mode':'GetEpisodes','url':addst("LastShowListedURL"),'img':addst("LastShowListedIMG")}))
			else: myNote('A Video is currently playing.','Try stopping the current video first.')
			return
		elif (tfalse(addst("enable-autoplay"))==True) and (addst("autoplay-select")=='Last'):
			play=xbmc.Player(GetPlayerCore())
			if (play.isPlayingVideo()==False):
				_addon.addon.setSetting(id="LastAutoPlayItemUrl", value=contentURL)
				_addon.addon.setSetting(id="LastAutoPlayItemName", value=ptitle)
				(mUrl,mName,mWidth,mHeight,mFileExt)=matches[-1]
				PlayVideo(mUrl, title='[Auto Play] '+mName, studio=ptitle, img=pimg, showtitle=showtitle,autoplay=True)
				xbmc.executebuiltin("XBMC.Container.Update(%s)" % _addon.build_plugin_url({'mode':'GetEpisodes','url':addst("LastShowListedURL"),'img':addst("LastShowListedIMG")}))
			else: myNote('A Video is currently playing.','Try stopping the current video first.')
			return
		for mUrl,mName,mWidth,mHeight,mFileExt in matches:
			#mUrl=urllib.unquote_plus(mUrl).replace('%2C',','); deb('unquoted url',mUrl)
			if   (mFileExt.lower()=='mkv'): img=art('mkv') #'http://convertmkvtomp4.info/images/mkv.png'
			elif (mFileExt.lower()=='mp4'): img=art('mp4') #'http://zamzar.files.wordpress.com/2013/03/mp4.png?w=480'
			elif (mFileExt.lower()=='flv'): img=art('flv') #'http://images.wikia.com/fileformats/images/a/ab/Icon_FLV.png'
			contextMenuItems=[]; labs={}
			#if (fTitle not in mUrl): mUrl+=fTitle
			pars={'img':pimg,'mode':'PlayVideo','url':mUrl,'title':mName,'studio':ptitle}
			parsDL={'img':pimg,'mode':'Download','section':ps('section.movie'),'url':mUrl,'title':ptitle+'-'+mName,'studio':ptitle+'-'+mName,'showtitle':ptitle+'-'+mName}
			deb('gv redirector url',mUrl)
			#pars2={'img':img,'mode':'Download','url':url,'title':mName,'studio':ptitle}
			contextMenuItems.append(('PlayURL', 'XBMC.RunPlugin(%s)' % _addon.build_plugin_url({'mode':'PlayURL','url':mUrl,'title':mName,'studio':ptitle,'img':pimg})))
			contextMenuItems.append(('Download', 'XBMC.RunPlugin(%s)' % _addon.build_plugin_url(parsDL)))
			contextMenuItems.append(('jDownloader', ps('cMI.jDownloader.addlink.url') % (urllib.quote_plus(mUrl))))
			labs['title']=''+mName #+'  (Testing)'
			if tfalse(addst("singleline"))==True: labs['title']=labs['title'].replace('[CR]',' ')
			if (tfalse(addst("enable-autoplay"))==True):
				if (addst("autoplay-select")==mName):
					play=xbmc.Player(GetPlayerCore())
					if (play.isPlayingVideo()==False):
						_addon.addon.setSetting(id="LastAutoPlayItemUrl", value=mUrl)
						_addon.addon.setSetting(id="LastAutoPlayItemName", value=ptitle)
						#(mUrl,mName,mWidth,mHeight,mFileExt)=matches[-1]
						debob([mUrl,mName,mWidth,mHeight,mFileExt]); 
						PlayVideo(mUrl, title='[Auto Play] '+mName, studio=ptitle, img=pimg, showtitle=showtitle,autoplay=True)
						xbmc.executebuiltin("XBMC.Container.Update(%s)" % _addon.build_plugin_url({'mode':'GetEpisodes','url':addst("LastShowListedURL"),'img':addst("LastShowListedIMG")}))
					else: myNote('A Video is currently playing.','Try stopping the current video first.')
					return
					###
			###
			try: _addon.add_directory(pars,labs,img=img,fanart=fimg,is_folder=False,contextmenu_items=contextMenuItems,total_items=ItemCount)
			except: pass
			count=count+1
	set_view(ps('content_links'),addst('links-view')); eod()
	### ################################################################


def Library_SaveTo_TV(section,url,img,name,year,country,season_number,episode_number,episode_title):
	##def listEpisodes(section, url, img='', season='') #_param['img']
	show_name=name
	xbmcplugin.setContent( int( sys.argv[1] ), 'episodes' ); WhereAmI('@ the Episodes List for TV Show -- url: %s' % url); html=net.http_GET(url).content
	if (html=='') or (html=='none') or (html==None):
		if (_debugging==True): print 'Html is empty.'
		return
	if (img==''):
		match=re.search( 'coverImage">.+?src="(.+?)"', html, re.IGNORECASE | re.MULTILINE | re.DOTALL); img=match.group(1)
	episodes=re.compile('<span class="epname">[\n].+?<a href="(.+?)"[\n]\s+title=".+?">(.+?)</a>[\n]\s+<a href="/.+?/season-(\d+)/episode-(\d+)/" class=".+?">[\n]\s+(\d+) links</a>', re.IGNORECASE | re.MULTILINE | re.DOTALL).findall(html) #; if (_debugging==True): print episodes
	if not episodes: 
		if (_debugging==True): print 'couldn\'t find episodes'
		return
	if (_param['thetvdb_series_id']=='') or (_param['thetvdb_series_id']=='none') or (_param['thetvdb_series_id']==None) or (_param['thetvdb_series_id']==False): thetvdb_episodes=None
	else: thetvdb_episodes=thetvdb_com_episodes2(_param['thetvdb_series_id'])
	#print 'thetvdb_episodes',thetvdb_episodes
	woot=False
	for ep_url, episode_name, season_number, episode_number, num_links in episodes:
		labs={}; s_no=season_number; e_no=episode_number
		if (int(episode_number) > -1) and (int(episode_number) < 10): episode_number='0'+episode_number
		labs['thumbnail']=img; labs['fanart']=_param['fanart']
		labs['EpisodeTitle']=episode_name #; labs['ShowTitle']=''
		labs['title']=season_number+'x'+episode_number+' - '+episode_name+'  [[I]'+num_links+' Links [/I]]'
		ep_url=_domain_url+ep_url; episode_name=messupText(episode_name,True,True,True,True)
		if (thetvdb_episodes==None) or (_param['thetvdb_series_id']==None) or (_param['thetvdb_series_id']==False) or (_param['thetvdb_series_id'] is not '') or (_param['thetvdb_series_id']=='none'): t=''
		if (thetvdb_episodes):
			for db_ep_url, db_sxe_no, db_ep_url2, db_ep_name, db_dateYear, db_dateMonth, db_dateDay, db_hasImage in thetvdb_episodes:
				db_ep_url=ps('meta.tv.domain')+db_ep_url
				db_ep_url2=ps('meta.tv.domain')+db_ep_url2
				if (db_sxe_no.strip()==(s_no+' x '+e_no)):
					if ('Episode #' in episode_name): episode_name=db_ep_name.strip()
					labs['Premeired']=labs['DateAired']=labs['Date']=db_dateYear+'-'+db_dateMonth+'-'+db_dateDay
					labs['year']=db_dateYear; labs['month']=db_dateMonth; labs['day']=db_dateDay
					(db_thumb,labs['thetvdb_series_id'],labs['thetvdb_episode_id']) = Episode__get_thumb(db_ep_url2.strip(),img)
					if (check_ifUrl_isHTML(db_thumb)==True): labs['thumbnail']=db_thumb
					labs['title']=cFL(season_number+cFL('x',ps('cFL_color4'))+episode_number,ps('cFL_color5'))+' - '+cFL(episode_name,ps('cFL_color4'))+cFL('  [[I]'+cFL(num_links+' Links ',ps('cFL_color3'))+'[/I]]',ps('cFL_color'))
					ep_html=mGetItemPage(db_ep_url2); deb('thetvdb - episode - url',db_ep_url2)
					deb('Length of ep_html',str(len(ep_html)))
					if (ep_html is not None) or (ep_html is not False) or (ep_html is not '') or (ep_html is not 'none'):
						labs['PlotOutline']=labs['plot']=mdGetTV(ep_html,['thetvdb.episode.overview1'])['thetvdb.episode.overview1']
		contextMenuItems=[]; labs['season']=season_number; labs['episode']=episode_number
		#contextMenuItems.append((ps('cMI.showinfo.name'),ps('cMI.showinfo.url')))
		#contextMenuItems.append(('Add - Library','XBMC.RunPlugin(%s?mode=%s&section=%s&title=%s&showtitle=%s&showyear=%s&url=%s&img=%s&season=%s&episode=%s&episodetitle=%s)' % ( sys.argv[0],'LibrarySaveEpisode',section, urllib.quote_plus(_param['title']), urllib.quote_plus(_param['showtitle']), urllib.quote_plus(_param['year']), urllib.quote_plus(ep_url), urllib.quote_plus(labs['thumbnail']), urllib.quote_plus(season_number), urllib.quote_plus(episode_number), urllib.quote_plus(episode_name) )))
		labs['title']=messupText(labs['title'],True,True,True,False)
		deb('Episode Name',labs['title'])
		deb('episode thumbnail',labs['thumbnail'])
		#
		Library_SaveTo_Episode(ep_url,labs['thumbnail'],show_name,year,country,season_number,episode_number,episode_name)
		### Library_SaveTo_Episode(url,iconimage,name,year,country,season_number,episode_number,episode_title)
		#
		#if (season==season_number) or (season==''): _addon.add_directory({'mode': 'GetLinks', 'year': _param['year'], 'section': section, 'img': img, 'url': ep_url, 'season': season_number, 'episode': episode_number, 'episodetitle': episode_name}, labs, img=labs['thumbnail'], fanart=labs['fanart'], contextmenu_items=contextMenuItems)
	set_view('episodes',ps('setview.episodes')); eod()

def Menu_BrowseByGenre(section=_default_section_):
	url=''; WhereAmI('@ the Genre Menu')#print 'Browse by genres screen'
	#browsebyImg=checkImgLocal(art('genre','.jpg'))
	ItemCount=len(GENRES)*4 # , total_items=ItemCount
	for genre in GENRES:
		gt=addst("genre-thumbs"); img=''; imgName=genre #; pre='http://icons.iconarchive.com/icons/sirubico/movie-genre/128/'
		#if (img==''): img=checkImgLocal(os.path.join(ps('special.home'),'addons','skin.primal','extras','moviegenresposter',imgName+'.jpg'))
		#if (img==''): img=checkImgLocal(os.path.join(ps('special.home'),'addons','skin.tangency','extras','moviegenresposter',imgName+'.jpg'))
		#if (img==''): img=checkImgLocal(os.path.join(ps('special.home'),'addons','plugin.video.1channel','art','themes','PrimeWire',imgName+'.png'))
		#if (img==''): img=checkImgLocal(os.path.join(ps('special.home'),'addons','plugin.video.1channel','art','themes','Glossy_Black',imgName+'.png'))
		#if (img=='') and (browsebyImg is not ''): img=browsebyImg
		#if (img==''): img=_artIcon
		if   (gt=='ArtSite'): img=psgn(genre.lower(),'.jpg')
		elif (gt=='ArtSiteSmall'): img=psgs(genre.lower(),'.jpg')
		elif (gt=='ArtSiteLarge'): img=psgsL(genre.lower(),'.jpg')
		elif (gt=='ArtFolderJpg') and (isFile(art('genre)'+genre.lower(),'.jpg'))==True): img=art('genre)'+genre.lower(),'.jpg')
		elif (gt=='ArtFolderPng') and (isFile(art('genre)'+genre.lower(),'.png'))==True): img=art('genre)'+genre.lower(),'.png')
		elif (gt=='icon.png'): img=_artIcon
		elif (gt=='sitelogo'): img=ps('img_kisslogo')
		elif (gt=='next'): img=ps('img_next')
		elif (gt=='prev'): img=ps('img_prev')
		elif (gt=='hot'): img=ps('img_hot')
		elif (gt=='updated'): img=ps('img_updated')
		elif (gt=='skin.primal'): img=checkImgLocal(os.path.join(ps('special.home'),'addons','skin.primal','extras','moviegenresposter',imgName+'.jpg'))
		elif (gt=='skin.tangency'): img=checkImgLocal(os.path.join(ps('special.home'),'addons','skin.tangency','extras','moviegenresposter',imgName+'.jpg'))
		elif (gt=='1ch.PrimeWire'): img=checkImgLocal(os.path.join(ps('special.home'),'addons','plugin.video.1channel','art','themes','PrimeWire',imgName+'.png'))
		elif (gt=='1ch.Glossy_Black'): img=checkImgLocal(os.path.join(ps('special.home'),'addons','plugin.video.1channel','art','themes','Glossy_Black',imgName+'.png'))
		elif (gt=='kiss.png'): img=art('kiss')
		elif (gt=='genre.jpg'): img=art('genre','.jpg')
		elif (gt=='turtle.jpg'): img=art('turtle','.jpg')
		elif (gt=='mkv.png'): img=art('mkv')
		elif (gt=='mp4.png'): img=art('mp4')
		elif (gt=='flv.png'): img=art('flv')
		#elif (gt==''): img=
		if (img==''): img=_artIcon
		_addon.add_directory({'mode': 'SelectSort','url': _domain_url+'/Genre/'+genre.replace(' ','-')},{'title':genre,'plot':ps('GENRES_Notes')[genre],'plotoutline':ps('GENRES_Notes')[genre]},img=img,fanart=_artFanart,total_items=ItemCount)
	set_view('tvshows',addst('genre-view')); eod()

def Select_Genre(url=''):
	if (url==''): url=_domain_url+'/'+ps('common_word')+'List'
	WhereAmI('@ the Select Genre Menu'); option_list=GENRES; r=askSelection(option_list,'Select Genre')
	#if   (r==0): Select_Sort(url+option_list[r].lower(),AZ='')
	if (r== -1): eod(); return
	else: Select_Sort(url+'/Genre/'+option_list[r].replace(' ','-'),AZ='')

def Select_Sort(url='',AZ='all'):
	if (url==''): url=_domain_url+'/'+ps('common_word')+'List'
	WhereAmI('@ the Select Sort Menu'); AZ=AZ.lower();
	option_list=['Alphabetical','Most Popular','Latest Update','New '+ps('common_word')]
	path_list  =['','/MostPopular','/LatestUpdate','/Newest']
	if (AZ=='') or (AZ=='all'): AZTag=''
	elif ('?' in url): AZTag='&c='+AZ
	else: AZTag='?c='+AZ
	pn='1'; pc=addst('pages'); ItemCount=4 #len(GENRES)
	_addon.add_directory({'mode':'GetTitles','url':url+''+AZTag,'pageno':pn,'pagecount':pc},{'title':'Alphabetical'},fanart=_artFanart,total_items=ItemCount,img=psgn('alphabetical','.jpg')) #,img=_artIcon #psgn('','.jpg')
	_addon.add_directory({'mode':'GetTitles','url':url+'/MostPopular'+AZTag,'pageno':pn,'pagecount':pc},{'title':'Most Popular'},fanart=_artFanart,total_items=ItemCount,img=psgn('most popular','.jpg')) #,img=ps('img_hot')
	_addon.add_directory({'mode':'GetTitles','url':url+'/LatestUpdate'+AZTag,'pageno':pn,'pagecount':pc},{'title':'Latest Update'},fanart=_artFanart,total_items=ItemCount,img=psgn('latest update','.jpg')) #,img=ps('img_updated')
	_addon.add_directory({'mode':'GetTitles','url':url+'/Newest'+AZTag,'pageno':pn,'pagecount':pc},{'title':'New '+ps('common_word')},fanart=_artFanart,total_items=ItemCount,img=psgn('new '+ps('common_word').lower(),'.jpg')) #,img=_artIcon
	set_view('list',addst('default-view')); eod()

def Select_AZ(url=''):
	if (url==''): url=_domain_url+'/'+ps('common_word')+'List'
	option_list=['All','0','A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z']
	WhereAmI('@ the Select AZ Menu')
	pn='1'; pc=addst('pages'); ItemCount=len(option_list)
	for oo in option_list:
		if (oo=='All'): ooo=''
		else: ooo=oo.lower()
		gt=addst("az-thumbs"); img='';
		if (gt=='ArtSite'): img=psgn(oo.lower(),'.jpg')
		if (gt=='ArtSiteSmall'): img=psgs(oo.lower(),'.jpg')
		if (gt=='ArtSiteLarge'): img=psgsL(oo.lower(),'.jpg')
		if (gt=='icon.png'): img=_artIcon
		if (gt=='sitelogo'): img=ps('img_kisslogo')
		if (gt=='next'): img=ps('img_next')
		if (gt=='prev'): img=ps('img_prev')
		if (gt=='hot'): img=ps('img_hot')
		if (gt=='updated'): img=ps('img_updated')
		if (gt=='kiss.png'): img=art('kiss')
		if (gt=='genre.jpg'): img=art('genre','.jpg')
		if (gt=='turtle.jpg'): img=art('turtle','.jpg')
		if (gt=='mkv.png'): img=art('mkv')
		if (gt=='mp4.png'): img=art('mp4')
		if (gt=='flv.png'): img=art('flv')
		if (gt=='chromatix.lower'): 
			if (oo=='all'):	img='http://icons.iconarchive.com/icons/chromatix/keyboard-keys/128/alt-icon.png'
			if (oo=='0'):		img='http://icons.iconarchive.com/icons/chromatix/keyboard-keys/128/hash-icon.png'
			else:						img='http://icons.iconarchive.com/icons/chromatix/keyboard-keys/128/letter-'+oo.lower()+'-icon.png'
		if (gt=='chromatix.upper'): 
			if (oo=='all'):	img='http://icons.iconarchive.com/icons/chromatix/keyboard-keys/128/alt-icon.png'
			if (oo=='0'):		img='http://icons.iconarchive.com/icons/chromatix/keyboard-keys/128/hash-icon.png'
			else:						img='http://icons.iconarchive.com/icons/chromatix/keyboard-keys/128/letter-uppercase-'+oo.upper()+'-icon.png'
		if (gt=='dooffy.lower'): 
			if (oo=='all'):	img='http://icons.iconarchive.com/icons/dooffy/characters/256/At-icon.png'
			if (oo=='0'):		img='http://icons.iconarchive.com/icons/dooffy/characters/256/0-Hash-icon.png'
			else:						img='http://icons.iconarchive.com/icons/dooffy/characters/256/'+oo.upper()+'1-icon.png'
		if (gt=='dooffy.upper'):
			if (oo=='all'):	img='http://icons.iconarchive.com/icons/dooffy/characters/256/At-icon.png'
			if (oo=='0'):		img='http://icons.iconarchive.com/icons/dooffy/characters/256/0-Hash-icon.png'
			else:						img='http://icons.iconarchive.com/icons/dooffy/characters/256/'+oo.upper()+'2-icon.png'
		if (gt=='balloon-green'):
			if (oo=='all'):	img='http://icons.iconarchive.com/icons/iconexpo/speech-balloon-green/256/speech-balloon-green-a-icon.png'
			if (oo=='0'):		img='http://icons.iconarchive.com/icons/iconexpo/speech-balloon-green/256/speech-balloon-green-o-icon.png'
			else:						img='http://icons.iconarchive.com/icons/iconexpo/speech-balloon-green/256/speech-balloon-green-'+oo.lower()+'-icon.png'
		if (gt=='balloon-orange'):
			if (oo=='all'):	img='http://icons.iconarchive.com/icons/iconexpo/speech-balloon-orange/256/speech-balloon-orange-a-icon.png'
			if (oo=='0'):		img='http://icons.iconarchive.com/icons/iconexpo/speech-balloon-orange/256/speech-balloon-orange-o-icon.png'
			else:						img='http://icons.iconarchive.com/icons/iconexpo/speech-balloon-orange/256/speech-balloon-orange-'+oo.lower()+'-icon.png'
		if (gt=='balloon-grey'):
			if (oo=='all'):	img='http://icons.iconarchive.com/icons/iconexpo/speech-balloon-grey/256/speech-balloon-white-a-icon.png'
			if (oo=='0'):		img='http://icons.iconarchive.com/icons/iconexpo/speech-balloon-grey/256/speech-balloon-white-o-icon.png'
			else:						img='http://icons.iconarchive.com/icons/iconexpo/speech-balloon-grey/256/speech-balloon-white-'+oo.lower()+'-icon.png'
		if (gt=='red-orb'):
			if (oo=='all'):	img='http://icons.iconarchive.com/icons/iconarchive/red-orb-alphabet/256/At-icon.png'
			if (oo=='0'):		img='http://icons.iconarchive.com/icons/iconarchive/red-orb-alphabet/256/Hash-icon.png'
			else:						img='http://icons.iconarchive.com/icons/iconarchive/red-orb-alphabet/256/Letter-A-icon.png'
		if (gt=='ariil.letter'):
			if (oo=='all'):	img='http://icons.iconarchive.com/icons/ariil/alphabet/256/Letter-A-icon.png'
			if (oo=='0'):		img='http://icons.iconarchive.com/icons/ariil/alphabet/256/Letter-O-icon.png'
			else:						img='http://icons.iconarchive.com/icons/ariil/alphabet/256/Letter-'+oo.upper()+'-icon.png'
		if (gt=='hydrattz.pink'):
			if (oo=='all'):	img='http://icons.iconarchive.com/icons/hydrattz/multipurpose-alphabet/256/Letter-A-pink-icon.png'
			if (oo=='0'):		img='http://icons.iconarchive.com/icons/hydrattz/multipurpose-alphabet/256/Letter-O-pink-icon.png'
			else:						img='http://icons.iconarchive.com/icons/hydrattz/multipurpose-alphabet/256/Letter-'+oo.upper()+'-pink-icon.png'
		if (gt=='hydrattz.blue'):
			if (oo=='all'):	img='http://icons.iconarchive.com/icons/hydrattz/multipurpose-alphabet/256/Letter-A-blue-icon.png'
			if (oo=='0'):		img='http://icons.iconarchive.com/icons/hydrattz/multipurpose-alphabet/256/Letter-O-blue-icon.png'
			else:						img='http://icons.iconarchive.com/icons/hydrattz/multipurpose-alphabet/256/Letter-'+oo.upper()+'-blue-icon.png'
		if (gt=='hydrattz.gold'):
			if (oo=='all'):	img='http://icons.iconarchive.com/icons/hydrattz/multipurpose-alphabet/256/Letter-A-blue-icon.png'
			if (oo=='0'):		img='http://icons.iconarchive.com/icons/hydrattz/multipurpose-alphabet/256/Letter-O-blue-icon.png'
			else:						img='http://icons.iconarchive.com/icons/hydrattz/multipurpose-alphabet/256/Letter-'+oo.upper()+'-blue-icon.png'
		if (gt=='hydrattz.red'):
			if (oo=='all'):	img='http://icons.iconarchive.com/icons/hydrattz/multipurpose-alphabet/256/Letter-A-red-icon.png'
			if (oo=='0'):		img='http://icons.iconarchive.com/icons/hydrattz/multipurpose-alphabet/256/Letter-O-red-icon.png'
			else:						img='http://icons.iconarchive.com/icons/hydrattz/multipurpose-alphabet/256/Letter-'+oo.upper()+'-red-icon.png'
		if (gt=='hydrattz.black'):
			if (oo=='all'):	img='http://icons.iconarchive.com/icons/hydrattz/multipurpose-alphabet/256/Letter-A-black-icon.png'
			if (oo=='0'):		img='http://icons.iconarchive.com/icons/hydrattz/multipurpose-alphabet/256/Letter-O-black-icon.png'
			else:						img='http://icons.iconarchive.com/icons/hydrattz/multipurpose-alphabet/256/Letter-'+oo.upper()+'-black-icon.png'
		if (gt=='hydrattz.grey'):
			if (oo=='all'):	img='http://icons.iconarchive.com/icons/hydrattz/multipurpose-alphabet/256/Letter-A-blue-grey.png'
			if (oo=='0'):		img='http://icons.iconarchive.com/icons/hydrattz/multipurpose-alphabet/256/Letter-O-blue-grey.png'
			else:						img='http://icons.iconarchive.com/icons/hydrattz/multipurpose-alphabet/256/Letter-'+oo.upper()+'-grey-icon.png'
		if (gt=='hydrattz.lg'):
			if (oo=='all'):	img='http://icons.iconarchive.com/icons/hydrattz/multipurpose-alphabet/256/Letter-A-lg-icon.png'
			if (oo=='0'):		img='http://icons.iconarchive.com/icons/hydrattz/multipurpose-alphabet/256/Letter-O-lg-icon.png'
			else:						img='http://icons.iconarchive.com/icons/hydrattz/multipurpose-alphabet/256/Letter-'+oo.upper()+'-lg-icon.png'
		if (gt=='hydrattz.dg'):
			if (oo=='all'):	img='http://icons.iconarchive.com/icons/hydrattz/multipurpose-alphabet/256/Letter-A-dg-icon.png'
			if (oo=='0'):		img='http://icons.iconarchive.com/icons/hydrattz/multipurpose-alphabet/256/Letter-O-dg-icon.png'
			else:						img='http://icons.iconarchive.com/icons/hydrattz/multipurpose-alphabet/256/Letter-'+oo.upper()+'-dg-icon.png'
		if (gt=='hydrattz.violet'):
			if (oo=='all'):	img='http://icons.iconarchive.com/icons/hydrattz/multipurpose-alphabet/256/Letter-A-violet-icon.png'
			if (oo=='0'):		img='http://icons.iconarchive.com/icons/hydrattz/multipurpose-alphabet/256/Letter-O-violet-icon.png'
			else:						img='http://icons.iconarchive.com/icons/hydrattz/multipurpose-alphabet/256/Letter-'+oo.upper()+'-violet-icon.png'
		if (gt=='hydrattz.orange'):
			if (oo=='all'):	img='http://icons.iconarchive.com/icons/hydrattz/multipurpose-alphabet/256/Letter-A-orange-icon.png'
			if (oo=='0'):		img='http://icons.iconarchive.com/icons/hydrattz/multipurpose-alphabet/256/Letter-O-orange-icon.png'
			else:						img='http://icons.iconarchive.com/icons/hydrattz/multipurpose-alphabet/256/Letter-'+oo.upper()+'-orange-icon.png'
		if (gt=='mattahan'):
			if (oo=='all'):	img='http://icons.iconarchive.com/icons/mattahan/umicons/256/Letter-A-icon.png'
			if (oo=='0'):		img='http://icons.iconarchive.com/icons/mattahan/umicons/256/Number-9-icon.png'
			else:						img='http://icons.iconarchive.com/icons/mattahan/umicons/256/Letter-'+oo.upper()+'-icon.png'
		#if (gt==''):
		#	if (oo=='all'):	img=''
		#	if (oo=='0'):		img=''
		#	else:						img=''
		#if (gt==''): img=''
		#if (gt==''): img=
		if (img==''): img=_artIcon
		_addon.add_directory({'mode':'SelectSort','url':url,'title':ooo,'pageno':pn,'pagecount':pc},{'title':oo},img=img,fanart=_artFanart,total_items=ItemCount)
	set_view('list',addst('default-view')); eod()

def _DoGetItems(url): 
	#xbmc.executebuiltin("XBMC.RunPlugin(%s)" % _addon.build_plugin_url({'mode':'GetTitles','url':url,'pageno':'1','pagecount':addst('pages')}))
	xbmc.executebuiltin("XBMC.Container.Update(%s)" % _addon.build_plugin_url({'mode':'GetTitles','url':url,'pageno':'1','pagecount':addst('pages')}))
	#listItems('',url,'1',addst('pages'))

def Bookmarks(section,url='',urlR=_domain_url):
	if (url==''): return
	if (urlR==''): urlR=_domain_url
	WhereAmI('@ the Bookmark Add/Remove -- url: %s' % url)
	cookie_file=xbmc.translatePath(os.path.join(_addonPath,'temp.cache.txt'))
	_T__F_=my_tools.KA_Login()
	if _T__F_==False: deadNote('Users Account','Login may have failed.'); eod(); return
	#try: 
	if isFile(cookie_file)==True: html=nURL(url,method='post',form_data={},headers={'Referer':urlR},cookie_file=cookie_file,load_cookie=True,save_cookie=True)
	else: html=nURL(url,method='post',form_data={},headers={'Referer':urlR},cookie_file=cookie_file,save_cookie=True)
	#	##if isFile(cookie_file)==True: html=nURL(url,headers={'Referer':_domain_url},proxy=Proxy,cookie_file=cookie_file,load_cookie=True,save_cookie=True)
	#	##else: html=nURL(url,headers={'Referer':_domain_url},proxy=Proxy,cookie_file=cookie_file,save_cookie=True)
	#except: html=''
	html=messupText(html,_html=True,_ende=True,_a=False,Slashes=False)
	temp_file=xbmc.translatePath(os.path.join(_addonPath,'temp.html.bookmarks.AR.txt'))
	if (_debugging==True) and (_testing==True):
		try: my_tools._SaveFile(temp_file,html)
		except: pass
	eod(); 
	return
	xbmc.executebuiltin("XBMC.Container.Refresh"); 

def listBookmarks(section,url=''):
	if (url==''): return
	WhereAmI('@ the Bookmark List -- url: %s' % url)
	cookie_file=xbmc.translatePath(os.path.join(_addonPath,'temp.cache.txt'))
	_T__F_=my_tools.KA_Login()
	if _T__F_==False: deadNote('Users Account','Login may have failed.'); eod(); return
	try: 
		#html=my_tools._OpenFile(xbmc.translatePath(os.path.join(_addonPath,'temp.html.test.txt')))
		if isFile(cookie_file)==True: html=nURL(url,headers={'Referer':_domain_url},cookie_file=cookie_file,load_cookie=True,save_cookie=True)
		#if isFile(cookie_file)==True: html=nURL(url,headers={'Referer':_domain_url},proxy=Proxy,cookie_file=cookie_file,load_cookie=True,save_cookie=True)
		else: html=nURL(url,headers={'Referer':_domain_url},cookie_file=cookie_file,save_cookie=True)
		#else: html=nURL(url,headers={'Referer':_domain_url},proxy=Proxy,cookie_file=cookie_file,save_cookie=True)
	except: html=''
	#listItems(section, _param['url'], _param['pageno'], addst('pages'), _param['genre'], _param['year'], _param['title'])
	if len(html)==0: debob('no html was found'); eod(); return;
	html=nolines(html)
	html=messupText(html,_html=True,_ende=True,_a=False,Slashes=False)
	#debob(html); 
	temp_file=xbmc.translatePath(os.path.join(_addonPath,'temp.html.bookmarks.txt'))
	if (_debugging==True) and (_testing==True):
		try: my_tools._SaveFile(temp_file,html)
		except: pass
	#s='<a\s*class="\D+"\s*href="(/'+ps('common_word')+'/[A-Za-z0-9\-/_]+)"\n*\s*title=\'(.*?)\'\n*\s*>\s*\n*\s*(.+?)\s*\n*\s*</a>\s*\n*\s*\n*\s*(.*?)\s*\n*\s*\n*\s*</td>\s*\n*\s*<td>\s*\n*\s*(.+?)\s*\n*\s*</td>'
	#s='<tr\s*>\s*<td title=\'(.*?)\'\s*>\s*<a\s*class="\D+"\s*href="(/'+ps('common_word')+'/.+?)"\s*>\s*(.+?)\s*</a\s*>\s*(.*?)\s*</td\s*>\s*<td\s*>\s*(.+?)\s*</td\s*>'
	s='<td title=\'(.*?)\'\s*>\s*<a\s*class="\D+"\s*href="(/'+ps('common_word')+'/.+?)"\s*>\s*(.+?)\s*</a\s*>\s*(.*?)\s*</td\s*>\s*<td\s*>\s*(.+?)\s*</td\s*>'
	#<a class="aAnime" href="/Anime/Bakuman-2">Bakuman. 2</a ></td ><td>Completed</td >
	iitems=re.compile(s, re.DOTALL).findall(html) ### , re.MULTILINE | re.IGNORECASE | re.DOTALL
	if (iitems is not None):
		ItemCount=len(iitems) # , total_items=ItemCount
		deb('# of items',str(ItemCount)); debob(iitems); 
		EnableMeta=tfalse(addst("enableMeta"))
		#for item_url, tInfo, name in iitems:
		#for item_url, tInfo, name, imInfo, LInfo in iitems:
		for tInfo, item_url, name, imInfo, LInfo in iitems:
			contextMenuItems=[]; item_url=_domain_url+item_url; labs={}; LInfo=LInfo.strip()
			#labs['title']=name
			try: img=re.compile('"(http://.+?\.jpg)"').findall(tInfo)[0].replace(' ','%20')
			except: img=_artIcon
			fimg=''+img
			if ('<p>' in tInfo) and ('</p>' in tInfo):
				try: labs['plot']=re.compile('<p>\s*\n*\s*(.+?)\s*\n*\s*</p>').findall(tInfo)[0].strip()
				except: labs['plot']=''
			else: labs['plot']=''
			if (tfalse(addst("Notyetaired"))==False) and (LInfo=='Not yet aired'): deb(LInfo,name)
			else: 
				labs['title']=name.replace(' (Dub)',' [COLOR green](Dub)[/COLOR]').replace(' (Sub)',' [COLOR blue](Sub)[/COLOR]').replace(' OVA',' [COLOR red]OVA[/COLOR]').replace(' Movie',' [COLOR maroon]Movie[/COLOR]').replace(': ',':[CR] ').replace(' New',' [COLOR yellow]New[/COLOR]').replace(' (TV)',' [COLOR cornflowerblue](TV)[/COLOR]').replace(' Specials',' [COLOR deeppink]Specials[/COLOR]') #.replace('','')
				deb('title',labs['title']); deb('url',item_url); deb('img',img); deb('fanart',fimg)
				#deb('plot',labs['plot']); 
				if ('</a>' in LInfo):
					deb('LInfo',LInfo)
					(LatestUrl,LatestName)=re.compile('<a href="(/'+ps('common_word')+'/.+?)">\s*\n*\s*(.+?)\s*\n*\s*</a>').findall(LInfo)[0]
					LatestUrl=_domain_url+LatestUrl
					LatestPar={'url':LatestUrl,'mode':'GetLinks','img':img,'fanart':fimg,'title':labs['title'].replace('[CR]','')+' - '+LatestName}
					contextMenuItems.append(('Latest:  '+LatestName,'XBMC.Container.Update(%s)' % _addon.build_plugin_url(LatestPar) ))
					#pars={'mode':'GetLinks','img':img,'url':ep_url,'title':ep_name}
					#contextMenuItems.append((ps('cMI.favorites.tv.add.name')+' '+addst('fav.movies.1.name'),ps('cMI.favorites.movie.add.url') % (sys.argv[0],ps('cMI.favorites.tv.add.mode'),section,urllib.quote_plus(name),'',urllib.quote_plus(img),urllib.quote_plus(fimg),urllib.quote_plus(''),urllib.quote_plus(labs['plot']),urllib.quote_plus(''),urllib.quote_plus(item_url), '' )))
				##### Right Click Menu for: Anime #####
				contextMenuItems.append((ps('cMI.showinfo.name'),ps('cMI.showinfo.url')))
				contextMenuItems.append((ps('cMI.favorites.tv.add.name')+' '+addst('fav.movies.1.name'),ps('cMI.favorites.movie.add.url') % (sys.argv[0],ps('cMI.favorites.tv.add.mode'),section,urllib.quote_plus(name),'',urllib.quote_plus(img),urllib.quote_plus(fimg),urllib.quote_plus(''),urllib.quote_plus(labs['plot']),urllib.quote_plus(''),urllib.quote_plus(item_url), '' )))
				if (tfalse(addst("enable-fav-movies-2"))==True): contextMenuItems.append((ps('cMI.favorites.tv.add.name')+' '+addst('fav.movies.2.name'),ps('cMI.favorites.movie.add.url') % (sys.argv[0],ps('cMI.favorites.tv.add.mode'),section,urllib.quote_plus(name),'',urllib.quote_plus(img),urllib.quote_plus(fimg),urllib.quote_plus(''),urllib.quote_plus(labs['plot']),urllib.quote_plus(''),urllib.quote_plus(item_url),'2' )))
				if (tfalse(addst("enable-fav-movies-3"))==True): contextMenuItems.append((ps('cMI.favorites.tv.add.name')+' '+addst('fav.movies.3.name'),ps('cMI.favorites.movie.add.url') % (sys.argv[0],ps('cMI.favorites.tv.add.mode'),section,urllib.quote_plus(name),'',urllib.quote_plus(img),urllib.quote_plus(fimg),urllib.quote_plus(''),urllib.quote_plus(labs['plot']),urllib.quote_plus(''),urllib.quote_plus(item_url),'3' )))
				if (tfalse(addst("enable-fav-movies-4"))==True): contextMenuItems.append((ps('cMI.favorites.tv.add.name')+' '+addst('fav.movies.4.name'),ps('cMI.favorites.movie.add.url') % (sys.argv[0],ps('cMI.favorites.tv.add.mode'),section,urllib.quote_plus(name),'',urllib.quote_plus(img),urllib.quote_plus(fimg),urllib.quote_plus(''),urllib.quote_plus(labs['plot']),urllib.quote_plus(''),urllib.quote_plus(item_url),'4' )))
				##if (labs['fanart'] is not ''): contextMenuItems.append(('Download Wallpaper', 'XBMC.RunPlugin(%s)' % _addon.build_plugin_url( { 'mode': 'Download' , 'section': ps('section.wallpaper') , 'studio': name+'  ('+year+')' , 'img': labs['thumbnail'] , 'url': labs['fanart'] } ) ))
				##contextMenuItems.append(('Add - Library','XBMC.RunPlugin(%s?mode=%s&section=%s&title=%s&showtitle=%s&showyear=%s&url=%s&img=%s)' % ( sys.argv[0],'LibrarySaveMovie',section, urllib.quote_plus(name), urllib.quote_plus(name), urllib.quote_plus(year), urllib.quote_plus(_domain_url+item_url), urllib.quote_plus(thumbnail))))
				##if os.path.exists(xbmc.translatePath(ps('special.home.addons'))+ps('cMI.1ch.search.folder')):
				##	contextMenuItems.append((ps('cMI.1ch.search.name'), 					ps('cMI.1ch.search.url') 				% (ps('cMI.1ch.search.plugin'), 			ps('cMI.1ch.search.section'), 			name)))
				##if os.path.exists(xbmc.translatePath(ps('special.home.addons'))+ps('cMI.primewire.search.folder')):
				##	contextMenuItems.append((ps('cMI.primewire.search.name'), 		ps('cMI.primewire.search.url') 	% (ps('cMI.primewire.search.plugin'), ps('cMI.primewire.search.section'), name)))
				##### Right Click Menu for: Anime ##### /\ #####
				pars={'mode':'GetEpisodes','url':item_url,'img':img,'title':labs['title']}
				if tfalse(addst("singleline"))==True: labs['title']=labs['title'].replace('[CR]',' ')
				try: _addon.add_directory(pars, labs, img=img, fanart=fimg, contextmenu_items=contextMenuItems, total_items=ItemCount)
				except: pass
	else: deb('Error','no items found.')
	set_view(ps('content_tvshows'),addst('anime-view')); eod(); return

def listItems(section=_default_section_, url='', startPage='1', numOfPages='1', genre='', year='', stitle='', season='', episode='', html='', chck=''): # List: Movies or TV Shows
	if (url==''): return
	#if (chck=='Latest'): url=url+chr(35)+'latest'
	WhereAmI('@ the Item List -- url: %s' % url)
	if (tfalse(addst('customproxy','false'))==True) and (len(addst('proxy','')) > 9): Proxy=addst('proxy','')
	else: Proxy="" #ps('proxy')
	start=int(startPage); end=(start+int(numOfPages)); html=''; html_last=''; nextpage=startPage; deb('page start',str(start)); deb('page end',str(end))
	cookie_file=xbmc.translatePath(os.path.join(_addonPath,'temp.cache.txt'))
	try: 
		if isFile(cookie_file)==True: html_=nURL(url,headers={'Referer':_domain_url},cookie_file=cookie_file,load_cookie=True,save_cookie=True)
		else: html_=nURL(url,headers={'Referer':_domain_url},proxy=Proxy,cookie_file=cookie_file,save_cookie=True)
	except: html_=''
	if (html_=='') or (html_=='none') or (html_==None): 
		deb('Error','Problem with page'); deadNote('Results:  '+section,'No results were found.')
		return
	deb('length of html_',str(len(html_))); 
	try:		last=int(re.compile('<li><a href="http://.+?page=\d+">(\d+)</a></li>\*s\n*\s*<li><a href="http://.+?page=\d+">&rsaquo;\s*Next\s*</a></li>').findall(html_))[0]
	except:	last=2
	deb('number of pages',str(last))
	if ('<h1>Nothing was found by your request</h1>' in html_): deadNote('Results:  '+section,'Nothing was found by your request'); eod(); return
	pmatch=re.findall(ps('LI.page.find'), html_)
	if pmatch: last=pmatch[-1]
	if ('?' in url):	urlSplitter='&page='; deb('urlSplitter',urlSplitter) ## Quick fix for urls that already have '?' in it.
	else:							urlSplitter='?page='; deb('urlSplitter',urlSplitter)
	for page in range(start,min(last,end)):
		if (int(page)> 1): #if (int(startPage)> 1):
			if ('&page=' in url): pageUrl=url.replace('&page=','&pagenull=')+'&page='+str(page) ## Quick fix.
			if ('?page=' in url): pageUrl=url.replace('?page=','?pagenull=')+'&page='+str(page) ## Quick fix.
			else: pageUrl=url+urlSplitter+str(page) #ps('LI.page.param')+startPage
		else: pageUrl=url
		deb('item listings for',pageUrl)
		try: 
			try: 
				if isFile(cookie_file)==True: html_last=nURL(pageUrl,headers={'Referer':_domain_url},proxy=Proxy,cookie_file=cookie_file,load_cookie=True,save_cookie=True)
				else: html_last=nURL(pageUrl,headers={'Referer':_domain_url},proxy=Proxy,cookie_file=cookie_file,save_cookie=True)
			except: 
				try:
					if isFile(cookie_file)==True: html=nURL(url,headers={'Referer':_domain_url},proxy=Proxy,cookie_file=cookie_file,load_cookie=True,save_cookie=True)
					else: html=nURL(url,headers={'Referer':_domain_url},proxy=Proxy,cookie_file=cookie_file,save_cookie=True)
				except: t=''
			if (_shoDebugging==True) and (html_last==''): deadNote('Testing','html_last is empty')
			if (html_last in html): t=''
			else: html=html+'\r\n'+html_last; deb('length of html_last',str(len(html_last))); 
			##if (_debugging==True): print html_last
		except: t=''
	if ' Last </a></li>' in html_last:
		LPurl=html_last.replace('&raquo;','').split(' Last </a></li>')[0].split('<li><a href="')[-1].split('"')[0]; LPnum=LPurl.split('page=')[-1]
		try: LPnum=LPnum.split('&')[0]
		except: pass
	else: LPurl=''; LPnum=startPage; 
	if (int(startPage) > 2): 
		try: _addon.add_directory({'mode': 'GetTitles', 'section': section, 'url': url, 'pageno': '1', 'pagecount': numOfPages}, {'title': addst("text-page-first","[COLOR goldenrod]  <<  [COLOR red]First[/COLOR]...[/COLOR][COLOR blue] 1[/COLOR]")}, img=ps('img_prev'))
		except: pass
	if (int(startPage) > 11): i=10; _addon.add_directory({'mode': 'GetTitles', 'section': section, 'url': url, 'pageno': str(i), 'pagecount': numOfPages}, {'title': addst("text-page-back-to","[COLOR goldenrod]  <<  [COLOR red][/COLOR]...[/COLOR][COLOR blue] %s[/COLOR]") % str(i)}, img=ps('img_prev'))
	if (int(startPage) > 21): i=20; _addon.add_directory({'mode': 'GetTitles', 'section': section, 'url': url, 'pageno': str(i), 'pagecount': numOfPages}, {'title': addst("text-page-back-to","[COLOR goldenrod]  <<  [COLOR red][/COLOR]...[/COLOR][COLOR blue] %s[/COLOR]") % str(i)}, img=ps('img_prev'))
	if (int(startPage) > 31): i=30; _addon.add_directory({'mode': 'GetTitles', 'section': section, 'url': url, 'pageno': str(i), 'pagecount': numOfPages}, {'title': addst("text-page-back-to","[COLOR goldenrod]  <<  [COLOR red][/COLOR]...[/COLOR][COLOR blue] %s[/COLOR]") % str(i)}, img=ps('img_prev'))
	if (int(startPage) > 41): i=40; _addon.add_directory({'mode': 'GetTitles', 'section': section, 'url': url, 'pageno': str(i), 'pagecount': numOfPages}, {'title': addst("text-page-back-to","[COLOR goldenrod]  <<  [COLOR red][/COLOR]...[/COLOR][COLOR blue] %s[/COLOR]") % str(i)}, img=ps('img_prev'))
	if (int(startPage) > 51): i=50; _addon.add_directory({'mode': 'GetTitles', 'section': section, 'url': url, 'pageno': str(i), 'pagecount': numOfPages}, {'title': addst("text-page-back-to","[COLOR goldenrod]  <<  [COLOR red][/COLOR]...[/COLOR][COLOR blue] %s[/COLOR]") % str(i)}, img=ps('img_prev'))
	if (int(startPage) > 61): i=60; _addon.add_directory({'mode': 'GetTitles', 'section': section, 'url': url, 'pageno': str(i), 'pagecount': numOfPages}, {'title': addst("text-page-back-to","[COLOR goldenrod]  <<  [COLOR red][/COLOR]...[/COLOR][COLOR blue] %s[/COLOR]") % str(i)}, img=ps('img_prev'))
	if (int(startPage) > 71): i=70; _addon.add_directory({'mode': 'GetTitles', 'section': section, 'url': url, 'pageno': str(i), 'pagecount': numOfPages}, {'title': addst("text-page-back-to","[COLOR goldenrod]  <<  [COLOR red][/COLOR]...[/COLOR][COLOR blue] %s[/COLOR]") % str(i)}, img=ps('img_prev'))
	if (int(startPage) > 81): i=80; _addon.add_directory({'mode': 'GetTitles', 'section': section, 'url': url, 'pageno': str(i), 'pagecount': numOfPages}, {'title': addst("text-page-back-to","[COLOR goldenrod]  <<  [COLOR red][/COLOR]...[/COLOR][COLOR blue] %s[/COLOR]") % str(i)}, img=ps('img_prev'))
	if (int(startPage) > 91): i=90; _addon.add_directory({'mode': 'GetTitles', 'section': section, 'url': url, 'pageno': str(i), 'pagecount': numOfPages}, {'title': addst("text-page-back-to","[COLOR goldenrod]  <<  [COLOR red][/COLOR]...[/COLOR][COLOR blue] %s[/COLOR]") % str(i)}, img=ps('img_prev'))
	if (int(startPage) > 1): 
		try: _addon.add_directory({'mode': 'GetTitles', 'section': section, 'url': url, 'pageno': str(int(startPage)-1), 'pagecount': numOfPages}, {'title': addst("text-page-prev","[COLOR goldenrod]  <  [COLOR red]Previous[/COLOR]...[/COLOR][COLOR blue] %s[/COLOR]") % str(int(startPage)-1)}, img=ps('img_prev'))
		except: pass
	###	### _addon.add_directory({'mode': 'GetTitles', 'url': url, 'startPage': str(end), 'numOfPages': numOfPages}, {'title': 'Next...'})
	###html=nolines(html)
	html=ParseDescription(html); html=remove_accents(html) #if (_debugging==True): print html
	html=messupText(html,_html=True,_ende=True,_a=False,Slashes=False)
	deb('Length of HTML',str(len(html))); #debob(html); 
	temp_file=xbmc.translatePath(os.path.join(_addonPath,'temp.html.items.txt'))
	if (_debugging==True) and (_testing==True):
		try: my_tools._SaveFile(temp_file,html)
		except: pass
	######
	if (len(html)==0): deb('Error','html is empty.'); return
	##s='<a\n*\s*href="(/'+ps('common_word')+'/[A-Za-z0-9\-/_]+)"\n*\s*title=\'(.*?)\'\n*\s*[/]*>\s*\n*\s*(.+?)\s*\n*\s*</a>\s*\n*\s*\n*\s*(.*?)\s*\n*\s*\n*\s*</td>\s*\n*\s*<td>\s*\n*\s*(.+?)\s*\n*\s*</td>\s*\n*\s*</tr>'; 
	#s='<a\n*\s*href="(/'+ps('common_word')+'/[A-Za-z0-9\-/_]+)"\n*\s*title=\'(.*?)\'\n*\s*[/]*>\s*\n*\s*(.+?)\s*\n*\s*</a>\s*\n*\s*\n*\s*(.*?)\s*\n*\s*\n*\s*</td>\s*\n*\s*<td>\s*\n*\s*(.+?)\s*\n*\s*</td>\s*\n*\s*</tr>'; 
	s='<td title=\'(.*?)\'\n*\s*[/]*>\s*\n*\s*<a\n*\s*href="(/'+ps('common_word')+'/[A-Za-z0-9\-/_]+)"\s*\n*\s*>\s*\n*\s*(.+?)\s*\n*\s*</a>\s*\n*\s*\n*\s*(.*?)\s*\n*\s*\n*\s*</td>\s*\n*\s*<td>\s*\n*\s*(.+?)\s*\n*\s*</td>\s*\n*\s*</tr>'; 
	iitems=re.compile(s, re.DOTALL).findall(html) ### , re.MULTILINE | re.IGNORECASE | re.DOTALL
	if (iitems is not None):
		ItemCount=len(iitems) # , total_items=ItemCount
		deb('# of items',str(ItemCount)); #debob(iitems); 
		EnableMeta=tfalse(addst("enableMeta"))
		EnableSiteArt=tfalse(addst("enable-site-art"))
		EnableVisitedLeft=tfalse(addst("enable-visited-left"))
		EnableGenresInPlot=tfalse(addst("enable-genres-in-plot"))
		if EnableMeta==False: EnableSiteArt=True
		#for item_url,tInfo,name,imInfo,LInfo in iitems:
		for tInfo,item_url,name,imInfo,LInfo in iitems:
			vtype='episode'; animetype='tvshow'; fimg=""; img=""; contextMenuItems=[]; item_url=_domain_url+item_url; labs={'imdb_id':'','cover_url':'','backdrop_url':'','plot':''}; LInfo=LInfo.strip()
			animename=''+name; animename=animename.replace(' (Dub)','').replace(' (Sub)','').replace(' (TV)','').replace(' OVA','').replace(' Movies','').replace(' Movie','').replace(' Specials','').replace(' New','') #.replace(' 2nd Season','')
			FoundItK=visited_check2(animename)
			if (EnableMeta==True):
				#if FoundItK==True: overlay_p=7
				#else: overlay_p=6
				overlay_p=6
				#
				animename=animename.replace('+','%2B')
				##.replace('','')
				if (" movie" in name.lower()) or (" specials" in name.lower()) or (" ova" in name.lower()): animetype="movie"; vtype='movie'; 
				elif (" (tv)" in name): animetype="tvshow"
				else: animetype="tvshow"
				#
				if animename=='Golden Time': animename+=' (2013)'
				#if animename=='Witch Craft Works': animename='Witch Craft Works (2014)'
				if animename=='Perfect Blue': animename+=' (1997)'
				if animename=='Kingdom': animename+=' (2012)'
				if animename=='Kingdom 2': animename='Kingdom (2012)'
				if animename=='Weiss Survive R': animename='Weiss Survive'
				
				
				
				try:		labs=GRABMETA(animename,animetype,overlay=overlay_p)
				except: labs={'imdb_id':'','cover_url':'','backdrop_url':'','plot':''}
				##labs=GRABMETA(animename,'tvshow')##labs=GRABMETA(animename,'movie')##
				#
				try: img=labs['cover_url']
				except: img=""
				try: fimg=labs['backdrop_url']
				except: fimg=""
				
				try: labs[u'plot']='[COLOR gray]'+labs['plot']+'[/COLOR]'
				except: labs[u'plot']=''
				
				try: debob(labs['genre'])
				except: pass
				
				
				
			###
			#debob(tInfo); 
			if (EnableSiteArt==True):
				if (img=="") or (img==u""):
					try: img=re.compile('"(http://.+?\.jpg)"').findall(tInfo)[0].replace(' ','%20')
					except: img=_artIcon
				if (fimg=="") or (fimg==u""): fimg=''+img
				if fimg==_artIcon: fimg=_artFanart
			try: labs[u'plot']=labs['plot']
			except: labs[u'plot']=''
			if ('<p>' in tInfo) and ('</p>' in tInfo):
				try: labs[u'plot']='[COLOR tan]'+re.compile('<p>\s*\n*\s*(.+?)\s*\n*\s*</p>').findall(tInfo)[0].strip()+'[/COLOR][CR][CR]'+labs['plot'] #[COLOR gray]'+labs['plot']+'[/COLOR]'
				except: pass
			labs[u'plot']=messupText(labs['plot'],_html=True,_ende=True,_a=False,Slashes=False)
			
			if (LInfo=='Completed'): # or (LInfo=='Not yet aired'):
				labs[u'plot']='['+cFL(LInfo,'lime')+'][CR]'+labs['plot']
			if (LInfo=='Not yet aired'):
				labs[u'plot']='['+cFL(LInfo,'red')+'][CR]'+labs['plot']
			#if (tfalse(addst("Notyetaired"))==False) and (LInfo=='Not yet aired'): t=''
			if (EnableMeta==True) and (EnableGenresInPlot==True):
				try:
					if len(labs['genre']) > 0:
						labs[u'plot']="[COLOR green]Genre(s): [B]"+str(labs['genre'])+"[/B][/COLOR][CR]"+labs['plot']
				except: pass
				#
			try: gZ001=labs['genre']
			except: labs[u'genre']=''
			
			
			#
			labs[u'title']=name.replace(' (Dub)',addst("text-dub",' [COLOR green](Dub)[/COLOR]')).replace(' (Sub)',addst("text-sub",' [COLOR blue](Sub)[/COLOR]')).replace(' OVA',addst("text-ova",' [COLOR red]OVA[/COLOR]')).replace(' Movie',addst("text-movie",' [COLOR maroon]Movie[/COLOR]')).replace(': ',addst("text-colon",':[CR] ')).replace(' New',addst("text-new",' [COLOR yellow]New[/COLOR]')).replace(' (TV)',addst("text-tv",' [COLOR cornflowerblue](TV)[/COLOR]')).replace(' Specials',addst("text-specials",' [COLOR deeppink]Specials[/COLOR]')) #.replace('','')
			deb('title',labs[u'title']); deb('url',item_url); deb('img',img); deb('fanart',fimg)
			#deb('plot',labs['plot']); 
			if ('</a>' in LInfo):
				deb('LInfo',LInfo)
				(LatestUrl,LatestName)=re.compile('<a href="(/'+ps('common_word')+'/.+?)">\s*\n*\s*(.+?)\s*\n*\s*</a>').findall(LInfo)[0]
				LatestUrl=_domain_url+LatestUrl
				LatestPar={'url':LatestUrl,'mode':'GetLinks','img':img,'fanart':fimg,'title':labs[u'title'].replace('[CR]','')+' - '+LatestName}
				try: contextMenuItems.append(('Latest:  '+LatestName,'XBMC.Container.Update(%s)' % _addon.build_plugin_url(LatestPar) ))
				except: pass
				#pars={'mode':'GetLinks','img':img,'url':ep_url,'title':ep_name}
				#contextMenuItems.append((ps('cMI.favorites.tv.add.name')+' '+addst('fav.movies.1.name'),ps('cMI.favorites.movie.add.url') % (sys.argv[0],ps('cMI.favorites.tv.add.mode'),section,urllib.quote_plus(name),'',urllib.quote_plus(img),urllib.quote_plus(fimg),urllib.quote_plus(''),urllib.quote_plus(labs['plot']),urllib.quote_plus(''),urllib.quote_plus(item_url), '' )))
			##### Right Click Menu for: Anime #####
			contextMenuItems.append((ps('cMI.showinfo.name'),ps('cMI.showinfo.url')))
			#debob(labs)
			#deb('name',name); 
			#debob(str(my_tools.fav__COMMON__check(name,section,''))); 
			#debob(str(fav__COMMON__check(name,section,''))); 
			if fav__COMMON__check(name,section,'')==True:
				try: contextMenuItems.append((ps('cMI.favorites.tv.remove.name')+' '+addst('fav.movies.1.name'),ps('cMI.favorites.tv.remove.url') % (sys.argv[0],ps('cMI.favorites.tv.remove.mode'),section,urllib.quote_plus(name),'',urllib.quote_plus(img),urllib.quote_plus(fimg),urllib.quote_plus(''),urllib.quote_plus(labs['plot']),urllib.quote_plus(labs['genre']),urllib.quote_plus(url),urllib.quote_plus(str(labs['imdb_id'])),'' )))
				except: pass
			else: 
				try: contextMenuItems.append((ps('cMI.favorites.tv.add.name')+' '+addst('fav.movies.1.name'),ps('cMI.favorites.tv.add.url') % (sys.argv[0],ps('cMI.favorites.tv.add.mode'),section,urllib.quote_plus(name),'',urllib.quote_plus(img),urllib.quote_plus(fimg),urllib.quote_plus(''),urllib.quote_plus(labs['plot']),urllib.quote_plus(''),urllib.quote_plus(item_url),urllib.quote_plus(str(labs['imdb_id'])), '' )))
				except: pass
			if (tfalse(addst("enable-fav-movies-2"))==True): 
				if fav__COMMON__check(name,section,'2')==True:
					try: contextMenuItems.append((ps('cMI.favorites.tv.remove.name')+' '+addst('fav.movies.2.name'),ps('cMI.favorites.tv.remove.url') % (sys.argv[0],ps('cMI.favorites.tv.remove.mode'),section,urllib.quote_plus(name),'',urllib.quote_plus(img),urllib.quote_plus(fimg),urllib.quote_plus(''),urllib.quote_plus(labs['plot']),urllib.quote_plus(labs['genre']),urllib.quote_plus(url),urllib.quote_plus(str(labs['imdb_id'])),'2' )))
					except: pass
				else: 
					try: contextMenuItems.append((ps('cMI.favorites.tv.add.name')+' '+addst('fav.movies.2.name'),ps('cMI.favorites.tv.add.url') % (sys.argv[0],ps('cMI.favorites.tv.add.mode'),section,urllib.quote_plus(name),'',urllib.quote_plus(img),urllib.quote_plus(fimg),urllib.quote_plus(''),urllib.quote_plus(labs['plot']),urllib.quote_plus(''),urllib.quote_plus(item_url),urllib.quote_plus(str(labs['imdb_id'])),'2' )))
					except: pass
			if (tfalse(addst("enable-fav-movies-3"))==True): 
				if fav__COMMON__check(name,section,'3')==True:
					try: contextMenuItems.append((ps('cMI.favorites.tv.remove.name')+' '+addst('fav.movies.3.name'),ps('cMI.favorites.tv.remove.url') % (sys.argv[0],ps('cMI.favorites.tv.remove.mode'),section,urllib.quote_plus(name),'',urllib.quote_plus(img),urllib.quote_plus(fimg),urllib.quote_plus(''),urllib.quote_plus(labs['plot']),urllib.quote_plus(labs['genre']),urllib.quote_plus(url),urllib.quote_plus(str(labs['imdb_id'])),'3' )))
					except: pass
				else: 
					try: contextMenuItems.append((ps('cMI.favorites.tv.add.name')+' '+addst('fav.movies.3.name'),ps('cMI.favorites.tv.add.url') % (sys.argv[0],ps('cMI.favorites.tv.add.mode'),section,urllib.quote_plus(name),'',urllib.quote_plus(img),urllib.quote_plus(fimg),urllib.quote_plus(''),urllib.quote_plus(labs['plot']),urllib.quote_plus(''),urllib.quote_plus(item_url),urllib.quote_plus(str(labs['imdb_id'])),'3' )))
					except: pass
			if (tfalse(addst("enable-fav-movies-4"))==True): 
				if fav__COMMON__check(name,section,'4')==True:
					try: contextMenuItems.append((ps('cMI.favorites.tv.remove.name')+' '+addst('fav.movies.4.name'),ps('cMI.favorites.tv.remove.url') % (sys.argv[0],ps('cMI.favorites.tv.remove.mode'),section,urllib.quote_plus(name),'',urllib.quote_plus(img),urllib.quote_plus(fimg),urllib.quote_plus(''),urllib.quote_plus(labs['plot']),urllib.quote_plus(labs['genre']),urllib.quote_plus(url),urllib.quote_plus(str(labs['imdb_id'])),'4' )))
					except: pass
				else: 
					try: contextMenuItems.append((ps('cMI.favorites.tv.add.name')+' '+addst('fav.movies.4.name'),ps('cMI.favorites.tv.add.url') % (sys.argv[0],ps('cMI.favorites.tv.add.mode'),section,urllib.quote_plus(name),'',urllib.quote_plus(img),urllib.quote_plus(fimg),urllib.quote_plus(''),urllib.quote_plus(labs['plot']),urllib.quote_plus(''),urllib.quote_plus(item_url),urllib.quote_plus(str(labs['imdb_id'])),'4' )))
					except: pass
			##if (labs['fanart'] is not ''): contextMenuItems.append(('Download Wallpaper', 'XBMC.RunPlugin(%s)' % _addon.build_plugin_url( { 'mode': 'Download' , 'section': ps('section.wallpaper') , 'studio': name+'  ('+year+')' , 'img': labs['thumbnail'] , 'url': labs['fanart'] } ) ))
			##contextMenuItems.append(('Add - Library','XBMC.RunPlugin(%s?mode=%s&section=%s&title=%s&showtitle=%s&showyear=%s&url=%s&img=%s)' % ( sys.argv[0],'LibrarySaveMovie',section, urllib.quote_plus(name), urllib.quote_plus(name), urllib.quote_plus(year), urllib.quote_plus(_domain_url+item_url), urllib.quote_plus(thumbnail))))
			##if os.path.exists(xbmc.translatePath(ps('special.home.addons'))+ps('cMI.1ch.search.folder')):
			##	contextMenuItems.append((ps('cMI.1ch.search.name'), 					ps('cMI.1ch.search.url') 				% (ps('cMI.1ch.search.plugin'), 			ps('cMI.1ch.search.section'), 			name)))
			##if os.path.exists(xbmc.translatePath(ps('special.home.addons'))+ps('cMI.primewire.search.folder')):
			##	contextMenuItems.append((ps('cMI.primewire.search.name'), 		ps('cMI.primewire.search.url') 	% (ps('cMI.primewire.search.plugin'), ps('cMI.primewire.search.section'), name)))
			##### Right Click Menu for: Anime ##### /\ #####
			try: contextMenuItems.append(("Refresh MetaData", "XBMC.RunPlugin(%s)" % _addon.build_plugin_url({'mode':'refresh_meta','imdb_id':str(labs['imdb_id']),'video_type':animetype,'title':animename,'alt_id':'imdbnum','year':''}) ))
			except: pass
			pars={'mode':'GetEpisodes','url':item_url,'img':img,'title':labs[u'title'],'type':vtype,'fanart':fimg}
			if FoundItK==True: labs[u'overlay']=7
			#else: labs['overlay']=6
			if (EnableMeta==True):
				pars[u'imdbid']=labs['imdb_id']
				if len(pars[u'imdbid'])==0: pars[u'imdbid']='0'
			if EnableVisitedLeft==True:
				if FoundItK==True: 
					labs[u'title']=addst("text-series-left-watched","[COLOR deeppink]@  [/COLOR]")+labs[u'title']
				else: labs[u'title']=addst("text-series-left-unwatched","[COLOR black]@  [/COLOR]")+labs[u'title']
			else:
				if FoundItK==True: labs[u'title']+=addst("text-series-right-watched","[COLOR deeppink]  @[/COLOR]")
			#deb('imInfo',imInfo); deb("mark-hot",str(addst("mark-hot","false"))); deb("hot in imInfo",str('/Content/images/hot.png' in imInfo)); 
			if (tfalse(addst("mark-hot","false"))==True) and ('/Content/images/hot.png' in imInfo):
				labs[u'title']+=" "+addst("text-hot","[COLOR fuchsia][[I]HOT [/I]][/COLOR]"); #debob(labs[u'title']); 
			if (tfalse(addst("Notyetaired"))==False) and (LInfo=='Not yet aired'): deb(LInfo,name)
			else: 
				if tfalse(addst("singleline"))==True: labs[u'title']=labs[u'title'].replace('[CR]',' ')
				try: _addon.add_directory(pars, labs, img=img, fanart=fimg, contextmenu_items=contextMenuItems, total_items=ItemCount)
				except: pass
			#if (tfalse(addst("Notyetaired"))==True) or (LInfo is not 'Not yet aired'):
			#	_addon.add_directory(pars, labs, img=img, fanart=fimg, contextmenu_items=contextMenuItems, total_items=ItemCount)
	else: deb('Error','no items found.')
	if (ps('LI.nextpage.check') in html_last): 
		if (_debugging==True): print 'A next-page has been found.'
		nextpage=re.findall(ps('LI.nextpage.match'), html_last)[0] #nextpage=re.compile('<li class="next"><a href="http://www.solarmovie.so/.+?.html?page=(\d+)"></a></li>').findall(html_last)[0]
		if (int(nextpage) <= last) and (end < last) and (start < last) and (start is not int(nextpage)): #(int(nextpage) > end) and (int(nextpage) <= last): # and (end < last): ## Do Show Next Page Link ##
			if (_debugging==True): print 'A next-page is being added.'
			#print {'mode': 'GetTitles', 'url': url, 'pageno': nextpage, 'pagecount': numOfPages}
			nextLastPage=str(int(nextpage)+int(numOfPages)-1)
			if nextLastPage==nextpage: nextLastPage=""
			else: nextLastPage="-"+nextLastPage
			try: _addon.add_directory({'mode': 'GetTitles', 'section': section, 'url': url, 'pageno': nextpage, 'pagecount': numOfPages}, {'title': addst("text-page-next","[COLOR goldenrod]  >  [COLOR red]Next[/COLOR]...[/COLOR][COLOR blue] %s%s[/COLOR]") % (str(nextpage),nextLastPage)}, img=ps('img_next'))
			except: pass
			#print {'start':str(start),'end':str(end),'last':str(last),'nextpage':str(nextpage)}
			if ' Last </a></li>' in html_last:
				#myNote('test',':'+str(last)+':')
				if (int(startPage) <  9) and (int(LPnum) > 10): i=10; _addon.add_directory({'mode': 'GetTitles', 'section': section, 'url': url, 'pageno': i, 'pagecount': numOfPages}, {'title': addst("text-page-forward-to","[COLOR goldenrod]  >>  [COLOR red][/COLOR]...[/COLOR][COLOR blue] %s[/COLOR]") % str(i)}, img=ps('img_next'))
				if (int(startPage) < 19) and (int(LPnum) > 20): i=20; _addon.add_directory({'mode': 'GetTitles', 'section': section, 'url': url, 'pageno': i, 'pagecount': numOfPages}, {'title': addst("text-page-forward-to","[COLOR goldenrod]  >>  [COLOR red][/COLOR]...[/COLOR][COLOR blue] %s[/COLOR]") % str(i)}, img=ps('img_next'))
				if (int(startPage) < 29) and (int(LPnum) > 30): i=30; _addon.add_directory({'mode': 'GetTitles', 'section': section, 'url': url, 'pageno': i, 'pagecount': numOfPages}, {'title': addst("text-page-forward-to","[COLOR goldenrod]  >>  [COLOR red][/COLOR]...[/COLOR][COLOR blue] %s[/COLOR]") % str(i)}, img=ps('img_next'))
				if (int(startPage) < 39) and (int(LPnum) > 40): i=40; _addon.add_directory({'mode': 'GetTitles', 'section': section, 'url': url, 'pageno': i, 'pagecount': numOfPages}, {'title': addst("text-page-forward-to","[COLOR goldenrod]  >>  [COLOR red][/COLOR]...[/COLOR][COLOR blue] %s[/COLOR]") % str(i)}, img=ps('img_next'))
				if (int(startPage) < 49) and (int(LPnum) > 50): i=50; _addon.add_directory({'mode': 'GetTitles', 'section': section, 'url': url, 'pageno': i, 'pagecount': numOfPages}, {'title': addst("text-page-forward-to","[COLOR goldenrod]  >>  [COLOR red][/COLOR]...[/COLOR][COLOR blue] %s[/COLOR]") % str(i)}, img=ps('img_next'))
				if (int(startPage) < 59) and (int(LPnum) > 60): i=60; _addon.add_directory({'mode': 'GetTitles', 'section': section, 'url': url, 'pageno': i, 'pagecount': numOfPages}, {'title': addst("text-page-forward-to","[COLOR goldenrod]  >>  [COLOR red][/COLOR]...[/COLOR][COLOR blue] %s[/COLOR]") % str(i)}, img=ps('img_next'))
				if (int(startPage) < 69) and (int(LPnum) > 70): i=70; _addon.add_directory({'mode': 'GetTitles', 'section': section, 'url': url, 'pageno': i, 'pagecount': numOfPages}, {'title': addst("text-page-forward-to","[COLOR goldenrod]  >>  [COLOR red][/COLOR]...[/COLOR][COLOR blue] %s[/COLOR]") % str(i)}, img=ps('img_next'))
				if (int(startPage) < 79) and (int(LPnum) > 80): i=80; _addon.add_directory({'mode': 'GetTitles', 'section': section, 'url': url, 'pageno': i, 'pagecount': numOfPages}, {'title': addst("text-page-forward-to","[COLOR goldenrod]  >>  [COLOR red][/COLOR]...[/COLOR][COLOR blue] %s[/COLOR]") % str(i)}, img=ps('img_next'))
				if (int(startPage) < 89) and (int(LPnum) > 90): i=90; _addon.add_directory({'mode': 'GetTitles', 'section': section, 'url': url, 'pageno': i, 'pagecount': numOfPages}, {'title': addst("text-page-forward-to","[COLOR goldenrod]  >>  [COLOR red][/COLOR]...[/COLOR][COLOR blue] %s[/COLOR]") % str(i)}, img=ps('img_next'))
				try: _addon.add_directory({'mode': 'GetTitles', 'section': section, 'url': url, 'pageno': LPnum, 'pagecount': numOfPages}, {'title':addst("text-page-last","[COLOR goldenrod]  >>  [COLOR red]Last[/COLOR]...[/COLOR][COLOR blue] %s[/COLOR]") % str(LPnum)}, img=ps('img_next'))
				except: pass
				
				
	set_view(ps('content_tvshows'),addst('anime-view')); eod(); return
	################################################################################

def listItems_Upcoming(section=_default_section_, url='', startPage='1', numOfPages='1', genre='', year='', stitle='', season='', episode='', html='', chck=''): # List: Movies or TV Shows
	if (url==''): return
	#if (chck=='Latest'): url=url+chr(35)+'latest'
	WhereAmI('@ the Item List -- url: %s' % url)
	if (tfalse(addst('customproxy','false'))==True) and (len(addst('proxy','')) > 9): Proxy=addst('proxy','')
	else: Proxy="" #ps('proxy')
	start=int(startPage); end=(start+int(numOfPages)); html=''; html_last=''; nextpage=startPage; deb('page start',str(start)); deb('page end',str(end))
	cookie_file=xbmc.translatePath(os.path.join(_addonPath,'temp.cache.txt'))
	try: 
		if isFile(cookie_file)==True: html_=nURL(url,headers={'Referer':_domain_url},cookie_file=cookie_file,load_cookie=True,save_cookie=True)
		else: html_=nURL(url,headers={'Referer':_domain_url},proxy=Proxy,cookie_file=cookie_file,save_cookie=True)
	except: html_=''
	if (html_=='') or (html_=='none') or (html_==None): 
		deb('Error','Problem with page'); deadNote('Results:  '+section,'No results were found.')
		return
	deb('length of html_',str(len(html_))); 
	try:		last=int(re.compile('<li><a href="http://.+?page=\d+">(\d+)</a></li>\*s\n*\s*<li><a href="http://.+?page=\d+">&rsaquo;\s*Next\s*</a></li>').findall(html_))[0]
	except:	last=2
	deb('number of pages',str(last))
	if ('<h1>Nothing was found by your request</h1>' in html_): deadNote('Results:  '+section,'Nothing was found by your request'); eod(); return
	pmatch=re.findall(ps('LI.page.find'), html_)
	if pmatch: last=pmatch[-1]
	if ('?' in url):	urlSplitter='&page='; deb('urlSplitter',urlSplitter) ## Quick fix for urls that already have '?' in it.
	else:							urlSplitter='?page='; deb('urlSplitter',urlSplitter)
	for page in range(start,min(last,end)):
		if (int(page)> 1): #if (int(startPage)> 1):
			if ('&page=' in url): pageUrl=url.replace('&page=','&pagenull=')+'&page='+str(page) ## Quick fix.
			if ('?page=' in url): pageUrl=url.replace('?page=','?pagenull=')+'&page='+str(page) ## Quick fix.
			else: pageUrl=url+urlSplitter+str(page) #ps('LI.page.param')+startPage
		else: pageUrl=url
		deb('item listings for',pageUrl)
		try: 
			try: 
				if isFile(cookie_file)==True: html_last=nURL(pageUrl,headers={'Referer':_domain_url},proxy=Proxy,cookie_file=cookie_file,load_cookie=True,save_cookie=True)
				else: html_last=nURL(pageUrl,headers={'Referer':_domain_url},proxy=Proxy,cookie_file=cookie_file,save_cookie=True)
			except: 
				try:
					if isFile(cookie_file)==True: html=nURL(url,headers={'Referer':_domain_url},proxy=Proxy,cookie_file=cookie_file,load_cookie=True,save_cookie=True)
					else: html=nURL(url,headers={'Referer':_domain_url},proxy=Proxy,cookie_file=cookie_file,save_cookie=True)
				except: t=''
			if (_shoDebugging==True) and (html_last==''): deadNote('Testing','html_last is empty')
			if (html_last in html): t=''
			else: html=html+'\r\n'+html_last; deb('length of html_last',str(len(html_last))); 
			##if (_debugging==True): print html_last
		except: t=''
	if ' Last </a></li>' in html_last:
		LPurl=html_last.replace('&raquo;','').split(' Last </a></li>')[0].split('<li><a href="')[-1].split('"')[0]; LPnum=LPurl.split('page=')[-1]
		try: LPnum=LPnum.split('&')[0]
		except: pass
	else: LPurl=''; LPnum=startPage; 
	if (int(startPage) > 2): 
		try: _addon.add_directory({'mode': 'GetTitles', 'section': section, 'url': url, 'pageno': '1', 'pagecount': numOfPages}, {'title': addst("text-page-first","[COLOR goldenrod]  <<  [COLOR red]First[/COLOR]...[/COLOR][COLOR blue] 1[/COLOR]")}, img=ps('img_prev'))
		except: pass
	if (int(startPage) > 11): i=10; _addon.add_directory({'mode': 'GetTitles', 'section': section, 'url': url, 'pageno': str(i), 'pagecount': numOfPages}, {'title': addst("text-page-back-to","[COLOR goldenrod]  <<  [COLOR red][/COLOR]...[/COLOR][COLOR blue] %s[/COLOR]") % str(i)}, img=ps('img_prev'))
	if (int(startPage) > 21): i=20; _addon.add_directory({'mode': 'GetTitles', 'section': section, 'url': url, 'pageno': str(i), 'pagecount': numOfPages}, {'title': addst("text-page-back-to","[COLOR goldenrod]  <<  [COLOR red][/COLOR]...[/COLOR][COLOR blue] %s[/COLOR]") % str(i)}, img=ps('img_prev'))
	if (int(startPage) > 31): i=30; _addon.add_directory({'mode': 'GetTitles', 'section': section, 'url': url, 'pageno': str(i), 'pagecount': numOfPages}, {'title': addst("text-page-back-to","[COLOR goldenrod]  <<  [COLOR red][/COLOR]...[/COLOR][COLOR blue] %s[/COLOR]") % str(i)}, img=ps('img_prev'))
	if (int(startPage) > 41): i=40; _addon.add_directory({'mode': 'GetTitles', 'section': section, 'url': url, 'pageno': str(i), 'pagecount': numOfPages}, {'title': addst("text-page-back-to","[COLOR goldenrod]  <<  [COLOR red][/COLOR]...[/COLOR][COLOR blue] %s[/COLOR]") % str(i)}, img=ps('img_prev'))
	if (int(startPage) > 51): i=50; _addon.add_directory({'mode': 'GetTitles', 'section': section, 'url': url, 'pageno': str(i), 'pagecount': numOfPages}, {'title': addst("text-page-back-to","[COLOR goldenrod]  <<  [COLOR red][/COLOR]...[/COLOR][COLOR blue] %s[/COLOR]") % str(i)}, img=ps('img_prev'))
	if (int(startPage) > 61): i=60; _addon.add_directory({'mode': 'GetTitles', 'section': section, 'url': url, 'pageno': str(i), 'pagecount': numOfPages}, {'title': addst("text-page-back-to","[COLOR goldenrod]  <<  [COLOR red][/COLOR]...[/COLOR][COLOR blue] %s[/COLOR]") % str(i)}, img=ps('img_prev'))
	if (int(startPage) > 71): i=70; _addon.add_directory({'mode': 'GetTitles', 'section': section, 'url': url, 'pageno': str(i), 'pagecount': numOfPages}, {'title': addst("text-page-back-to","[COLOR goldenrod]  <<  [COLOR red][/COLOR]...[/COLOR][COLOR blue] %s[/COLOR]") % str(i)}, img=ps('img_prev'))
	if (int(startPage) > 81): i=80; _addon.add_directory({'mode': 'GetTitles', 'section': section, 'url': url, 'pageno': str(i), 'pagecount': numOfPages}, {'title': addst("text-page-back-to","[COLOR goldenrod]  <<  [COLOR red][/COLOR]...[/COLOR][COLOR blue] %s[/COLOR]") % str(i)}, img=ps('img_prev'))
	if (int(startPage) > 91): i=90; _addon.add_directory({'mode': 'GetTitles', 'section': section, 'url': url, 'pageno': str(i), 'pagecount': numOfPages}, {'title': addst("text-page-back-to","[COLOR goldenrod]  <<  [COLOR red][/COLOR]...[/COLOR][COLOR blue] %s[/COLOR]") % str(i)}, img=ps('img_prev'))
	if (int(startPage) > 1): 
		try: _addon.add_directory({'mode': 'GetTitles', 'section': section, 'url': url, 'pageno': str(int(startPage)-1), 'pagecount': numOfPages}, {'title': addst("text-page-prev","[COLOR goldenrod]  <  [COLOR red]Previous[/COLOR]...[/COLOR][COLOR blue] %s[/COLOR]") % str(int(startPage)-1)}, img=ps('img_prev'))
		except: pass
	###	### _addon.add_directory({'mode': 'GetTitles', 'url': url, 'startPage': str(end), 'numOfPages': numOfPages}, {'title': 'Next...'})
	###html=nolines(html)
	html=ParseDescription(html); html=remove_accents(html) #if (_debugging==True): print html
	html=messupText(html,_html=True,_ende=True,_a=False,Slashes=False)
	deb('Length of HTML',str(len(html))); #debob(html); 
	temp_file=xbmc.translatePath(os.path.join(_addonPath,'temp.html.items.txt'))
	if (_debugging==True) and (_testing==True):
		try: my_tools._SaveFile(temp_file,html)
		except: pass
	######
	if (len(html)==0): deb('Error','html is empty.'); return
	###s='<a\n*\s*href="(/'+ps('common_word')+'/[A-Za-z0-9\-/_]+)"\n*\s*title=\'(.*?)\'\n*\s*[/]*>\s*\n*\s*(.+?)\s*\n*\s*</a>\s*\n*\s*\n*\s*(.*?)\s*\n*\s*\n*\s*</td>\s*\n*\s*<td>\s*\n*\s*(.+?)\s*\n*\s*</td>\s*\n*\s*</tr>'; 
	##s='<a\n*\s*href="(/'+ps('common_word')+'/[A-Za-z0-9\-/_]+)"\n*\s*title=\'(.*?)\'\n*\s*[/]*>\s*\n*\s*(.+?)\s*\n*\s*</a>\s*\n*\s*\n*\s*(.*?)\s*\n*\s*\n*\s*</td>\s*\n*\s*<td>\s*\n*\s*(.+?)\s*\n*\s*</td>\s*\n*\s*</tr>'; 
	#s='<td title=\'(.*?)\'\n*\s*[/]*>\s*\n*\s*<a\n*\s*href="(/'+ps('common_word')+'/[A-Za-z0-9\-/_]+)"\s*\n*\s*>\s*\n*\s*(.+?)\s*\n*\s*</a>\s*\n*\s*\n*\s*(.*?)\s*\n*\s*\n*\s*</td>\s*\n*\s*<td>\s*\n*\s*(.+?)\s*\n*\s*</td>\s*\n*\s*</tr>'; 
	
	#s='<td title=\'(.*?)\'\n*\s*[/]*>\s*\n*\s*<a\n*\s*href="(/'+ps('common_word')+'/[A-Za-z0-9\-/_]+)"\s*\n*\s*>\s*\n*\s*(.+?)\s*\n*\s*</a>\s*\n*\s*\n*\s*(.*?)\s*\n*\s*\n*\s*</td>\s*\n*\s*<td>\s*\n*\s*(.+?)\s*\n*\s*</td>\s*\n*\s*</tr>'; 
	s ='<div style="display: inline-block; width: \d+px">\s*'; 
	s+='<a href="(/'+ps('common_word')+'/[A-Za-z0-9\-/_]+)">\s*'; 
	s+='<img width="\d+px" height="\d+px" src="(.+?)"></a>\s*'; 
	s+='</div>\s*<div style="display: inline-block; width: \d+px; vertical-align: top; padding-left: \d+px">\s*'; 
	s+='<a href="(/'+ps('common_word')+'/[A-Za-z0-9\-/_]+)"><span class="title">(.+?)</span></a>\s*'; 
	s+='<p>\s*<span class="info">\s*Genres\s*:\s*</span>\s*(.*?)\s*</p>\s*'; 
	s+='<p>\s*<span class="info">\s*Date aired\s*:\s*</span>\s*(.*?)\s*</p>\s*'; 
	s+='<p>\s*<span class="info">\s*Summary\s*:\s*</span>\s*<p>\s*(.*?)</p>\s*</p>\s*'; 
	#s+='</div>\s*</div>\s*<div class="clear2">\s*</div>\s*'; 
	#s+='\s*'; 
	#s+='\s*'; 
	html=nolines(html); html=html.replace('&nbsp;',''); 
	iitems=re.compile(s, re.DOTALL).findall(html) ### , re.MULTILINE | re.IGNORECASE | re.DOTALL
	if (iitems is not None):
		ItemCount=len(iitems) # , total_items=ItemCount
		deb('# of items',str(ItemCount)); #debob(iitems); 
		EnableMeta=tfalse(addst("enableMeta"))
		EnableSiteArt=tfalse(addst("enable-site-art"))
		EnableVisitedLeft=tfalse(addst("enable-visited-left"))
		EnableGenresInPlot=tfalse(addst("enable-genres-in-plot"))
		if EnableMeta==False: EnableSiteArt=True
		### ## ### 
		EnableMeta=False; EnableSiteArt=True
		### ## ### 
		#for item_url,tInfo,name,imInfo,LInfo in iitems:
		#for tInfo,item_url,name,imInfo,LInfo in iitems:
		for item_url,img_url,item_url,name,list_of_genres,when_date,summary in iitems: #tInfo, #,imInfo,LInfo
			vtype='episode'; animetype='tvshow'; fimg=""; img=""; contextMenuItems=[]; item_url=_domain_url+item_url; labs={'imdb_id':'','cover_url':'','backdrop_url':'','plot':''}; #LInfo=LInfo.strip()
			### ## ### 
			LInfo=''; tInfo=''; imInfo=''; 
			### ## ### 
			animename=''+name; animename=animename.replace(' (Dub)','').replace(' (Sub)','').replace(' (TV)','').replace(' OVA','').replace(' Movies','').replace(' Movie','').replace(' Specials','').replace(' New','') #.replace(' 2nd Season','')
			FoundItK=visited_check2(animename)
			if (EnableMeta==True):
				#if FoundItK==True: overlay_p=7
				#else: overlay_p=6
				overlay_p=6
				#
				animename=animename.replace('+','%2B')
				##.replace('','')
				if (" movie" in name.lower()) or (" specials" in name.lower()) or (" ova" in name.lower()): animetype="movie"; vtype='movie'; 
				elif (" (tv)" in name): animetype="tvshow"
				else: animetype="tvshow"
				#
				if animename=='Golden Time': animename+=' (2013)'
				#if animename=='Witch Craft Works': animename='Witch Craft Works (2014)'
				if animename=='Perfect Blue': animename+=' (1997)'
				if animename=='Kingdom': animename+=' (2012)'
				if animename=='Kingdom 2': animename='Kingdom (2012)'
				if animename=='Weiss Survive R': animename='Weiss Survive'
				
				
				
				try:		labs=GRABMETA(animename,animetype,overlay=overlay_p)
				except: labs={'imdb_id':'','cover_url':'','backdrop_url':'','plot':''}
				##labs=GRABMETA(animename,'tvshow')##labs=GRABMETA(animename,'movie')##
				#
				try: img=labs['cover_url']
				except: img=""
				try: fimg=labs['backdrop_url']
				except: fimg=""
				
				try: labs[u'plot']='[COLOR gray]'+labs['plot']+'[/COLOR]'
				except: labs[u'plot']=''
				
				try: debob(labs['genre'])
				except: pass
				
				
				
			###
			if (EnableSiteArt==True):
				if (img=="") or (img==u"") or (len(img)==0):
					#try: img=re.compile('"(http://.+?\.jpg)"').findall(tInfo)[0].replace(' ','%20')
					#except: img=_artIcon
					img=img_url
				if (fimg=="") or (fimg==u""): fimg=''+img
				if fimg==_artIcon: fimg=_artFanart
			try: labs[u'plot']=labs['plot']
			except: labs[u'plot']=''
			if ('<p>' in tInfo) and ('</p>' in tInfo):
				try: labs[u'plot']='[COLOR tan]'+re.compile('<p>\s*\n*\s*(.+?)\s*\n*\s*</p>').findall(tInfo)[0].strip()+'[/COLOR][CR][CR]'+labs['plot'] #[COLOR gray]'+labs['plot']+'[/COLOR]'
				except: pass
			### ## ### 
			CR='[CR]'; CR2='[CR][CR]'; 
			if len(labs[u'plot'])==0: labs[u'plot']+=cFL(summary,'grey'); 
			else: labs[u'plot']+=CR2+summary; 
			labs[u'plot']=CR+cFL(cFL('Date Aired: ','deeppink')+when_date,'mediumpurple')+CR+labs['plot']; 
			labs[u'plot']=labs['plot'].replace('<br/>',CR).replace('<br>',CR).replace('<BR/>',CR).replace('<BR>',CR)
			### ## ### 
			labs[u'plot']=messupText(labs['plot'],_html=True,_ende=True,_a=False,Slashes=False)
			
			#if (LInfo=='Completed'): # or (LInfo=='Not yet aired'):
			#	labs[u'plot']='['+cFL(LInfo,'lime')+'][CR]'+labs['plot']
			#if (LInfo=='Not yet aired'):
			#	labs[u'plot']='['+cFL(LInfo,'red')+'][CR]'+labs['plot']
			#if (tfalse(addst("Notyetaired"))==False) and (LInfo=='Not yet aired'): t=''
			if (EnableMeta==True) and (EnableGenresInPlot==True):
				try:
					if len(labs['genre']) > 0:
						labs[u'plot']="[COLOR green]Genre(s): [B]"+str(labs['genre'])+"[/B][/COLOR][CR]"+labs['plot']
				except: pass
				#
			try: gZ001=labs['genre']
			except: labs[u'genre']=''
			
			
			#
			labs[u'title']=name.replace(' (Dub)',addst("text-dub",' [COLOR green](Dub)[/COLOR]')).replace(' (Sub)',addst("text-sub",' [COLOR blue](Sub)[/COLOR]')).replace(' OVA',addst("text-ova",' [COLOR red]OVA[/COLOR]')).replace(' Movie',addst("text-movie",' [COLOR maroon]Movie[/COLOR]')).replace(': ',addst("text-colon",':[CR] ')).replace(' New',addst("text-new",' [COLOR yellow]New[/COLOR]')).replace(' (TV)',addst("text-tv",' [COLOR cornflowerblue](TV)[/COLOR]')).replace(' Specials',addst("text-specials",' [COLOR deeppink]Specials[/COLOR]')) #.replace('','')
			deb('title',labs[u'title']); deb('url',item_url); deb('img',img); deb('fanart',fimg)
			##deb('plot',labs['plot']); 
			#if ('</a>' in LInfo):
			#	deb('LInfo',LInfo)
			#	(LatestUrl,LatestName)=re.compile('<a href="(/'+ps('common_word')+'/.+?)">\s*\n*\s*(.+?)\s*\n*\s*</a>').findall(LInfo)[0]
			#	LatestUrl=_domain_url+LatestUrl
			#	LatestPar={'url':LatestUrl,'mode':'GetLinks','img':img,'fanart':fimg,'title':labs[u'title'].replace('[CR]','')+' - '+LatestName}
			#	try: contextMenuItems.append(('Latest:  '+LatestName,'XBMC.Container.Update(%s)' % _addon.build_plugin_url(LatestPar) ))
			#	except: pass
			#	#pars={'mode':'GetLinks','img':img,'url':ep_url,'title':ep_name}
			#	#contextMenuItems.append((ps('cMI.favorites.tv.add.name')+' '+addst('fav.movies.1.name'),ps('cMI.favorites.movie.add.url') % (sys.argv[0],ps('cMI.favorites.tv.add.mode'),section,urllib.quote_plus(name),'',urllib.quote_plus(img),urllib.quote_plus(fimg),urllib.quote_plus(''),urllib.quote_plus(labs['plot']),urllib.quote_plus(''),urllib.quote_plus(item_url), '' )))
			##### Right Click Menu for: Anime #####
			contextMenuItems.append((ps('cMI.showinfo.name'),ps('cMI.showinfo.url')))
			#debob(labs)
			#deb('name',name); 
			#debob(str(my_tools.fav__COMMON__check(name,section,''))); 
			#debob(str(fav__COMMON__check(name,section,''))); 
			if fav__COMMON__check(name,section,'')==True:
				try: contextMenuItems.append((ps('cMI.favorites.tv.remove.name')+' '+addst('fav.movies.1.name'),ps('cMI.favorites.tv.remove.url') % (sys.argv[0],ps('cMI.favorites.tv.remove.mode'),section,urllib.quote_plus(name),'',urllib.quote_plus(img),urllib.quote_plus(fimg),urllib.quote_plus(''),urllib.quote_plus(labs['plot']),urllib.quote_plus(labs['genre']),urllib.quote_plus(url),urllib.quote_plus(str(labs['imdb_id'])),'' )))
				except: pass
			else: 
				try: contextMenuItems.append((ps('cMI.favorites.tv.add.name')+' '+addst('fav.movies.1.name'),ps('cMI.favorites.tv.add.url') % (sys.argv[0],ps('cMI.favorites.tv.add.mode'),section,urllib.quote_plus(name),'',urllib.quote_plus(img),urllib.quote_plus(fimg),urllib.quote_plus(''),urllib.quote_plus(labs['plot']),urllib.quote_plus(''),urllib.quote_plus(item_url),urllib.quote_plus(str(labs['imdb_id'])), '' )))
				except: pass
			if (tfalse(addst("enable-fav-movies-2"))==True): 
				if fav__COMMON__check(name,section,'2')==True:
					try: contextMenuItems.append((ps('cMI.favorites.tv.remove.name')+' '+addst('fav.movies.2.name'),ps('cMI.favorites.tv.remove.url') % (sys.argv[0],ps('cMI.favorites.tv.remove.mode'),section,urllib.quote_plus(name),'',urllib.quote_plus(img),urllib.quote_plus(fimg),urllib.quote_plus(''),urllib.quote_plus(labs['plot']),urllib.quote_plus(labs['genre']),urllib.quote_plus(url),urllib.quote_plus(str(labs['imdb_id'])),'2' )))
					except: pass
				else: 
					try: contextMenuItems.append((ps('cMI.favorites.tv.add.name')+' '+addst('fav.movies.2.name'),ps('cMI.favorites.tv.add.url') % (sys.argv[0],ps('cMI.favorites.tv.add.mode'),section,urllib.quote_plus(name),'',urllib.quote_plus(img),urllib.quote_plus(fimg),urllib.quote_plus(''),urllib.quote_plus(labs['plot']),urllib.quote_plus(''),urllib.quote_plus(item_url),urllib.quote_plus(str(labs['imdb_id'])),'2' )))
					except: pass
			if (tfalse(addst("enable-fav-movies-3"))==True): 
				if fav__COMMON__check(name,section,'3')==True:
					try: contextMenuItems.append((ps('cMI.favorites.tv.remove.name')+' '+addst('fav.movies.3.name'),ps('cMI.favorites.tv.remove.url') % (sys.argv[0],ps('cMI.favorites.tv.remove.mode'),section,urllib.quote_plus(name),'',urllib.quote_plus(img),urllib.quote_plus(fimg),urllib.quote_plus(''),urllib.quote_plus(labs['plot']),urllib.quote_plus(labs['genre']),urllib.quote_plus(url),urllib.quote_plus(str(labs['imdb_id'])),'3' )))
					except: pass
				else: 
					try: contextMenuItems.append((ps('cMI.favorites.tv.add.name')+' '+addst('fav.movies.3.name'),ps('cMI.favorites.tv.add.url') % (sys.argv[0],ps('cMI.favorites.tv.add.mode'),section,urllib.quote_plus(name),'',urllib.quote_plus(img),urllib.quote_plus(fimg),urllib.quote_plus(''),urllib.quote_plus(labs['plot']),urllib.quote_plus(''),urllib.quote_plus(item_url),urllib.quote_plus(str(labs['imdb_id'])),'3' )))
					except: pass
			if (tfalse(addst("enable-fav-movies-4"))==True): 
				if fav__COMMON__check(name,section,'4')==True:
					try: contextMenuItems.append((ps('cMI.favorites.tv.remove.name')+' '+addst('fav.movies.4.name'),ps('cMI.favorites.tv.remove.url') % (sys.argv[0],ps('cMI.favorites.tv.remove.mode'),section,urllib.quote_plus(name),'',urllib.quote_plus(img),urllib.quote_plus(fimg),urllib.quote_plus(''),urllib.quote_plus(labs['plot']),urllib.quote_plus(labs['genre']),urllib.quote_plus(url),urllib.quote_plus(str(labs['imdb_id'])),'4' )))
					except: pass
				else: 
					try: contextMenuItems.append((ps('cMI.favorites.tv.add.name')+' '+addst('fav.movies.4.name'),ps('cMI.favorites.tv.add.url') % (sys.argv[0],ps('cMI.favorites.tv.add.mode'),section,urllib.quote_plus(name),'',urllib.quote_plus(img),urllib.quote_plus(fimg),urllib.quote_plus(''),urllib.quote_plus(labs['plot']),urllib.quote_plus(''),urllib.quote_plus(item_url),urllib.quote_plus(str(labs['imdb_id'])),'4' )))
					except: pass
			##if (labs['fanart'] is not ''): contextMenuItems.append(('Download Wallpaper', 'XBMC.RunPlugin(%s)' % _addon.build_plugin_url( { 'mode': 'Download' , 'section': ps('section.wallpaper') , 'studio': name+'  ('+year+')' , 'img': labs['thumbnail'] , 'url': labs['fanart'] } ) ))
			##contextMenuItems.append(('Add - Library','XBMC.RunPlugin(%s?mode=%s&section=%s&title=%s&showtitle=%s&showyear=%s&url=%s&img=%s)' % ( sys.argv[0],'LibrarySaveMovie',section, urllib.quote_plus(name), urllib.quote_plus(name), urllib.quote_plus(year), urllib.quote_plus(_domain_url+item_url), urllib.quote_plus(thumbnail))))
			##if os.path.exists(xbmc.translatePath(ps('special.home.addons'))+ps('cMI.1ch.search.folder')):
			##	contextMenuItems.append((ps('cMI.1ch.search.name'), 					ps('cMI.1ch.search.url') 				% (ps('cMI.1ch.search.plugin'), 			ps('cMI.1ch.search.section'), 			name)))
			##if os.path.exists(xbmc.translatePath(ps('special.home.addons'))+ps('cMI.primewire.search.folder')):
			##	contextMenuItems.append((ps('cMI.primewire.search.name'), 		ps('cMI.primewire.search.url') 	% (ps('cMI.primewire.search.plugin'), ps('cMI.primewire.search.section'), name)))
			##### Right Click Menu for: Anime ##### /\ #####
			try: contextMenuItems.append(("Refresh MetaData", "XBMC.RunPlugin(%s)" % _addon.build_plugin_url({'mode':'refresh_meta','imdb_id':str(labs['imdb_id']),'video_type':animetype,'title':animename,'alt_id':'imdbnum','year':''}) ))
			except: pass
			pars={'mode':'GetEpisodes','url':item_url,'img':img,'title':labs[u'title'],'type':vtype,'fanart':fimg}
			if FoundItK==True: labs[u'overlay']=7
			#else: labs['overlay']=6
			if (EnableMeta==True):
				pars[u'imdbid']=labs['imdb_id']
				if len(pars[u'imdbid'])==0: pars[u'imdbid']='0'
			if EnableVisitedLeft==True:
				if FoundItK==True: 
					labs[u'title']=addst("text-series-left-watched","[COLOR deeppink]@  [/COLOR]")+labs[u'title']
				else: labs[u'title']=addst("text-series-left-unwatched","[COLOR black]@  [/COLOR]")+labs[u'title']
			else:
				if FoundItK==True: labs[u'title']+=addst("text-series-right-watched","[COLOR deeppink]  @[/COLOR]")
			##deb('imInfo',imInfo); deb("mark-hot",str(addst("mark-hot","false"))); deb("hot in imInfo",str('/Content/images/hot.png' in imInfo)); 
			#if (tfalse(addst("mark-hot","false"))==True) and ('/Content/images/hot.png' in imInfo):
			#	labs[u'title']+=" "+addst("text-hot","[COLOR fuchsia][[I]HOT [/I]][/COLOR]"); #debob(labs[u'title']); 
			if (tfalse(addst("Notyetaired"))==False) and (LInfo=='Not yet aired'): debob(name); #deb(LInfo,name)
			else: 
				if tfalse(addst("singleline"))==True: labs[u'title']=labs[u'title'].replace('[CR]',' ')
				try: _addon.add_directory(pars, labs, img=img, fanart=fimg, contextmenu_items=contextMenuItems, total_items=ItemCount)
				except: pass
			#if (tfalse(addst("Notyetaired"))==True) or (LInfo is not 'Not yet aired'):
			#	_addon.add_directory(pars, labs, img=img, fanart=fimg, contextmenu_items=contextMenuItems, total_items=ItemCount)
	else: deb('Error','no items found.')
	if (ps('LI.nextpage.check') in html_last): 
		if (_debugging==True): print 'A next-page has been found.'
		nextpage=re.findall(ps('LI.nextpage.match'), html_last)[0] #nextpage=re.compile('<li class="next"><a href="http://www.solarmovie.so/.+?.html?page=(\d+)"></a></li>').findall(html_last)[0]
		if (int(nextpage) <= last) and (end < last) and (start < last) and (start is not int(nextpage)): #(int(nextpage) > end) and (int(nextpage) <= last): # and (end < last): ## Do Show Next Page Link ##
			if (_debugging==True): print 'A next-page is being added.'
			#print {'mode': 'GetTitles', 'url': url, 'pageno': nextpage, 'pagecount': numOfPages}
			nextLastPage=str(int(nextpage)+int(numOfPages)-1)
			if nextLastPage==nextpage: nextLastPage=""
			else: nextLastPage="-"+nextLastPage
			try: _addon.add_directory({'mode': 'GetTitles', 'section': section, 'url': url, 'pageno': nextpage, 'pagecount': numOfPages}, {'title': addst("text-page-next","[COLOR goldenrod]  >  [COLOR red]Next[/COLOR]...[/COLOR][COLOR blue] %s%s[/COLOR]") % (str(nextpage),nextLastPage)}, img=ps('img_next'))
			except: pass
			#print {'start':str(start),'end':str(end),'last':str(last),'nextpage':str(nextpage)}
			if ' Last </a></li>' in html_last:
				#myNote('test',':'+str(last)+':')
				if (int(startPage) <  9) and (int(LPnum) > 10): i=10; _addon.add_directory({'mode': 'GetTitles', 'section': section, 'url': url, 'pageno': i, 'pagecount': numOfPages}, {'title': addst("text-page-forward-to","[COLOR goldenrod]  >>  [COLOR red][/COLOR]...[/COLOR][COLOR blue] %s[/COLOR]") % str(i)}, img=ps('img_next'))
				if (int(startPage) < 19) and (int(LPnum) > 20): i=20; _addon.add_directory({'mode': 'GetTitles', 'section': section, 'url': url, 'pageno': i, 'pagecount': numOfPages}, {'title': addst("text-page-forward-to","[COLOR goldenrod]  >>  [COLOR red][/COLOR]...[/COLOR][COLOR blue] %s[/COLOR]") % str(i)}, img=ps('img_next'))
				if (int(startPage) < 29) and (int(LPnum) > 30): i=30; _addon.add_directory({'mode': 'GetTitles', 'section': section, 'url': url, 'pageno': i, 'pagecount': numOfPages}, {'title': addst("text-page-forward-to","[COLOR goldenrod]  >>  [COLOR red][/COLOR]...[/COLOR][COLOR blue] %s[/COLOR]") % str(i)}, img=ps('img_next'))
				if (int(startPage) < 39) and (int(LPnum) > 40): i=40; _addon.add_directory({'mode': 'GetTitles', 'section': section, 'url': url, 'pageno': i, 'pagecount': numOfPages}, {'title': addst("text-page-forward-to","[COLOR goldenrod]  >>  [COLOR red][/COLOR]...[/COLOR][COLOR blue] %s[/COLOR]") % str(i)}, img=ps('img_next'))
				if (int(startPage) < 49) and (int(LPnum) > 50): i=50; _addon.add_directory({'mode': 'GetTitles', 'section': section, 'url': url, 'pageno': i, 'pagecount': numOfPages}, {'title': addst("text-page-forward-to","[COLOR goldenrod]  >>  [COLOR red][/COLOR]...[/COLOR][COLOR blue] %s[/COLOR]") % str(i)}, img=ps('img_next'))
				if (int(startPage) < 59) and (int(LPnum) > 60): i=60; _addon.add_directory({'mode': 'GetTitles', 'section': section, 'url': url, 'pageno': i, 'pagecount': numOfPages}, {'title': addst("text-page-forward-to","[COLOR goldenrod]  >>  [COLOR red][/COLOR]...[/COLOR][COLOR blue] %s[/COLOR]") % str(i)}, img=ps('img_next'))
				if (int(startPage) < 69) and (int(LPnum) > 70): i=70; _addon.add_directory({'mode': 'GetTitles', 'section': section, 'url': url, 'pageno': i, 'pagecount': numOfPages}, {'title': addst("text-page-forward-to","[COLOR goldenrod]  >>  [COLOR red][/COLOR]...[/COLOR][COLOR blue] %s[/COLOR]") % str(i)}, img=ps('img_next'))
				if (int(startPage) < 79) and (int(LPnum) > 80): i=80; _addon.add_directory({'mode': 'GetTitles', 'section': section, 'url': url, 'pageno': i, 'pagecount': numOfPages}, {'title': addst("text-page-forward-to","[COLOR goldenrod]  >>  [COLOR red][/COLOR]...[/COLOR][COLOR blue] %s[/COLOR]") % str(i)}, img=ps('img_next'))
				if (int(startPage) < 89) and (int(LPnum) > 90): i=90; _addon.add_directory({'mode': 'GetTitles', 'section': section, 'url': url, 'pageno': i, 'pagecount': numOfPages}, {'title': addst("text-page-forward-to","[COLOR goldenrod]  >>  [COLOR red][/COLOR]...[/COLOR][COLOR blue] %s[/COLOR]") % str(i)}, img=ps('img_next'))
				try: _addon.add_directory({'mode': 'GetTitles', 'section': section, 'url': url, 'pageno': LPnum, 'pagecount': numOfPages}, {'title':addst("text-page-last","[COLOR goldenrod]  >>  [COLOR red]Last[/COLOR]...[/COLOR][COLOR blue] %s[/COLOR]") % str(LPnum)}, img=ps('img_next'))
				except: pass
				
				
	set_view(ps('content_tvshows'),addst('anime-view')); eod(); return
	################################################################################

##def listItems(section=_default_section_, url='', html='', episode=False, startPage='1', numOfPages='1', genre='', year='', stitle=''): # List: Movies or TV Shows
def listItems_OLD(section=_default_section_, url='', startPage='1', numOfPages='1', genre='', year='', stitle='', season='', episode='', html='', chck=''): # List: Movies or TV Shows
	if (url==''): return
	#if (chck=='Latest'): url=url+chr(35)+'latest'
	WhereAmI('@ the Item List -- url: %s' % url)
	if (tfalse(addst('customproxy','false'))==True) and (len(addst('proxy','')) > 9): Proxy=addst('proxy','')
	else: Proxy="" #ps('proxy')
	start=int(startPage); end=(start+int(numOfPages)); html=''; html_last=''; nextpage=startPage; deb('page start',str(start)); deb('page end',str(end))
	cookie_file=xbmc.translatePath(os.path.join(_addonPath,'temp.cache.txt'))
	try: 
		if isFile(cookie_file)==True: html_=nURL(url,headers={'Referer':_domain_url},cookie_file=cookie_file,load_cookie=True,save_cookie=True)
		else: html_=nURL(url,headers={'Referer':_domain_url},proxy=Proxy,cookie_file=cookie_file,save_cookie=True)
	except: html_=''
	#debob(html_)
	#try: html_=net.http_GET(url).content
	#except: 
	#	try: html_=getURL(url)
	#	except: 
	#		try: html_=getURLr(url,_domain_url)
	#		except: html_=''
	#print html_
	if (html_=='') or (html_=='none') or (html_==None): 
		deb('Error','Problem with page'); deadNote('Results:  '+section,'No results were found.')
		return
	deb('length of html_',str(len(html_))); 
	#try:		last=int(re.compile('<li><a href="http://.+?page=\d+">(\d+)</a></li>[\n]\s+<li class="next">', re.IGNORECASE | re.DOTALL).findall(html_))[0]
	try:		last=int(re.compile('<li><a href="http://.+?page=\d+">(\d+)</a></li>\*s\n*\s*<li><a href="http://.+?page=\d+">&rsaquo;\s*Next\s*</a></li>').findall(html_))[0]
	except:	last=2
	deb('number of pages',str(last))
	#print min(last,end)
	if ('<h1>Nothing was found by your request</h1>' in html_):
		deadNote('Results:  '+section,'Nothing was found by your request'); eod(); return
	pmatch=re.findall(ps('LI.page.find'), html_)
	if pmatch: last=pmatch[-1]
	if ('?' in url):	urlSplitter='&page='; deb('urlSplitter',urlSplitter) ## Quick fix for urls that already have '?' in it.
	else:							urlSplitter='?page='; deb('urlSplitter',urlSplitter)
	for page in range(start,min(last,end)):
		if (int(page)> 1): #if (int(startPage)> 1):
			if ('&page=' in url): pageUrl=url.replace('&page=','&pagenull=')+'&page='+str(page) ## Quick fix.
			if ('?page=' in url): pageUrl=url.replace('?page=','?pagenull=')+'&page='+str(page) ## Quick fix.
			else: pageUrl=url+urlSplitter+str(page) #ps('LI.page.param')+startPage
		else: pageUrl=url
		deb('item listings for',pageUrl)
		try: 
			try: 
				if isFile(cookie_file)==True: html_last=nURL(pageUrl,headers={'Referer':_domain_url},proxy=Proxy,cookie_file=cookie_file,load_cookie=True,save_cookie=True)
				else: html_last=nURL(pageUrl,headers={'Referer':_domain_url},proxy=Proxy,cookie_file=cookie_file,save_cookie=True)
			#try: html_last=net.http_GET(pageUrl).content
			#except: 
			except: 
				try:
					if isFile(cookie_file)==True: html=nURL(url,headers={'Referer':_domain_url},proxy=Proxy,cookie_file=cookie_file,load_cookie=True,save_cookie=True)
					else: html=nURL(url,headers={'Referer':_domain_url},proxy=Proxy,cookie_file=cookie_file,save_cookie=True)
				#try: html_=getURL(url)
				except: t=''
			if (_shoDebugging==True) and (html_last==''): deadNote('Testing','html_last is empty')
			if (html_last in html): t=''
			else: html=html+'\r\n'+html_last; deb('length of html_last',str(len(html_last))); 
			##if (_debugging==True): print html_last
		except: t=''
	if (ps('LI.nextpage.check') in html_last): 
		if (_debugging==True): print 'A next-page has been found.'
		nextpage=re.findall(ps('LI.nextpage.match'), html_last)[0] #nextpage=re.compile('<li class="next"><a href="http://www.solarmovie.so/.+?.html?page=(\d+)"></a></li>').findall(html_last)[0]
		if (int(nextpage) <= last) and (end < last) and (start < last) and (start is not int(nextpage)): #(int(nextpage) > end) and (int(nextpage) <= last): # and (end < last): ## Do Show Next Page Link ##
			if (_debugging==True): print 'A next-page is being added.'
			#print {'mode': 'GetTitles', 'url': url, 'pageno': nextpage, 'pagecount': numOfPages}
			_addon.add_directory({'mode': 'GetTitles', 'section': section, 'url': url, 'pageno': nextpage, 'pagecount': numOfPages}, {'title': ps('LI.nextpage.name')}, img=ps('img_next'))
			#print {'start':str(start),'end':str(end),'last':str(last),'nextpage':str(nextpage)}
	###	### _addon.add_directory({'mode': 'GetTitles', 'url': url, 'startPage': str(end), 'numOfPages': numOfPages}, {'title': 'Next...'})
	###html=nolines(html)
	html=ParseDescription(html); html=remove_accents(html) #if (_debugging==True): print html
	html=messupText(html,_html=True,_ende=True,_a=False,Slashes=False)
	deb('Length of HTML',str(len(html))); debob(html); 
	temp_file=xbmc.translatePath(os.path.join(_addonPath,'temp.html.items.txt'))
	if (_debugging==True) and (_testing==True):
		try: my_tools._SaveFile(temp_file,html)
		except: pass
	######
	if (len(html)==0): deb('Error','html is empty.'); return
	#s='<a\n*\s*href="(/'+ps('common_word')+'/[A-Za-z0-9\-/_]+)"\n*\s*title=\'(.*?)\'\n*\s*/*>\n*\s*(.+?)\s*\n*\s*</a>'
	#s='<a\n*\s*href="(/'+ps('common_word')+'/[A-Za-z0-9\-/_]+)"\n*\s*title=\'(.*?)\'\n*\s*/*>\s*\n*\s*(.+?)\s*\n*\s*</a>\s*\n*\s*\n*\s*</td>\s*\n*\s*<td>\s*\n*\s*(.*?)\s*\n*\s*</td>\s*\n*\s*</tr>'
	s='<a\n*\s*href="(/'+ps('common_word')+'/[A-Za-z0-9\-/_]+)"\n*\s*title=\'(.*?)\'\n*\s*[/]*>\s*\n*\s*(.+?)\s*\n*\s*</a>\s*\n*\s*\n*\s*(.*?)\s*\n*\s*\n*\s*</td>\s*\n*\s*<td>\s*\n*\s*(.+?)\s*\n*\s*</td>\s*\n*\s*</tr>'
	## ## http://kissanime.com/M
	## ## <article class="underline" alink="/M/Anime/Pupa"><div class="post-preview"><a href="/M/Anime/Pupa"><img src="http://kissanime.com/Uploads/Etc/9-15-2013/61078454554395l.jpg"/></a></div><div class="post-content"><h2><a href="/M/Anime/Pupa">Pupa</a></h2><p>Episode 001</p><div class="date"><span class="bggreen">Ongoing</span></div></div><div class="clear"></div></article>
	## s='<article class="underline" alink=".+?"><div class="post-preview"><a href="/M(/Anime/.+?)"><img src="(http://kissanime.com/Uploads/Etc/[0-9\-]+/[0-9]+.jpg)"/></a></div><div class="post-content"><h2><a href=".+?">(.+?)</a></h2><p>(.+?)</p><div class="date"><span class="\D+">(.+?)</span></div></div><div class="clear"></div></article>'
	#s2=''
	#s1=[s,s2]
	#for s in s1:
	iitems=re.compile(s, re.DOTALL).findall(html) ### , re.MULTILINE | re.IGNORECASE | re.DOTALL
	if (iitems is not None):
		ItemCount=len(iitems) # , total_items=ItemCount
		deb('# of items',str(ItemCount)); debob(iitems); 
		EnableMeta=tfalse(addst("enableMeta"))
		#for item_url, tInfo, name in iitems:
		for item_url, tInfo, name, imInfo, LInfo in iitems:
			contextMenuItems=[]; item_url=_domain_url+item_url; labs={}; LInfo=LInfo.strip()
			try: img=re.compile('"(http://.+?\.jpg)"').findall(tInfo)[0].replace(' ','%20')
			except: img=_artIcon
			fimg=''+img
			if ('<p>' in tInfo) and ('</p>' in tInfo):
				try: labs['plot']=re.compile('<p>\s*\n*\s*(.+?)\s*\n*\s*</p>').findall(tInfo)[0].strip()
				except: labs['plot']=''
			else: labs['plot']=''
			if (LInfo=='Completed') or (LInfo=='Not yet aired'):
				labs['plot']='['+cFL(LInfo,'lime')+'][CR]'+labs['plot']
			#if ('<img' in imInfo): labs['plot']=imInfo.strip().replace(' style="vertical-align: middle"','').replace(' title="Just updated"','').replace(' title="Popular anime"','').replace(' />','>').replace('src="../','src="'+_domain_url+'/').replace('../','').replace('">','[/IMG]').replace('<img src="','[IMG]')+'[CR]'+labs['plot'] #.replace('>',']').replace('<img ','[IMG ')
			#
			#
			#
			if (tfalse(addst("Notyetaired"))==False) and (LInfo=='Not yet aired'): t=''
			elif (EnableMeta==True):
				animetype='tvshow'; animename=''+name
				animename.replace(' (Dub)','').replace(' (Sub)','').replace(' (TV)','').replace(' OVA','').replace(' Movies','').replace(' Movie','').replace(' Specials','').replace(' New','')
				##.replace('','')
				#
				mlabs=GRABMETA(animename,'tvshow')
				mlabsMovie=GRABMETA(animename,'movie')
				##mlabs=GRABMETA(animename,animetype)
				##mlabs=GRABMETA('the walking dead',animetype)
				#print 'mlabs'; print mlabs
				#print 'mlabsMovie'; print mlabsMovie
				##if (mlabs['backdrop_url'] is not None): fimg=mlabs['backdrop_url']
				if (len(mlabs['backdrop_url']) > 0): 
					fimg=mlabs['backdrop_url']
					labs['rating']=mlabs['rating']
				elif (len(mlabsMovie['backdrop_url']) > 0): 
					fimg=mlabsMovie['backdrop_url']
					labs['rating']=mlabsMovie['rating']
				if (len(mlabs['cover_url']) > 0): img=mlabs['cover_url']
				elif (len(mlabsMovie['cover_url']) > 0): img=mlabsMovie['cover_url']
				#labs['poster_url']=img
				#labs['poster']=img
				#labs['cover']=img
				if (len(mlabs['cast']) > 0): labs['cast']=mlabs['cast']
				elif (len(mlabsMovie['cast']) > 0): labs['cast']=mlabsMovie['cast']
				#print 'cast'; print labs['cast']
				if (len(mlabs['genre']) > 0): labs['genre']=mlabs['genre']
				elif (len(mlabsMovie['genre']) > 0): labs['genre']=mlabsMovie['genre']
				if (len(mlabs['studio']) > 0): labs['studio']=mlabs['studio']
				#elif (len(mlabsMovie['studio']) > 0): labs['studio']=mlabsMovie['studio']
				if (len(mlabs['banner_url']) > 0): 
					labs['banner_url']=mlabs['banner_url']
					labs['banner']=mlabs['banner_url']
				if (len(mlabsMovie['thumb_url']) > 0): labs['thumb_url']=mlabsMovie['thumb_url']
				if (mlabsMovie['year'] > 0): labs['year']=mlabsMovie['year']
				if (len(mlabsMovie['tmdb_id']) > 0): labs['tmdb_id']=mlabsMovie['tmdb_id']
				if (len(mlabsMovie['director']) > 0): labs['director']=mlabsMovie['director']
				if (len(mlabsMovie['writer']) > 0): labs['writer']=mlabsMovie['writer']
				if (len(mlabs['mpaa']) > 0): labs['mpaa']=mlabs['mpaa']
				elif (len(mlabsMovie['mpaa']) > 0): labs['mpaa']=mlabsMovie['mpaa']
				if (len(mlabsMovie['duration']) > 0): labs['duration']=mlabsMovie['duration']
				if (len(mlabs['status']) > 0): labs['status']=mlabs['status']
				#
				
				if (len(mlabs['title']) > 0): labs['showtitle']=mlabs['title']
				elif (len(mlabsMovie['title']) > 0): labs['showtitle']=mlabsMovie['title']
				if (len(mlabs['premiered']) > 0): labs['premiered']=mlabs['premiered']
				elif (len(mlabsMovie['premiered']) > 0): labs['premiered']=mlabsMovie['premiered']
				if (mlabs['overlay'] is not 6): labs['overlay']=mlabs['overlay']
				#elif (mlabsMovie['overlay'] is not 6): labs['overlay']=mlabsMovie['overlay']
				else: labs['overlay']=6
				if (len(mlabs['duration']) > 0): labs['duration']=mlabs['duration']
				elif (len(mlabsMovie['duration']) > 0): labs['duration']=mlabsMovie['duration']
				
				if (len(mlabs['imdb_id']) > 0): labs['imdb_id']=mlabs['imdb_id']
				elif (len(mlabsMovie['imdb_id']) > 0): labs['imdb_id']=mlabsMovie['imdb_id']
				if (len(mlabs['tvdb_id']) > 0): labs['tvdb_id']=mlabs['tvdb_id']
				if (len(mlabsMovie['tmdb_id']) > 0): labs['tmdb_id']=mlabsMovie['tmdb_id']
				
				if (len(mlabs['plot']) > 0):
					if (len(labs['plot']) > 0): labs['plot']+='[CR][CR]'+mlabs['plot']
					else: labs['plot']=mlabs['plot']
				elif (len(mlabsMovie['plot']) > 0):
					if (len(labs['plot']) > 0): labs['plot']+='[CR][CR]'+mlabsMovie['plot']
					else: labs['plot']=mlabsMovie['plot']
				labs['plot']=messupText(labs['plot'],_html=True,_ende=True,_a=False,Slashes=False)
				if (len(mlabsMovie['tagline']) > 0): labs['tagline']=mlabsMovie['tagline']
				if (len(mlabsMovie['votes']) > 0): labs['votes']=mlabsMovie['votes']
				if (len(mlabsMovie['trailer_url']) > 0): labs['trailer_url']=mlabsMovie['trailer_url']
				
				
				#
				### Movies
				#'rating': meta['rating'],
				#'duration': meta['duration'],
				#'genre': meta['genre'],
				#'mpaa':"rated %s"%meta['mpaa'],
				#'plot': meta['plot'],
				#'title': meta['title'],
				#'writer': meta['writer'],
				#'cover_url': meta['cover_url'],
				#'director': meta['director'],
				#'cast': meta['cast'],
				#'backdrop': meta['backdrop_url'],
				#'backdrop_url': meta['backdrop_url'],
				#'tmdb_id': meta['tmdb_id'],
				#'year': meta['year'],
				#'votes': meta['votes'],
				#'tagline': meta['tagline'],
				#'premiered': meta['premiered'],
				#'trailer_url': meta['trailer_url'],
				#'studio': meta['studio']
				#'imdb_id': meta['imdb_id'],
				### TV Shows
				#'rating': meta['rating'],
				#'genre': meta['genre'],
				#'mpaa':"rated %s"%meta['mpaa'],
				#'plot': meta['plot'],
				#'title': meta['title'],
				#'cover_url': meta['cover_url'],
				#'cast': meta['cast'],
				#'studio': meta['studio'],
				#'banner_url': meta['banner_url'],
				#'backdrop_url': meta['backdrop_url'],
				#'status': meta['status'],
				#'premiered': meta['premiered'],
				#'imdb_id': meta['imdb_id'],
				#'tvdb_id': meta['tvdb_id'],
				#'year': meta['year'],
				#'imgs_prepacked': meta['imgs_prepacked'],
				#'overlay': meta['overlay'],
				#'duration': meta['duration']
				#
				#infoLabels={'rating': meta['rating'],'duration': meta['duration'],'genre': meta['genre'],'mpaa':"rated %s"%meta['mpaa'],'plot': meta['plot'],'title': meta['title'],'writer': meta['writer'],'cover_url': meta['cover_url'],'director': meta['director'],'cast': meta['cast'],'backdrop': meta['backdrop_url'],'backdrop_url': meta['backdrop_url'],'tmdb_id': meta['tmdb_id'],'year': meta['year'],'votes': meta['votes'],'tagline': meta['tagline'],'premiered': meta['premiered'],'trailer_url': meta['trailer_url'],'studio': meta['studio']}
				##infoLabels={'rating': meta['rating'],'duration': meta['duration'],'genre': meta['genre'],'mpaa':"rated %s"%meta['mpaa'],'plot': meta['plot'],'title': meta['title'],'writer': meta['writer'],'cover_url': meta['cover_url'],'director': meta['director'],'cast': meta['cast'],'backdrop_url': meta['backdrop_url'],'backdrop_url': meta['backdrop_url'],'tmdb_id': meta['tmdb_id'],'year': meta['year']}
				#infoLabels={'rating': meta['rating'],'genre': meta['genre'],'mpaa':"rated %s"%meta['mpaa'],'plot': meta['plot'],'title': meta['title'],'cover_url': meta['cover_url'],'cast': meta['cast'],'studio': meta['studio'],'banner_url': meta['banner_url'],'backdrop_url': meta['backdrop_url'],'status': meta['status'],'premiered': meta['premiered'],'imdb_id': meta['imdb_id'],'tvdb_id': meta['tvdb_id'],'year': meta['year'],'imgs_prepacked': meta['imgs_prepacked'],'overlay': meta['overlay'],'duration': meta['duration']}
				##infoLabels={'rating': meta['rating'],'genre': meta['genre'],'mpaa':"rated %s"%meta['mpaa'],'plot': meta['plot'],'title': meta['title'],'cover_url': meta['cover_url'],'cast': meta['cast'],'studio': meta['studio'],'banner_url': meta['banner_url'],'backdrop_url': meta['backdrop_url'],'status': meta['status']}
				#
				#
				#if (len(mlabs['rating']) > 0): labs['rating']=mlabs['rating']
				#elif (len(mlabsMovie['rating']) > 0): labs['rating']=mlabsMovie['rating']
				#if (len(mlabs['rating']) > 0): labs['rating']=mlabs['rating']
				#elif (len(mlabsMovie['rating']) > 0): labs['rating']=mlabsMovie['rating']
				
				
				if (len(labs['plot'])==0) and (len(mlabs['plot']) > 0): labs['plot']=mlabs['plot']
				elif (len(labs['plot'])==0) and (len(mlabsMovie['plot']) > 0): labs['plot']=mlabsMovie['plot']
				
			#
			#mlabs['']  mlabs['backdrop_url']
			#try: img=re.compile('("http://kissanime.com/Uploads/Etc/[0-9\-]+/[0-9]+[A-Za-z0-9\-_/\s]*.jpg)"').findall(tInfo)[0]
			labs['title']=name.replace(' (Dub)',' [COLOR green](Dub)[/COLOR]').replace(' (Sub)',' [COLOR blue](Sub)[/COLOR]').replace(' OVA',' [COLOR red]OVA[/COLOR]').replace(' Movie',' [COLOR maroon]Movie[/COLOR]').replace(': ',':[CR] ').replace(' New',' [COLOR yellow]New[/COLOR]').replace(' (TV)',' [COLOR cornflowerblue](TV)[/COLOR]').replace(' Specials',' [COLOR deeppink]Specials[/COLOR]') #.replace('','')
			deb('title',labs['title']); deb('url',item_url); deb('img',img); deb('fanart',fimg)
			#deb('plot',labs['plot']); 
			if ('</a>' in LInfo):
				deb('LInfo',LInfo)
				(LatestUrl,LatestName)=re.compile('<a href="(/'+ps('common_word')+'/.+?)">\s*\n*\s*(.+?)\s*\n*\s*</a>').findall(LInfo)[0]
				LatestUrl=_domain_url+LatestUrl
				LatestPar={'url':LatestUrl,'mode':'GetLinks','img':img,'fanart':fimg,'title':labs['title'].replace('[CR]','')+' - '+LatestName}
				contextMenuItems.append(('Latest:  '+LatestName,'XBMC.Container.Update(%s)' % _addon.build_plugin_url(LatestPar) ))
				#pars={'mode':'GetLinks','img':img,'url':ep_url,'title':ep_name}
				#contextMenuItems.append((ps('cMI.favorites.tv.add.name')+' '+addst('fav.movies.1.name'),ps('cMI.favorites.movie.add.url') % (sys.argv[0],ps('cMI.favorites.tv.add.mode'),section,urllib.quote_plus(name),'',urllib.quote_plus(img),urllib.quote_plus(fimg),urllib.quote_plus(''),urllib.quote_plus(labs['plot']),urllib.quote_plus(''),urllib.quote_plus(item_url), '' )))
			##### Right Click Menu for: Anime #####
			contextMenuItems.append((ps('cMI.showinfo.name'),ps('cMI.showinfo.url')))
			contextMenuItems.append((ps('cMI.favorites.tv.add.name')+' '+addst('fav.movies.1.name'),ps('cMI.favorites.movie.add.url') % (sys.argv[0],ps('cMI.favorites.tv.add.mode'),section,urllib.quote_plus(name),'',urllib.quote_plus(img),urllib.quote_plus(fimg),urllib.quote_plus(''),urllib.quote_plus(labs['plot']),urllib.quote_plus(''),urllib.quote_plus(item_url), '' )))
			if (tfalse(addst("enable-fav-movies-2"))==True): contextMenuItems.append((ps('cMI.favorites.tv.add.name')+' '+addst('fav.movies.2.name'),ps('cMI.favorites.movie.add.url') % (sys.argv[0],ps('cMI.favorites.tv.add.mode'),section,urllib.quote_plus(name),'',urllib.quote_plus(img),urllib.quote_plus(fimg),urllib.quote_plus(''),urllib.quote_plus(labs['plot']),urllib.quote_plus(''),urllib.quote_plus(item_url),'2' )))
			if (tfalse(addst("enable-fav-movies-3"))==True): contextMenuItems.append((ps('cMI.favorites.tv.add.name')+' '+addst('fav.movies.3.name'),ps('cMI.favorites.movie.add.url') % (sys.argv[0],ps('cMI.favorites.tv.add.mode'),section,urllib.quote_plus(name),'',urllib.quote_plus(img),urllib.quote_plus(fimg),urllib.quote_plus(''),urllib.quote_plus(labs['plot']),urllib.quote_plus(''),urllib.quote_plus(item_url),'3' )))
			if (tfalse(addst("enable-fav-movies-4"))==True): contextMenuItems.append((ps('cMI.favorites.tv.add.name')+' '+addst('fav.movies.4.name'),ps('cMI.favorites.movie.add.url') % (sys.argv[0],ps('cMI.favorites.tv.add.mode'),section,urllib.quote_plus(name),'',urllib.quote_plus(img),urllib.quote_plus(fimg),urllib.quote_plus(''),urllib.quote_plus(labs['plot']),urllib.quote_plus(''),urllib.quote_plus(item_url),'4' )))
			##if (labs['fanart'] is not ''): contextMenuItems.append(('Download Wallpaper', 'XBMC.RunPlugin(%s)' % _addon.build_plugin_url( { 'mode': 'Download' , 'section': ps('section.wallpaper') , 'studio': name+'  ('+year+')' , 'img': labs['thumbnail'] , 'url': labs['fanart'] } ) ))
			##contextMenuItems.append(('Add - Library','XBMC.RunPlugin(%s?mode=%s&section=%s&title=%s&showtitle=%s&showyear=%s&url=%s&img=%s)' % ( sys.argv[0],'LibrarySaveMovie',section, urllib.quote_plus(name), urllib.quote_plus(name), urllib.quote_plus(year), urllib.quote_plus(_domain_url+item_url), urllib.quote_plus(thumbnail))))
			##if os.path.exists(xbmc.translatePath(ps('special.home.addons'))+ps('cMI.1ch.search.folder')):
			##	contextMenuItems.append((ps('cMI.1ch.search.name'), 					ps('cMI.1ch.search.url') 				% (ps('cMI.1ch.search.plugin'), 			ps('cMI.1ch.search.section'), 			name)))
			##if os.path.exists(xbmc.translatePath(ps('special.home.addons'))+ps('cMI.primewire.search.folder')):
			##	contextMenuItems.append((ps('cMI.primewire.search.name'), 		ps('cMI.primewire.search.url') 	% (ps('cMI.primewire.search.plugin'), ps('cMI.primewire.search.section'), name)))
			##### Right Click Menu for: Anime ##### /\ #####
			pars={'mode':'GetEpisodes','url':item_url,'img':img,'title':labs['title']}
			#deb('LInfo',LInfo)
			if (tfalse(addst("Notyetaired"))==False) and (LInfo=='Not yet aired'): deb(LInfo,name)
			else: 
				if tfalse(addst("singleline"))==True: labs['title']=labs['title'].replace('[CR]',' ')
				try: _addon.add_directory(pars, labs, img=img, fanart=fimg, contextmenu_items=contextMenuItems, total_items=ItemCount)
				except: pass
			#if (tfalse(addst("Notyetaired"))==True) or (LInfo is not 'Not yet aired'):
			#	_addon.add_directory(pars, labs, img=img, fanart=fimg, contextmenu_items=contextMenuItems, total_items=ItemCount)
	else: deb('Error','no items found.')
	set_view(ps('content_tvshows'),addst('anime-view')); eod(); return
	################################################################################

def listEpisodes(section, url, img='', showtitle='', season=''): #_param['img']
	xbmcplugin.setContent( int( sys.argv[1] ), 'episodes' ); WhereAmI('@ the Episodes List for TV Show -- url: %s' % url); debob(showtitle); 
	#try: html=net.http_GET(url).content
	cookie_file=xbmc.translatePath(os.path.join(_addonPath,'temp.cache.txt'))
	#,proxy=ps('proxy')
	try: 
		if isFile(cookie_file)==True: html=nURL(url,headers={'Referer':_domain_url},cookie_file=cookie_file,load_cookie=True,save_cookie=True)
		else: html=nURL(url,headers={'Referer':_domain_url},cookie_file=cookie_file,save_cookie=True)
	except: html=''
	addstv(id="LastShowListedURL", value=url)
	addstv(id="LastShowListedIMG", value=img)
	addstv(id="LastShowListedNAME", value=showtitle)
	fimg=addpr("fanart",img)
	addstv(id="LastShowListedFANART", value=fimg)
	metadata_tv_episodes=tfalse(addst("metadata_tv_episodes")); metadata_tv_ep_plot=tfalse(addst("metadata_tv_ep_plot"))
	if (html=='') or (html=='none') or (html==None): deb('Html','is empty.' ); return
	##s='<img src="../../Content/images/bullet.png" />&nbsp;<a href="(/Anime/.+?)"><b>(.+?)</b></a><div class="clear" style="height:5px"></div>'
	#s='<img src="../../Content/images/bullet.png"\s*/>\s*<a href="(/Anime/.+?)"><b>(.+?)</b></a><div class="clear" style="height:5px"></div>'
	s='<img src="../../Content/images/bullet.png"\s*/>\s*<a href="(/'+ps('common_word')+'/[A-Za-z0-9\-/_]+)"\s*>\s*<b>(.+?)</b>\s*</a>\s*<div class="clear" style="height:5px">\s*</div>'
	
	#  <img src="../../Content/images/bullet.png"/>      <a href="            "><b>     </b></a><div class="clear" style="height:5px"></div>
	try:		relatedshows=re.compile(s, re.DOTALL).findall(html.replace('&nbsp;',' '))
	except:	relatedshows=''
	
	html=messupText(html,_html=True,_ende=True,_a=False,Slashes=False)
	temp_file=xbmc.translatePath(os.path.join(_addonPath,'temp.html.episodes.txt'))
	if (_debugging==True) and (_testing==True):
		try: my_tools._SaveFile(temp_file,html)
		except: pass
	#
	try:		BookmarkID=re.compile('type:\s*"POST",\s*\n*\s*url:\s*"/Bookmark/(\d+)/remove"', re.DOTALL).findall(html)[0]
	except:	BookmarkID=''
	if (img==''): img=_artIcon
	s='<tr>\s*\n*\s*<td>\s*\n*\s*<a\s*\n*\s*\s*\n*\s*.*?href="(/'+ps('common_word')+'/.+?\?id=[0-9]+)"\s*\n*\s*title="\D*\s*'+ps('common_word2')+' .+?"\s*\n*\s*>\s*\n*\s*(.+?)\s*\n*\s*</a>\s*\n*\s*</td>\s*\n*\s*<td>\s*\n*\s*([0-9/]*)\s*\n*\s*</td>'
	try:		episodes=re.compile(s, re.DOTALL).findall(html)
	except:	episodes=''
	#debob(episodes); 
	if (not episodes) or (episodes==None) or (episodes==False) or (episodes==''): ItemCount=0; deb('Episodes','couldn\'t find episodes'); #eod(); return
	else: ItemCount=len(episodes) # , total_items=ItemCount
	#
	xRP='XBMC.RunPlugin(%s)'
	#xRP='XBMC.Container.Update(%s)'
	#BMa=( cFL('Add Online Bookmark',  'lime') , xRP % _addon.build_plugin_url({'url':url+'/Bookmark/'+BookmarkID+'/add',   'mode':'Bookmarks','section':section}) )
	#BMr=( cFL('Remove Online Bookmark','red') , xRP % _addon.build_plugin_url({'url':url+'/Bookmark/'+BookmarkID+'/remove','mode':'Bookmarks','section':section}) )
	BMa=( cFL('Add Online Bookmark',  'lime') , xRP % _addon.build_plugin_url({'url':_domain_url+'/Bookmark/'+BookmarkID+'/add',   'mode':'Bookmarks','section':section}) )
	BMr=( cFL('Remove Online Bookmark','red') , xRP % _addon.build_plugin_url({'url':_domain_url+'/Bookmark/'+BookmarkID+'/remove','mode':'Bookmarks','section':section}) )
	#BMa=( cFL('Add Online Bookmark',  'lime') , xRP % _addon.build_plugin_url({'url':_domain_url+'/Bookmark/'+BookmarkID+'/add',   'mode':'Bookmarks','section':section,'title':url}).replace('/?','/default.py?') )
	#BMr=( cFL('Remove Online Bookmark','red') , xRP % _addon.build_plugin_url({'url':_domain_url+'/Bookmark/'+BookmarkID+'/remove','mode':'Bookmarks','section':section,'title':url}).replace('/?','/default.py?') )
	#BMa=BMa.replace('/?','/default.py?')
	#BMr=BMr.replace('/?','/default.py?')
	debob([BMa,BMr]); 
	#
	EnableVisitedLeft=tfalse(addst("enable-visited-left-e"))
	EnableMeta=tfalse(addst("enableMeta"))
	EnableEpisodeMeta=tfalse(addst("episodeMeta"))
	if (EnableMeta==True): 
		s='1'; stitle=showtitle; 
		stitle=stitle.replace(addst("text-sub",' [COLOR blue](Sub)[/COLOR]'),'').replace(addst("text-dub",' [COLOR green](Dub)[/COLOR]'),'').replace(addst("text-ova",' [COLOR red]OVA[/COLOR]'),'').replace(addst("text-movie",' [COLOR maroon]Movie[/COLOR]'),'').replace(addst("text-colon",':[CR] '),':').replace(addst("text-new",' [COLOR yellow]New[/COLOR]'),'').replace(addst("text-tv",' [COLOR cornflowerblue](TV)[/COLOR]'),'').replace(addst("text-specials",' [COLOR deeppink]Specials[/COLOR]'),'').replace(" "+addst("text-hot","[COLOR fuchsia][[I]HOT [/I]][/COLOR]"),''); 
		#stitle=stitle.replace(' The Movie','').replace(' Movie','').replace(' Episode','').replace(' OVA','').replace(' _Special','').replace(' _Preview','').replace(' (Sub)','').replace(' (Dub)',''); 
		##labs[u'title']=name.replace(' (Dub)',addst("text-dub",' [COLOR green](Dub)[/COLOR]')).replace(' (Sub)',addst("text-sub",' [COLOR blue](Sub)[/COLOR]')).replace(' OVA',addst("text-ova",' [COLOR red]OVA[/COLOR]')).replace(' Movie',addst("text-movie",' [COLOR maroon]Movie[/COLOR]')).replace(': ',addst("text-colon",':[CR] ')).replace(' New',addst("text-new",' [COLOR yellow]New[/COLOR]')).replace(' (TV)',addst("text-tv",' [COLOR cornflowerblue](TV)[/COLOR]')).replace(' Specials',addst("text-specials",' [COLOR deeppink]Specials[/COLOR]')) #.replace('','')
		if stitle=='Golden Time': stitle+=' (2013)'
		#if stitle=='Witch Craft Works': stitle='Witch Craft Works (2014)'
		if stitle=='Perfect Blue': stitle+=' (1997)'
		if stitle=='Kingdom': stitle+=' (2012)'
		
		
		if '2' in showtitle: s='2'
		#s='All'
		if stitle=='Kingdom 2': stitle='Kingdom (2012)'; s='2'
		if stitle=='Weiss Survive R': stitle='Weiss Survive'; s='2'
		imdb_id=addpr("imdbid",""); vtype=addpr("type",""); deb('imdb_id',imdb_id); deb('vtype',vtype); labsShow={}; 
		if len(vtype)==0: vtype='episode'
		if (len(imdb_id)==0) or (len(imdb_id)==1): imdb_id=addpr("dbid",""); 
		if (len(imdb_id)==0) or (len(imdb_id)==1): 
			if vtype=='movie': stype='movie'
			else: stype='tvshow'
			try:		labsShow=GRABMETA(stitle,stype,overlay=6)
			except: labsShow={'imdb_id':''}
			imdb_id=labsShow[u'imdb_id']
		deb('imdb_id',imdb_id); deb('show title',stitle); 
		try: metaget=metahandlers.MetaData(); 
		except: pass
		#
	else: labsShow={}; imdb_id=''; 
	_addon.addon.setSetting(id="LastShowListedImdbID", value=imdb_id)
	eN3=0; showImg=img; showFanart=fimg
	# Status
	if tfalse(addst("show-ep-status","false"))==True:
		s4='<span class="info">Status:</span>'
		if s4 in html: s4+='\s*(\D+)\s*\n\s*<'; Status=re.compile(s4).findall(html.replace("&nbsp;"," "))[0]
		else: Status="Unknown"
		deb("Status",Status); _addon.add_directory({'mode':'System.ExecWait','url':url},{'title':cFL('Status: ','green')+cFL(str(Status),'lime')+"[CR]"+cFL(showtitle,'deepskyblue')},img=showImg,fanart=showFanart,is_folder=True)
	#
	if ItemCount > 0: 
		
		if (EnableEpisodeMeta==True) and (EnableMeta==True): episodes=episodes[::-1]
		elif tfalse(addst('episodeSort','false'))==True: episodes=episodes[::-1]
		if (len(episodes) > 80) and (EnableEpisodeMeta==True) and (EnableMeta==True) and (tfalse(addst('episodeLongListsMeta','false'))==False): EnableEpisodeMeta=False
		for ep_url, ep_name, ep_date in episodes:
			debob(ep_name); 
			contextMenuItems=[]; labs={}; ep_url=_domain_url+ep_url
			contextMenuItems.append(('Episode Information',ps('cMI.showinfo.url')))
			#contextMenuItems.append(('Add - Library','XBMC.RunPlugin(%s?mode=%s&section=%s&title=%s&showtitle=%s&showyear=%s&url=%s&img=%s&season=%s&episode=%s&episodetitle=%s)' % ( sys.argv[0],'LibrarySaveEpisode',section, urllib.quote_plus(_param['title']), urllib.quote_plus(_param['showtitle']), urllib.quote_plus(_param['year']), urllib.quote_plus(ep_url), urllib.quote_plus(labs['thumbnail']), urllib.quote_plus(season_number), urllib.quote_plus(episode_number), urllib.quote_plus(episode_name) )))
			labs[u'title']=''+ep_name; labs[u'backdrop_url']=img; labs[u'cover_url']=img; labs[u'plot']=''
			if visited_check(ep_name)==True: olay=7
			else: olay=6
			if (EnableEpisodeMeta==True) and (EnableMeta==True) and (vtype=='episode') and (len(imdb_id) > 2):
				#try:
				#if "episode " in ep_name.lower(): e_no="episode "+(ep_name.lower().split("episode ")[-1])
				#else: e_no=ep_name.lower()
				#e_no=str(int(ep_name)).lower().replace(showtitle,"").replace("episode 00","").replace("episode 0","").replace("episode ","").strip()
				#e_no=str(int(ep_name.lower().replace(showtitle,"").replace("episode 00","").replace("episode 0","").replace("episode ","").strip()))
				#e_no=ep_name.lower().split(' ')[-1]; 
				e_no=ep_name.lower(); 
				e_no=e_no.replace('(720p)','').replace('(1080p)','').replace('(480p)','').replace('(360p)','').replace('(280p)','').strip(); 
				if 'Episode ' in e_no: e_no=e_no.split('Episode ')[-1]; 
				elif 'Special ' in e_no: e_no=e_no.split('Special ')[-1]; 
				elif 'Movie ' in e_no: e_no=e_no.split('Movie ')[-1]; 
				elif 'Ova ' in e_no: e_no=e_no.split('Ova ')[-1]; 
				#else: e_no=ep_name.lower().split(' ')[-1]
				debob(e_no); 
				try: e_no=re.compile('(\d+[\-]*\d*)').findall(e_no)[0]; 
				except: e_no='0'
				try:
					if e_no[-1]=='-': e_no=e_no[0:len(e_no)-1]
				except: pass
				#if '- ' in e_no: e_no=e_no.split('- ')[0].strip()
				if ' (' in e_no: e_no=e_no.split(' (')[0]
				elif '(' in e_no: e_no=e_no.split('(')[0]
				e_no=e_no.replace(" 00","").replace(" 0","").strip()
				e_no=e_no.strip()
				if len(e_no)==0: e_no='0'; 
				if '-' in e_no: e_no=e_no.strip()
				else: 
					try: e_no=str(int(e_no)); 
					except: pass
				if str(e_no)=='1': s='1'; eN3=0; 
				if len(e_no)==0: e_no='0'; 
				debob(str(e_no)); 
				if '.' in e_no: eN4=""+e_no.split('.')[0]; eN5=""+e_no.split('.')[0]; 
				else: eN4=""+str(e_no); eN5=""+str(e_no); 
				if ' - ' in e_no: eN4=eN4.split(' - ')[0]; eN5=eN5.split(' - ')[1]; 
				if '-' in e_no: eN4=eN4.split('-')[0]; eN5=eN5.split('-')[1]; 
				eN4=eN4.strip(); eN5=eN5.strip(); 
				#deb('eN4',str(eN4)); deb('eN3',str(eN3)); 
				eN2=""+str(int(eN4)-int(eN3)); 
				
				
				#try: labs=metaget.get_episode_meta(tvshowtitle=stitle,imdb_id=imdb_id,season=s,episode=e_no,air_date='',episode_title='',overlay=6)
				try: labs=metaget.get_episode_meta(tvshowtitle=stitle,imdb_id=imdb_id,season=s,episode=eN2,air_date='',episode_title='',overlay=6)
				except: pass
				try: 
					if (len(labs['title'])==0) and (len(labs['plot'])==0) and (len(labs['episode_id'])==0):
						s=str(int(s)+1); eN3=int(eN5)-1; 
						eN2=""+str(int(eN4)-int(eN3)); 
						try: labs=metaget.get_episode_meta(tvshowtitle=stitle,imdb_id=imdb_id,season=s,episode=eN2,air_date='',episode_title='',overlay=6)
						except: pass
				except: pass
				
				
				
				debob(labs); 
				if len(labs[u'title'])==0: labs[u'title']=''+ep_name
				else: 
					if   len(e_no)==1: labs[u'title']='00'+str(e_no)+' - '+labs[u'title']
					elif len(e_no)==2: labs[u'title']='0'+str(e_no)+' - '+labs[u'title']
					elif len(e_no)==3: labs[u'title']=''+str(e_no)+' - '+labs[u'title']
					else: labs[u'title']=''+str(e_no)+' - '+labs[u'title']
				
				try: labs[u'title']=messupText(labs[u'title'],True,True,True)
				except: pass
				try: labs[u'plot']=messupText(labs[u'plot'],True,True,True)
				except: pass
				debob(labs); 
			else: imdb_id=''; 
			if ('[CR]' not in labs[u'title']): labs[u'title']=labs[u'title'].replace(' The Movie',' [CR]The Movie')
			if ('[CR]' not in labs[u'title']): labs[u'title']=labs[u'title'].replace(' Movie',' [CR]Movie')
			if ('[CR]' not in labs[u'title']): labs[u'title']=labs[u'title'].replace(' Episode',' [CR]Episode')
			if ('[CR]' not in labs[u'title']): labs[u'title']=labs[u'title'].replace(' OVA',' [CR]OVA')
			if ('[CR]' not in labs[u'title']): labs[u'title']=labs[u'title'].replace(' _Special',' [CR]Special')
			if ('[CR]' not in labs[u'title']): labs[u'title']=labs[u'title'].replace(' _Preview',' [CR]Preview')
			if ('[CR]' in labs[u'title']): labs[u'title']=labs[u'title'].split('[CR]')[1]
			#labs[u'title']=labs[u'title']+cFL('  ['+cFL(ep_date.replace('/',cFL('/','pink')),'blue')+']','pink')
			try: (labs['month'],labs['day'],labs['year'])=ep_date.split('/')
			except: labs['month']=''; labs['day']; labs['year']
			mdy=cFL('  ['+cFL(labs['month'],'deeppink')+'/'+cFL(labs['day'],'deepskyblue')+'/'+cFL(labs['year'],'blueviolet')+']','pink')
			if (len(labs['month']) > 0) and (len(labs['day']) > 0) and (len(labs['year']) > 0): labs['title']+=mdy
			else: labs[u'title']+=cFL('  ['+cFL(ep_date.replace('/',cFL('/','pink')),'blue')+']','pink')
			labs[u'plot']=cFL(ep_name,'red')+cFL('[CR]Date Added:  ['+cFL(ep_date.replace('/',cFL('/','pink')),'blue')+']','pink')+'[CR]'+labs[u'plot']; 
			try: labs[u'plot']=cFL('season: ','green')+cFL(str(s),'deeppink')+cFL(' episode: ','green')+cFL(str(eN2),'deeppink')+'[CR]'+labs[u'plot']
			except: pass
			labs['Date']=ep_date.replace('/','-')
			labs['premiered']=ep_date.replace('/','-')
			deb('Episode Name',labs[u'title']); deb('episode thumbnail',img)
			#
			#xRP='XBMC.RunPlugin(%s)'
			#contextMenuItems.append(( cFL('Add Online Bookmark',  'lime') , xRP % _addon.build_plugin_url({'url':_domain_url+'/Bookmark/'+BookmarkID+'/add',   'mode':'BookmarkAdd'   ,'site':site,'section':section}) ))
			#contextMenuItems.append(( cFL('Remove Online Bookmark','red') , xRP % _addon.build_plugin_url({'url':_domain_url+'/Bookmark/'+BookmarkID+'/remove','mode':'BookmarkRemove','site':site,'section':section}) ))
			if (len(addst('username','')) > 0) and (len(addst('password','')) > 0) and (tfalse(addst('enable-accountinfo','false'))==True): 
				if len(BookmarkID) > 0:
					contextMenuItems.append(BMa)
					contextMenuItems.append(BMr)
			#BookmarkID
			pars={'mode':'GetLinks','img':img,'url':ep_url,'title':ep_name}
			
			if tfalse(addst("singleline"))==True: labs['title']=labs['title'].replace('[CR]',' ')
			try:
				if visited_check(ep_name)==True: 
					if EnableVisitedLeft==True: labs[u'title']="[COLOR lime]@[/COLOR]  "+labs['title']
					else: labs['title']+="  [COLOR lime]@[/COLOR]"
					labs[u'overlay']=7
					contextMenuItems.append(("Unmark",'XBMC.RunPlugin(%s)' % _addon.build_plugin_url({'mode':'RemoveVisit','title':ep_name})))
					contextMenuItems.append(("Empty Visits",'XBMC.RunPlugin(%s)' % _addon.build_plugin_url({'mode':'EmptyVisit'})))
				else: 
					if EnableVisitedLeft==True: labs[u'title']="[COLOR black]@[/COLOR]  "+labs['title']
					labs[u'overlay']=6
					contextMenuItems.append(("Mark",'XBMC.RunPlugin(%s)' % _addon.build_plugin_url({'mode':'AddVisit','title':ep_name})))
			except: pass
			
			if (tfalse(addst("enable-autoplay"))==True):
				try: _addon.add_directory(pars,labs,img=labs[u'cover_url'],fanart=labs[u'backdrop_url'],is_folder=False,contextmenu_items=contextMenuItems,total_items=ItemCount)
				except: pass
			else:
				try: _addon.add_directory(pars,labs,img=labs[u'cover_url'],fanart=labs[u'backdrop_url'],is_folder=True,contextmenu_items=contextMenuItems,total_items=ItemCount)
				except:
					try: _addon.add_directory(pars,labs,img=img,fanart=img,is_folder=True,contextmenu_items=contextMenuItems,total_items=ItemCount)
					except: pass
	#
	##EnableMeta=tfalse(addst("enableMeta"))
	##EnableSiteArt=tfalse(addst("enable-site-art"))
	EnableVisitedLeft=tfalse(addst("enable-visited-left"))
	##if EnableMeta==False: EnableSiteArt=True
	if len(relatedshows) > 0:
		for (item_url,item_name) in relatedshows:
			contextMenuItems=[]; labs={}; item_url=_domain_url+item_url; img=_artIcon; 
			pars={'mode':'GetEpisodes','img':img,'url':item_url,'title':item_name}; labs['title']=cFL('Related: ','pink')+item_name+''; 
			animename=''+item_name; animename.replace(' (Dub)','').replace(' (Sub)','').replace(' (TV)','').replace(' OVA','').replace(' Movies','').replace(' Movie','').replace(' Specials','').replace(' New','') #.replace(' 2nd Season','')
			FoundItK=visited_check2(animename)
			if EnableVisitedLeft==True:
				if FoundItK==True: 
					#labs[u'title']+="  [COLOR deeppink]@[/COLOR]"
					labs[u'title']="[COLOR deeppink]@[/COLOR]  "+labs[u'title']
					#labs[u'plot']="  [COLOR lime]@[/COLOR]  "+labs[u'plot']
				else: labs[u'title']="[COLOR black]@[/COLOR]  "+labs[u'title']
			else:
				if FoundItK==True: labs[u'title']+="  [COLOR deeppink]@[/COLOR]"
			try: _addon.add_directory(pars,labs,img=img,fanart=img,is_folder=True,contextmenu_items=contextMenuItems,total_items=ItemCount)
			except: pass
	# Genres
	if tfalse(addst("show-ep-genres","false"))==True:
		s='<span class="info">Genres:</span>'; 
		if s in html:
			htmlG=html.split(s)[1].split('</p>')[0]; s='<a href="(/Genre/.+?)" class="dotUnder" title="(.+?)">(.+?)</a>'; 
			try: r1=re.compile(s).findall(html)
			except: r1=""
			if len(r1) > 0:
				for g,t1,t2 in r1:
					try: t1=t1.replace('&quot;','"'); imgG=psgn(t2.lower(),'.jpg'); _addon.add_directory({'mode':'SelectSort','url':_domain_url+g},{'title':cFL('Genre: ','green')+cFL(str(t2),'deeppink'),'plot':messupText(t1,True,True,True)},img=imgG,fanart=showFanart,is_folder=True)
					except: pass
	# Views
	if tfalse(addst("show-ep-views","false"))==True:
		s='<span class="info">Views:</span>'
		if s in html: s+='\s*(\d+)\s*'; Views=re.compile(s).findall(html.replace("&nbsp;"," "))[0]
		else: Views="Unknown"
		deb("Views",Views); _addon.add_directory({'mode':'System.ExecWait','url':url},{'title':cFL('Views: ','green')+cFL(str(Views),'yellow')+"[CR]"+cFL(showtitle,'deepskyblue')},img=showImg,fanart=showFanart,is_folder=True)
	# Plot
	if tfalse(addst("show-ep-showplot","false"))==True:
		s='<span class="info">Summary:</span>'; contextMenuItems=[]; contextMenuItems.append((ps('cMI.showinfo.name'),ps('cMI.showinfo.url'))); 
		if s in html: 
			try: 
				s+='\s*\n*\s*<p.*?>(.+?)\s*<'; #s+='\s*\n*\s*<p>(.+?)\s*</p>'; 
				P=re.compile(s).findall(html.replace("&nbsp;"," "))[0]; P=P.replace('<br/>','').replace('<br />','').replace('<BR/>','').replace('<BR />','').replace('<br>','').replace('<BR>',''); P="[CR][COLOR green]Show Plot:  [CR][/COLOR][COLOR tan]"+P+"[/COLOR]"; 
				deb("Show Plot",P); _addon.add_directory({'mode':'System.ExecWait','url':url},{'title':cFL('[ Show Plot ]','green'),'plot':P},img=showImg,fanart=showFanart,is_folder=True,contextmenu_items=contextMenuItems)
			except: p=''; pass
	#
	set_view(ps('content_episodes'),addst('episode-view')); eod() #set_view('episodes',ps('setview.episodes')); eod()

def TestProxies():
	try: from highway.proxies import Proxies
	except:
		myNote("Test Proxies","[COLOR red]module not found.[/COLOR]")
		eod()
		return
	#results=Proxies().getProxyList(path="country-us")
	#myNote("Testing Proxies",":"+str(len(results))+":")
	
	#proxyaddress=Proxies().catchNewProxy(path="country-us")
	#myNote("Testing Proxies","[COLOR red]:[/COLOR]"+str(proxyaddress)+"[COLOR red]:[/COLOR]")
	
	
	eod()
	#RefreshList()
	return

def GrabNewProxy():
	try: from highway.proxies import Proxies
	except:
		myNote("New Proxy","[COLOR red]module not found.[/COLOR]")
		eod()
		return
	proxyaddress=Proxies().catchNewProxy(path="country-us")
	addstv("proxy",proxyaddress)
	myNote("New Proxy","[COLOR red]:[/COLOR]"+str(proxyaddress)+"[COLOR red]:[/COLOR]")
	eod()
	#RefreshList()
	return

def Menu_Last():
	WhereAmI('@ the Last Menu')
	###
	#xbmc.executebuiltin('Skin.SetString(UseCustomBackground,true)'); 
	#xbmc.executebuiltin('Skin.SetBool(UseCustomBackground)'); 
	
	if (_debugging==False) and (_shoDebugging==True):
		_addon.show_ok_dialog(["XBMC "+XBMCversion['Ver'],"Build: "+XBMCversion['Release'],"Date: "+XBMCversion['Date']], title="OS: "+sOS, is_error=False); 
	#deb('Version All',XBMCversion['All']); deb('Version Number',XBMCversion['Ver']); deb('Version Release Name',XBMCversion['Release']); deb('Version Date',XBMCversion['Date']); 
	
	try: deb("System Platform",str(sys.platform)); 
	except: pass
	#time.sleep(2); 
	#xbmc.executebuiltin('ReloadSkin()'); 
	
	###
	if tfalse(addst("singleline"))==True: CR2=' '
	else: CR2='[CR]'
	if (len(addst("LastShowListedURL")) > 0): _addon.add_directory({'mode':'GetEpisodes','url':addst("LastShowListedURL"),'imdbid':addst("LastShowListedImdbID"),'img':addst("LastShowListedIMG")},{'title':cFL_('Last '+ps('common_word')+' Visited:'+CR2+cFL(addst("LastShowListedNAME"),'blue'),ps('cFL_color'))},fanart=addst("LastShowListedIMG"),img=addst("LastShowListedIMG"))
	##if (len(addst("LastVideoPlayItemUrl")) > 0): _addon.add_directory({'mode':'PlayVideo','url':addst("LastVideoPlayItemUrl"),'title':addst('LastVideoPlayItemName'),'studio':addst('LastVideoPlayItemStudio')},{'title':cFL_('Last Video [Played]: '+cFL(addst('LastVideoPlayItemName'),ps('cFL_color3'))+CR2+cFL(addst('LastVideoPlayItemStudio'),'blue'),ps('cFL_color'))},fanart=addst("LastVideoPlayItemImg"),img=addst("LastVideoPlayItemImg"))
	##if (len(addst("LastAutoPlayItemUrl")) > 0): _addon.add_directory({'mode':'PlayVideoA','url':addst("LastAutoPlayItemUrl"),'title':addst('LastAutoPlayItemName')},{'title':cFL_('Last Video [AutoPlay]:'+CR2+cFL(addst('LastAutoPlayItemName'),'blue'),ps('cFL_color'))},fanart=addst("LastAutoPlayItemImg"),img=addst("LastAutoPlayItemImg"))
	if (len(addst("LastVideoPlayItemUrl")) > 0): _addon.add_directory({'mode':'PlayVideoB','url':addst("LastVideoPlayItemUrl"),'title':addst('LastVideoPlayItemName'),'studio':addst('LastVideoPlayItemStudio'),'img':addst("LastVideoPlayItemImg")},{'title':cFL_('Last Video [Played]: '+cFL(addst('LastVideoPlayItemName'),ps('cFL_color3'))+CR2+cFL(addst('LastVideoPlayItemStudio'),'blue'),ps('cFL_color'))},fanart=addst("LastVideoPlayItemImg"),img=addst("LastVideoPlayItemImg"),is_folder=False)
	if (len(addst("LastAutoPlayItemUrl")) > 0):  _addon.add_directory({'mode':'PlayVideoA','url':addst("LastAutoPlayItemUrl") ,'title':addst('LastAutoPlayItemName') ,'img':addst("LastAutoPlayItemImg")},{'title':cFL_('Last Video [AutoPlay]:'+CR2+cFL(addst('LastAutoPlayItemName'),'blue'),ps('cFL_color'))},fanart=addst("LastAutoPlayItemImg"),img=addst("LastAutoPlayItemImg"),is_folder=False)
	set_view('list',addst('default-view')); eod()

def Menu_2():
	WhereAmI('@ the Menu 2')
	if tfalse(addst("singleline"))==True: CR2=' '
	else: CR2='[CR]'
	_addon.add_directory({'mode':'System.Exec','url':'http://kissanime.com/'},{'title': cFL_('KissAnime.com',ps('cFL_color3'))},is_folder=True,fanart=_artFanart,img='http://kissanime.com/Content/images/logo.png'); 
	#_addon.add_directory({'mode':'System.Exec','url':'http://kissanime.com/M'},{'title': cFL_('KissAnime Mobile',ps('cFL_color3'))},is_folder=True,fanart=_artFanart,img='http://kissanime.com/Content/images/logo.png'); 
	#_addon.add_directory({'mode':'System.Exec','url':'http://kissanime.com/Message/ReportError'},{'title': cFL_('Report Errors',ps('cFL_color3'))},is_folder=True,fanart=_artFanart,img='http://kissanime.com/Content/images/logo.png'); 
	#_addon.add_directory({'mode':'System.Exec','url':''},{'title': cFL_('KissAnime',ps('cFL_color3'))},is_folder=True,fanart=_artFanart,img='http://kissanime.com/Content/images/logo.png'); 
	_addon.add_directory({'mode':'System.Exec','url':'http://kissanime.com/AdvanceSearch'},{'title': cFL_('Advanced Search',ps('cFL_color3'))},is_folder=True,fanart=_artFanart,img='http://kissanime.com/Content/images/logo.png'); 
	_addon.add_directory({'mode':'System.Exec','url':'https://www.facebook.com/groups/kisscommunity'},{'title': cFL_('Discussion',ps('cFL_color3'))},is_folder=True,fanart='https://fbcdn-sphotos-b-a.akamaihd.net/hphotos-ak-prn2/t1/954767_686622534684507_1720354290_n.jpg',img='http://i.imgur.com/ImsT2tb.png'); 
	_addon.add_directory({'mode':'System.Exec','url':'https://www.facebook.com/messages/kissanimeweb'},{'title': cFL_('Request Anime',ps('cFL_color3'))},is_folder=True,fanart='https://scontent-b-ord.xx.fbcdn.net/hphotos-frc3/t1/483600_372465079535066_686333025_n.jpg',img='http://i.imgur.com/S568G7Q.jpg'); 
	_addon.add_directory({'mode':'System.Exec','url':'http://kissmanga.com/'},{'title': cFL_('KissManga.com',ps('cFL_color3'))},is_folder=True,fanart='https://scontent-b-ord.xx.fbcdn.net/hphotos-frc3/t1/1538852_511236602306952_774531197_n.jpg',img='http://kissmanga.com/Content/images/logo.png'); 
	_addon.add_directory({'mode':'System.Exec','url':'https://www.facebook.com/kissanimeweb'},{'title': cFL_('FaceBook',ps('cFL_color3'))},is_folder=True,fanart='https://scontent-b-ord.xx.fbcdn.net/hphotos-frc3/t1/483600_372465079535066_686333025_n.jpg',img='http://www.marketingpilgrim.com/wp-content/uploads/2012/01/facebook-icon-1.png'); 
	
	
	set_view('list',addst('default-view')); eod()

def Menu_MainMenu(): #The Main Menu
	WhereAmI('@ the Main Menu')
	if tfalse(addst("singleline"))==True: CR2=' '
	else: CR2='[CR]'
	# ,img=psgn('','.jpg') # ,img=ps('img_kisslogo')
	#
	if _debugging==True:
		try: 
			if (tfalse(addst('customproxy','false'))==True):
				from highway.proxies import Proxies as Test01
				_addon.add_directory({'mode':'TestProxies'},{'title':cFL('Test Proxies',ps('cFL_color'))+' [Dev Tool]'},is_folder=True,fanart=_artFanart,img=ps('img_kisslogo')) #ps('img_kisslogo'))
				#_addon.add_directory({'mode':'GrabNewProxy'},{'title':cFL('Grab New Proxy',ps('cFL_color'))+' [User Tool]'},is_folder=True,fanart=_artFanart,img=ps('img_kisslogo')) #ps('img_kisslogo'))
		except: pass
	try: 
		if (tfalse(addst('customproxy','false'))==True):
			from highway.proxies import Proxies as DoIPrintLink01
			_addon.add_directory({'mode':'GrabNewProxy'},{'title':cFL('Grab New Proxy',ps('cFL_color'))+' [User Tool]'},is_folder=True,fanart=_artFanart,img=ps('img_kisslogo')) #ps('img_kisslogo'))
	except: pass
	#
	_addon.add_directory({'mode':'SelectAZ','url':_domain_url+'/'+ps('common_word')+'List'},{'title':cFL_(ps('common_word')+' List ( All | # | A-Z )',ps('cFL_color'))},fanart=_artFanart,img=psgn(ps('common_word').lower()+' list all','.jpg'))
	_addon.add_directory({'mode':'GetTitles','url':_domain_url+'/Status/Ongoing'},{'title':cFL_('Ongoing',ps('cFL_color'))},fanart=_artFanart,img=psgn('ongoing','.jpg'))
	_addon.add_directory({'mode':'GetTitles','url':_domain_url+'/Status/Completed'},{'title':cFL_('Completed',ps('cFL_color'))},fanart=_artFanart,img=psgn('completed','.jpg'))
	_addon.add_directory({'mode':'BrowseGenre','url':_domain_url+'/'},{'title':cFL_('Genre',ps('cFL_color'))},fanart=_artFanart,img=psgn('genre','.jpg'))
	_addon.add_directory({'mode':'GetTitles','url':_domain_url+'/'+ps('common_word')+'List/Newest'},{'title':cFL_(ps('common_word')+' List [Newest]',ps('cFL_color'))},fanart=_artFanart,img=psgn(ps('common_word').lower()+' list newest','.jpg'))
	_addon.add_directory({'mode':'GetTitles','url':_domain_url+'/'+ps('common_word')+'List/LatestUpdate'},{'title':cFL_(ps('common_word')+' List [Latest Update]',ps('cFL_color'))},fanart=_artFanart,img=psgn(ps('common_word').lower()+' list latest update','.jpg'))
	_addon.add_directory({'mode':'GetTitles','url':_domain_url+'/'+ps('common_word')+'List/MostPopular'},{'title':cFL_(ps('common_word')+' List [Popularity]',ps('cFL_color'))},fanart=_artFanart,img=psgn(ps('common_word').lower()+' list popularity','.jpg'))
	#
	if (tfalse(addst("oldmenu"))==True):
		_addon.add_directory({'mode':'SelectGenre','url':_domain_url+'/'},{'title':cFL_('Genre (Select)',ps('cFL_color'))},fanart=_artFanart,img=psgn('genre select','.jpg')) #art('genre','.jpg'))
		_addon.add_directory({'mode':'BrowseLast'},{'title':cFL_('Last',ps('cFL_color2'))},fanart=_artFanart,img=psgn('last','.jpg')) #ps('img_kisslogo'))
	_addon.add_directory({'mode':'GetTitles','url':_domain_url+'/'+ps('common_word')+'List'},{'title':cFL_(ps('common_word')+' List [Alphabet]',ps('cFL_color'))},fanart=_artFanart,img=psgn(ps('common_word').lower()+' list alphabet','.jpg')) #img=ps('img_kisslogo'))
	##_addon.add_directory({'mode':'BrowseGenre2'},{'title':cFL_('Genres',ps('cFL_color'))},fanart=_artFanart,img=art('genre','.jpg'))
	_addon.add_directory({'mode':'Search','pageno': '1', 'pagecount': addst('pages')},{'title':cFL_('Search',ps('cFL_color'))},fanart=_artFanart,img=psgn('search','.jpg')) #ps('img_search'))
	#
	for genre in ['OVA','Movie']:
		img=psgn(genre.lower(),'.jpg'); _addon.add_directory({'mode': 'SelectSort','url': _domain_url+'/Genre/'+genre.replace(' ','-')},{'title':genre},img=img,fanart=_artFanart)
	#
	if (len(addst("LastShowListedURL")) > 0) and (tfalse(addst("enable-autoplay-lsv"))==True): _addon.add_directory({'mode':'GetEpisodes','url':addst("LastShowListedURL"),'imdbid':addst("LastShowListedImdbID"),'img':addst("LastShowListedIMG")},{'title':cFL_('Last '+ps('common_word')+' Visited:'+CR2+cFL(addst("LastShowListedNAME"),'blue'),ps('cFL_color'))},fanart=addst("LastShowListedIMG"),img=addst("LastShowListedIMG"))
	#if (len(addst("LastShowListedURL")) > 0) and (tfalse(addst("enable-autoplay-lsv"))==True): _addon.add_directory({'mode':'GetEpisodes','url':addst("LastShowListedURL")},{'title':cFL_('Last '+ps('common_word')+' Visited:'+CR2+cFL(addst("LastShowListedNAME"),'blue'),ps('cFL_color'))},fanart=addst("LastShowListedIMG"),img=addst("LastShowListedIMG"))
	if (len(addst("LastVideoPlayItemUrl")) > 0) and (tfalse(addst("enable-autoplay-lvp"))==True): _addon.add_directory({'mode':'PlayVideoB','url':addst("LastVideoPlayItemUrl"),'title':addst('LastVideoPlayItemName'),'studio':addst('LastVideoPlayItemStudio'),'img':addst("LastVideoPlayItemImg")},{'title':cFL_('Last Video [Played]: '+cFL(addst('LastVideoPlayItemName'),ps('cFL_color3'))+CR2+cFL(addst('LastVideoPlayItemStudio'),'blue'),ps('cFL_color'))},fanart=addst("LastVideoPlayItemImg"),img=addst("LastVideoPlayItemImg"),is_folder=False)
	#if (len(addst("LastAutoPlayItemUrl")) > 0) and (tfalse(addst("enable-autoplay-lvap"))==True): _addon.add_directory({'mode':'PlayVideo','url':addst("LastAutoPlayItemUrl"),'title':addst('LastAutoPlayItemName')},{'title':cFL_('Last Video [AutoPlay]:'+CR2+cFL(addst('LastAutoPlayItemName'),'blue'),ps('cFL_color'))},fanart=addst("LastShowListedIMG"),img=addst("LastShowListedIMG"))
	if (len(addst("LastAutoPlayItemUrl")) > 0) and (tfalse(addst("enable-autoplay-lvap"))==True): _addon.add_directory({'mode':'PlayVideoA','url':addst("LastAutoPlayItemUrl"),'title':addst('LastAutoPlayItemName'),'img':addst("LastAutoPlayItemImg")},{'title':cFL_('Last Video [AutoPlay]:'+CR2+cFL(addst('LastAutoPlayItemName'),'blue'),ps('cFL_color'))},fanart=addst("LastAutoPlayItemImg"),img=addst("LastAutoPlayItemImg"),is_folder=False)
	#
	#if _debugging==True:
	if (len(addst('username','')) > 0) and (len(addst('password','')) > 0) and (tfalse(addst('enable-accountinfo','false'))==True): 
		_addon.add_directory({'mode':'listBookmarks','url':_domain_url+'/BookmarkList'},{'title':cFL('Online Bookmarks',ps('cFL_color'))+' [Account]'},fanart=_artFanart,img=psgn('online bookmarks','.jpg')) #ps('img_kisslogo'))
	
	#
	_addon.add_directory({'mode': 'FavoritesList'},{'title':  cFL_('Favorites '+addst('fav.movies.1.name'),ps('cFL_color3'))},fanart=_artFanart,img=psgn('favorites','.jpg')) #_art404)
	if (tfalse(addst("enable-fav-movies-2"))==True): _addon.add_directory({'mode': 'FavoritesList','subfav': '2'},{'title':  cFL_('Favorites '+addst('fav.movies.2.name'),ps('cFL_color3'))},fanart=_artFanart,img=psgn('favorites 2','.jpg')) #_art404)
	if (tfalse(addst("enable-fav-movies-3"))==True): _addon.add_directory({'mode': 'FavoritesList','subfav': '3'},{'title':  cFL_('Favorites '+addst('fav.movies.3.name'),ps('cFL_color3'))},fanart=_artFanart,img=psgn('favorites 3','.jpg')) #_art404)
	if (tfalse(addst("enable-fav-movies-4"))==True): _addon.add_directory({'mode': 'FavoritesList','subfav': '4'},{'title':  cFL_('Favorites '+addst('fav.movies.4.name'),ps('cFL_color3'))},fanart=_artFanart,img=psgn('favorites 4','.jpg')) #_art404)
	#
	
	_addon.add_directory({'mode': 'GetTitlesUpcoming','url':_domain_url+'/Upcoming'+ps('common_word')+''},{'title': cFL_('Upcoming '+ps('common_word'),ps('cFL_color3'))},is_folder=True,fanart=_artFanart,img=psgn('upcoming anime','.jpg'))
	
	#_addon.add_directory({'mode': 'ResolverSettings'}, {'title':  cFL('U',ps('cFL_color2'))+'rl-Resolver Settings'},is_folder=False		,img=art('turtle','.jpg')	,fanart=_artFanart)
	_addon.add_directory({'mode': 'Settings'}, 				 {'title':  cFL('P',ps('cFL_color2'))+'lugin Settings'}			,is_folder=False,fanart=_artFanart,img=psgn('plugin settings','.jpg')) #,img=art('kiss')
	##_addon.add_directory({'mode': 'DownloadStop'}, 		 {'title':  cFL('S',ps('cFL_color'))+'top Current Download'},is_folder=False		,img=_artDead							,fanart=_artFanart)
	_addon.add_directory({'mode': 'TextBoxFile',  'title': "[COLOR cornflowerblue]Local Change Log:[/COLOR]  %s"  % (__plugin__), 'url': ps('changelog.local')}, 	{'title': cFL_('Local Change Log',ps('cFL_color3'))}, is_folder=False ,fanart=_artFanart,img=psgn('local change log','.jpg')) #,img=art('thechangelog','.jpg')
	
	_addon.add_directory({'mode': 'BrowseMenu2'},{'title': cFL_('KissAnime '+CR2+'Site Shortcuts',ps('cFL_color3'))},is_folder=True,fanart=_artFanart,img=psgn('site shortcuts','.jpg')) #_artIcon) #'http://kissanime.com/Content/images/logo.png') #,img=art('thechangelog','.jpg')
	
	if (tfalse(addst("label-empty-favorites"))==True):
		_addon.add_directory({'section': '', 'mode': 'FavoritesEmpty', 'subfav':  ''},	 		{'title':  cFL('E',ps('cFL_color'))+'mpty Favorites '+addst('fav.movies.1.name')},fanart=_artFanart,img=art('trash','.gif'),is_folder=False)
		if (tfalse(addst("enable-fav-movies-2"))==True): _addon.add_directory({'section': '', 'mode': 'FavoritesEmpty', 'subfav': '2'},	 		{'title':  cFL('E',ps('cFL_color'))+'mpty Favorites '+addst('fav.movies.2.name')},fanart=_artFanart,img=art('trash','.gif'),is_folder=False)
		if (tfalse(addst("enable-fav-movies-3"))==True): _addon.add_directory({'section': '', 'mode': 'FavoritesEmpty', 'subfav': '3'},	 		{'title':  cFL('E',ps('cFL_color'))+'mpty Favorites '+addst('fav.movies.3.name')},fanart=_artFanart,img=art('trash','.gif'),is_folder=False)
		if (tfalse(addst("enable-fav-movies-4"))==True): _addon.add_directory({'section': '', 'mode': 'FavoritesEmpty', 'subfav': '4'},	 		{'title':  cFL('E',ps('cFL_color'))+'mpty Favorites '+addst('fav.movies.4.name')},fanart=_artFanart,img=art('trash','.gif'),is_folder=False)
	##_addon.add_directory({'mode': 'TextBoxUrl',   'title': "[COLOR cornflowerblue]Latest Change Log:[/COLOR]  %s" % (__plugin__), 'url': ps('changelog.url')}, 		{'title': cFL('L',ps('cFL_color'))+'atest Online Change Log'},	img=art('thechangelog','.jpg'), is_folder=False ,fanart=_artFanart)
	##_addon.add_directory({'mode': 'TextBoxUrl',   'title': "[COLOR cornflowerblue]Latest News:[/COLOR]  %s"       % (__plugin__), 'url': ps('news.url')}, 				{'title': cFL('L',ps('cFL_color'))+'atest Online News'},				img=_art404										, is_folder=False ,fanart=_artFanart)
	##_addon.add_directory({'mode': 'LatestThreads','title': "[COLOR cornflowerblue]Latest Threads[/COLOR]", 'url': ps('LatestThreads.url')}, 											{'title': cFL('L',ps('cFL_color'))+'atest Threads'},						img=_art404										, is_folder=False ,fanart=_artFanart)
	##_addon.add_directory({'mode': 'PrivacyPolicy','title': "", 'url': ''}, 																																												{'title': cFL('P',ps('cFL_color'))+'rivacy Policy'},						img=_art404										, is_folder=False ,fanart=_artFanart)
	##_addon.add_directory({'mode': 'TermsOfService','title': "", 'url': ''}, 																																											{'title': cFL('T',ps('cFL_color'))+'erms of Service'},					img=_art404										, is_folder=False ,fanart=_artFanart)
	### ############ 
	set_view('list',addst('default-view')); eod()
	### ############ 
	### _addon.show_countdown(9000,'Testing','Working...') ### Time seems to be in seconds.
	### ############ Coding for Catching Update-Messages from My Repository.
	##CurDate=time.strftime("%Y-%m-%d"); CurTime24=time.strftime("%H:%M"); CurTime12=time.strftime("%I:%M"); 
	if tfalse(addst("check-github-messages","false"))==True:
		LastDate=addst('git-last',''); deb('CurDate ',CurDate); deb('LastDate',LastDate); #myNote("-","="); ## for testing ##
		if not CurDate==LastDate: GitData=getGitMsg(); checkGitMsg(); 
	
	### ############ 

##### /\ ##### Menus #####
### ############################################################################################################
### ############################################################################################################
### ############################################################################################################
##### Favorites #####
def fav__empty(section,subfav=''): WhereAmI('@ Favorites - Empty - %s%s' % (section,subfav)); favs=[]; cache.set('favs_'+section+subfav+'__', str(favs)); sunNote(bFL('Favorites'),bFL('Your Favorites Have Been Wiped Clean. Bye Bye.'))
def fav__remove(section,name,year,subfav=''):
	WhereAmI('@ Favorites - Remove - %s%s' % (section,subfav)); deb('fav__remove() '+section,name+'  ('+year+')'); saved_favs=cache.get('favs_'+section+subfav+'__'); tf=False
	if saved_favs:
		favs=eval(saved_favs)
		if favs:
			for (_name,_year,_img,_fanart,_country,_url,_plot,_genre,_dbid) in favs: 
				if (name==_name) and (year==_year):
					favs.remove((_name,_year,_img,_fanart,_country,_url,_plot,_genre,_dbid)); cache.set('favs_'+section+subfav+'__', str(favs)); tf=True; sunNote(bFL(name.upper()+'  ('+year+')'),bFL('Removed from Favorites')); deb(name+'  ('+year+')','Removed from Favorites. (Hopefully)'); xbmc.executebuiltin("XBMC.Container.Refresh"); return
			if (tf==False): sunNote(bFL(name.upper()),bFL('not found in your Favorites'))
		else: sunNote(bFL(name.upper()+'  ('+year+')'),bFL('not found in your Favorites'))
def fav__COMMON__check(name,section,subfav):
	#debob("testing4"); 
	saved_favs=cache.get('favs_'+section+subfav+'__'); 
	#debob("testing3"); 
	#debob(str(len(saved_favs))); 
	#debob(saved_favs); 
	if saved_favs:
		#debob("testing2"); 
		#try:
		favs=eval(saved_favs); 
		if favs:
			#debob("testing1"); 
			#for (_name,_year,_img,_fanart,_country,_url,_plot,_Genres,_site,_subfav,_section,_ToDoParams,_commonID,_commonID2) in favs: 
			for (_name,_year,_img,_fanart,_country,_url,_plot,_genre,_dbid) in favs: 
				#if (name==_name) and (year==_year): return True
				if (name==_name): return True
				#if (name in _name): return True
			return False
		else: return False
		#except: return False
	else: return False
def fav__add_OLD(section,name,year='',img=_art150,fanart=_artFanart,subfav=''):
	WhereAmI('@ Favorites - Add - %s%s' % (section,subfav))
	if (debugging==True): print 'fav__add()',section,name+'  ('+year+')',img,fanart
	saved_favs=cache.get('favs_'+section+subfav+'__'); favs=[]; fav_found=False
	if saved_favs:
		if (debugging==True): print saved_favs
		favs=eval(saved_favs)
		if favs:
			if (debugging==True): print favs
			for (_name,_year,_img,_fanart,_country,_url,_plot,_genre,_dbid) in favs:
				if (name==_name) and (year==_year): 
					fav_found=True; sunNote(bFL(section+':  '+name.upper()+'  ('+year+')'),bFL('Already in your Favorites')); return
	if   (section==ps('section.tv')):    favs.append((name,year,img,fanart,_param['country'],_param['url'],_param['plot'],_param['genre'],_param['dbid']))
	elif (section==ps('section.movie')): favs.append((name,year,img,fanart,_param['country'],_param['url'],_param['plot'],_param['genre'],addpr('dbid','')))
	cache.set('favs_'+section+subfav+'__', str(favs)); sunNote(bFL(name+'  ('+year+')'),bFL('Added to Favorites'))

def fav__add(section,name,year='',img=_art150,fanart=_artFanart,subfav=''):
	WhereAmI('@ Favorites - Add - %s%s' % (section,subfav))
	if (debugging==True): print 'fav__add()',section,name+'  ('+year+')',img,fanart
	favs=[]; fav_found=False
	try: 
		saved_favs=cache.get('favs_'+section+subfav+'__'); 
	except: deb("cache.get() - Error getting",'favs_'+section+subfav+'__'); 
	if len(saved_favs)==0: 
		try: debob(saved_favs); 
		except: pass
	try: favs=eval(saved_favs); #debob(favs); 
	except: favs=[]; #debob(favs); 
	if len(favs)==0: debob(favs)
	for (_name,_year,_img,_fanart,_country,_url,_plot,_genre,_dbid) in favs:
		if (name==_name) and (year==_year): 
			fav_found=True; sunNote(bFL(section+':  '+name.upper()+'  ('+year+')'),bFL('Already in your Favorites')); return
	if   (section==ps('section.tv')):    favs.append((name,year,img,fanart,_param['country'],_param['url'],_param['plot'],_param['genre'],_param['dbid']))
	elif (section==ps('section.movie')): favs.append((name,year,img,fanart,_param['country'],_param['url'],_param['plot'],_param['genre'],addpr('dbid','')))
	else: 
		deb("'sectoin' Error","section seems to be an unknown type."); 
		deb("'sectoin' Error","defaulting to 'tv' type as section."); 
		favs.append((name,year,img,fanart,_param['country'],_param['url'],_param['plot'],_param['genre'],_param['dbid']))
	cache.set('favs_'+section+subfav+'__', str(favs)); sunNote(bFL(name+'  ('+year+')'),bFL('Added to Favorites'))
def fav__list(section,subfav=''):
	WhereAmI('@ Favorites - List - %s%s' % (section,subfav)); saved_favs=cache.get('favs_'+section+subfav+'__'); favs=[]
	if saved_favs:
		if (debugging==True): print saved_favs
		favs=sorted(eval(saved_favs), key=lambda fav: (fav[1],fav[0]),reverse=True)
		ItemCount=len(favs) # , total_items=ItemCount
		if favs:
			#if   (section==ps('section.tv')): 		xbmcplugin.setContent( int( sys.argv[1] ), 'tvshows' )
			#elif (section==ps('section.movie')): 	xbmcplugin.setContent( int( sys.argv[1] ), 'movies' )
			for (name,year,img,fanart,country,url,plot,genre,dbid) in favs:
				if (debugging==True): print '----------------------------'
				if (debugging==True): print name,year,img,fanart,country,url,plot,genre,dbid #,pars,labs
				contextMenuItems=[]; labs2={}; labs2['fanart']=''
				labs2['title']=cFL(name,ps('cFL_color3'))
				#labs2['title']=cFL(name+'  ('+cFL(year,ps('cFL_color2'))+')',ps('cFL_color')); 
				labs2['image']=img; labs2['fanart']=fanart; labs2['ShowTitle']=name; labs2['year']=year; labs2['plot']=plot
				#pars2={'mode': 'GetLinks', 'section': section, 'url': url, 'img': img, 'image': img, 'fanart': fanart, 'title': name, 'year': year }; 
				pars2={'mode': 'GetEpisodes', 'section': section, 'url': url, 'img': img, 'image': img, 'fanart': fanart, 'title': name, 'year': year, 'showtitle': name, 'dbid': str(dbid), 'imdbid': str(dbid) }; 
				##labs2['title']=cFL(name+'  ('+cFL(year,ps('cFL_color2'))+')  ['+cFL(country,ps('cFL_color3'))+']',ps('cFL_color'))
				##labs2[u'overlay']=xbmcgui.ICON_OVERLAY_WATCHED
				##labs2['overlay']=xbmcgui.ICON_OVERLAY_WATCHED
				#labs2['overlay']=7
				#
				##### Right Click Menu for: TV #####
				contextMenuItems.append((ps('cMI.showinfo.name'),ps('cMI.showinfo.url')))
				if (len(addst('download_folder_wallpapers')) > 0) and (fanart is not ''): 
					try: 
						contextMenuItems.append(('Download Wallpaper', 'XBMC.RunPlugin(%s)' % _addon.build_plugin_url( { 'mode': 'Download' , 'section': ps('section.wallpaper') , 'studio': name , 'img': img , 'url': fanart } ) ))
					except: pass
				#if (len(addst('download_folder_wallpapers')) > 0) and (fanart is not ''): contextMenuItems.append(('Download Wallpaper', 'XBMC.RunPlugin(%s)' % _addon.build_plugin_url( { 'mode': 'Download' , 'section': ps('section.wallpaper') , 'studio': name+' ('+year+')' , 'img': img , 'url': fanart } ) ))
				##
				if (subfav is not ''): contextMenuItems.append((ps('cMI.favorites.tv.add.name')+' '+addst('fav.movies.1.name'),ps('cMI.favorites.tv.add.url') % (sys.argv[0],ps('cMI.favorites.tv.add.mode'),section,urllib.quote_plus(name),'',urllib.quote_plus(img),urllib.quote_plus(fanart),urllib.quote_plus(country),urllib.quote_plus(plot),urllib.quote_plus(genre),urllib.quote_plus(url),urllib.quote_plus(str(dbid)), '' )))
				if (tfalse(addst("enable-fav-movies-2"))==True) and (subfav is not '2'): contextMenuItems.append((ps('cMI.favorites.tv.add.name')+' '+addst('fav.movies.2.name'),ps('cMI.favorites.tv.add.url') % (sys.argv[0],ps('cMI.favorites.tv.add.mode'),section,urllib.quote_plus(name),'',urllib.quote_plus(img),urllib.quote_plus(fanart),urllib.quote_plus(country),urllib.quote_plus(plot),urllib.quote_plus(genre),urllib.quote_plus(url),urllib.quote_plus(str(dbid)),'2' )))
				if (tfalse(addst("enable-fav-movies-3"))==True) and (subfav is not '3'): contextMenuItems.append((ps('cMI.favorites.tv.add.name')+' '+addst('fav.movies.3.name'),ps('cMI.favorites.tv.add.url') % (sys.argv[0],ps('cMI.favorites.tv.add.mode'),section,urllib.quote_plus(name),'',urllib.quote_plus(img),urllib.quote_plus(fanart),urllib.quote_plus(country),urllib.quote_plus(plot),urllib.quote_plus(genre),urllib.quote_plus(url),urllib.quote_plus(str(dbid)),'3' )))
				if (tfalse(addst("enable-fav-movies-4"))==True) and (subfav is not '4'): contextMenuItems.append((ps('cMI.favorites.tv.add.name')+' '+addst('fav.movies.4.name'),ps('cMI.favorites.tv.add.url') % (sys.argv[0],ps('cMI.favorites.tv.add.mode'),section,urllib.quote_plus(name),'',urllib.quote_plus(img),urllib.quote_plus(fanart),urllib.quote_plus(country),urllib.quote_plus(plot),urllib.quote_plus(genre),urllib.quote_plus(url),urllib.quote_plus(str(dbid)),'4' )))
				##
				#contextMenuItems.append((ps('cMI.favorites.tv.remove.name'), 	   ps('cMI.favorites.movie.remove.url') % (sys.argv[0],ps('cMI.favorites.tv.remove.mode'),section,urllib.quote_plus(name),year,urllib.quote_plus(img),urllib.quote_plus(fanart),urllib.quote_plus(country),urllib.quote_plus(plot),urllib.quote_plus(genre),urllib.quote_plus(url), '' )))
				contextMenuItems.append((ps('cMI.favorites.tv.remove.name'),ps('cMI.favorites.tv.remove.url') % (sys.argv[0],ps('cMI.favorites.tv.remove.mode'),section,urllib.quote_plus(name),year,urllib.quote_plus(img),urllib.quote_plus(fanart),urllib.quote_plus(country),urllib.quote_plus(plot),urllib.quote_plus(genre),urllib.quote_plus(url),urllib.quote_plus(str(dbid)),subfav )))
				contextMenuItems.append(('Empty Favorites','XBMC.RunPlugin(%s?mode=%s&section=%s&subfav=%s' % (sys.argv[0],'FavoritesEmpty',section,subfav ) ))
				##### Right Click Menu for: TV ##### /\ #####
				if tfalse(addst("singleline"))==True: labs2['title']=labs2['title'].replace('[CR]',' ')
				try: _addon.add_directory(pars2, labs2, img=img, fanart=fanart, contextmenu_items=contextMenuItems, context_replace=True)
				except: deb('Error Listing Item',name+'  ('+year+')')
			set_view('episodes',addst('episode-view'))
			#set_view('movies' ,ps('setview.movies')	,True)
		else: sunNote('Favorites:  '+section,'No favorites found *'); set_view('list',addst('default-view')); eod(); return
	else: sunNote('Favorites:  '+section,'No favorites found **'); set_view('list',addst('default-view')); eod(); return
	#set_view('list',addst('default-view')); 
	eod()

def ChangeFanartUpdate(section,subfav,fanart,dbid):
	WhereAmI('@ Favorites - Update Fanart - %s%s' % (section,subfav))
	saved_favs=cache.get('favs_'+section+subfav+'__'); favs=[]; favs_new=[]; fav_found=False; name=''; year=''
	if saved_favs:
		if (debugging==True): print saved_favs
		favs=eval(saved_favs)
		if favs:
			for (_name,_year,_img,_fanart,_country,_url,_plot,_genre,_dbid) in favs:
				if (dbid==_dbid):	favs_new.append((_name,_year,_img, fanart,_country,_url,_plot,_genre,_dbid)); name=_name; year=_year
				else:							favs_new.append((_name,_year,_img,_fanart,_country,_url,_plot,_genre,_dbid))
			cache.set('favs_'+section+subfav+'__', str(favs_new)); sunNote(bFL(name+'  ('+year+')'),bFL('Updated Fanart'))
	eod(); #xbmc.executebuiltin('XBMC.Container.Update(%s)' % _addon.build_plugin_url({'mode': 'FavoritesList' , 'section': section , 'subfav': subfav}))

def ChangeFanartList(section,subfav,dbid,current,img,title):
	WhereAmI('@ Favorites - List - %s%s - %s' % (section,subfav,dbid)); 
	if   (section==ps('section.tv')):
		url=ps('meta.tv.fanart.all.url') % dbid
		html=mGetItemPage(url)
		deb('length of HTML',str(len(html)))
		try:		iitems=re.compile(ps('meta.tv.fanart.all.match')).findall(html)
		except:	iitems=None
		if (iitems==None) or (iitems==''): deb('Error','No Items Found.'); return
		ItemCount=len(iitems) # , total_items=ItemCount
		deb('Items Found',str(ItemCount))
		parsC={'section':section,'subfav':subfav,'mode':'ChangeFanartUpdate','url':current, 'title': dbid}
		#_addon.add_directory(parsC,{ 'title': title, 'studio': title },img=img,fanart=current)
		_addon.add_directory(parsC,{ 'title': title, 'studio': title },img=current,fanart=current)
		#_addon.add_item(parsC,{ 'title': title, 'studio': title },img=img,fanart=current)
		#_addon.add_directory({'mode':'test'}, {'title':title}, img=img)
		#_addon.add_directory({'mode':'test'}, {'title':'title'})
		#_addon.end_of_directory(); return
		iitems=sorted(iitems, key=lambda item: item[0], reverse=False)
		#print iitems
		for fanart_url,fanart_name in iitems:
			fanart_url=ps('meta.tv.fanart.all.prefix')+fanart_url
			pars={ 'section': section, 'subfav': subfav, 'mode': 'ChangeFanartUpdate', 'url': fanart_url, 'title': dbid }
			deb('fanart url ',fanart_url); deb('fanart name',fanart_name); #print pars
			#_addon.add_directory(pars, {'title':'Fanart No. '+fanart_name}, img=img, fanart=fanart_url, total_items=ItemCount)
			_addon.add_directory(pars, {'title':'Fanart No. '+fanart_name}, img=fanart_url, fanart=fanart_url, total_items=ItemCount)
			#_addon.add_directory(pars, {'title':'Fanart No. '+fanart_name}, img=img, fanart=fanart_url)
			#_addon.add_directory(pars, {'title':'Fanart No. '+str(fanart_name)})
		#eod()
		#sunNote('Testing - '+section,'lala a la la la!')
		set_view('list',addst('default-view')); 
		eod()
		#xbmc.executebuiltin("XBMC.Container.Refresh")
	elif (section==ps('section.movie')):
		url=''
		return
	else: return
	set_view('list',addst('default-view')); eod()


##### /\ ##### Favorites #####
### ############################################################################################################
### ############################################################################################################
### ############################################################################################################
##### Search #####
def doSearchNormal (section,title=''):
	SearchPrefix=_domain_url+'/Search/'+ps('common_word')+'?keyword=%s'
	if (title==''):
		title=showkeyboard(txtMessage=title,txtHeader="Title:  ("+section+")")
		if (title=='') or (title=='none') or (title==None) or (title==False): return
	title=title.replace(' ','+')
	#title=title.replace(' ','%20')
	_param['url']=SearchPrefix % title; deb('Searching for',_param['url']); 
	listItems(section, _param['url'], _param['pageno'], addst('pages'), _param['genre'], _param['year'], _param['title'])

def doSearchAdvanced (section,title=''):
	txtHeader='Advanced Search'; options={}; r= -1
	#########################
	options[ps('AdvSearch.tags.1')]				=''
	options[ps('AdvSearch.tags.2')]				=''
	options[ps('AdvSearch.tags.3')]				=''
	options[ps('AdvSearch.tags.4')]				='0'
	options[ps('AdvSearch.tags.5')]				=str(ps('BrowseByYear.earliestyear'))
	options[ps('AdvSearch.tags.6')]				=str(int(datetime.date.today().strftime("%Y"))+1)
	options[ps('AdvSearch.tags.7')]				=''						### &q[genre][]=2&q[genre][]=13
	#########################
	options['startPage']		='1'
	options['numOfPages']		=addst('pages') #'1'
	#########################
	if   (section==ps('section.tv')   ): options[ps('AdvSearch.tags.0')]='1'; options['url']=ps('AdvSearch.url.tv')
	elif (section==ps('section.movie')): options[ps('AdvSearch.tags.0')]='0'; options['url']=ps('AdvSearch.url.movie')
	else: 															 options[ps('AdvSearch.tags.0')]='0'; options['url']=ps('AdvSearch.url.movie')
	options['url']+='['+ps('AdvSearch.tags.0')+']='+options[ps('AdvSearch.tags.0')]; _param['url']=options['url']
	#options['']=''
	#options['']=''
	### [year_from]=2013&q[year_to]=2014&q[country]=132&q[genre][]=2&q[genre][]=13
	### http://www.solarmovie.so/advanced-search/?q[title]=maveric&q[is_series]=0&q[actor]=&q[description]=&q[year_from]=2013&q[year_to]=2014&q[country]=0
	### http://www.solarmovie.so/advanced-search/?q[title]=maveric&q[is_series]=0&q[actor]=testb&q[description]=testa&q[year_from]=2013&q[year_to]=2014&q[country]=132&q[genre][]=2&q[genre][]=13
	while (r is not 0):
		option_list=[]
		option_list.append(																						 ps('AdvSearch.menu.0'))
		if (''==options[ps('AdvSearch.tags.1')]): 	option_list.append(ps('AdvSearch.menu.1'))
		else:																				option_list.append(ps('AdvSearch.menu.1')+':  '+options[ps('AdvSearch.tags.1')])
		if (''==options[ps('AdvSearch.tags.2')]): 	option_list.append(ps('AdvSearch.menu.2'))
		else:																				option_list.append(ps('AdvSearch.menu.2')+':  '+options[ps('AdvSearch.tags.2')])
		if (''==options[ps('AdvSearch.tags.3')]): 	option_list.append(ps('AdvSearch.menu.3'))
		else:																				option_list.append(ps('AdvSearch.menu.3')+':  '+options[ps('AdvSearch.tags.3')])
		if (''==options[ps('AdvSearch.tags.4')]): 	option_list.append(ps('AdvSearch.menu.4'))
		else:																				option_list.append(ps('AdvSearch.menu.4')+':  '+options[ps('AdvSearch.tags.4')])
		if (''==options[ps('AdvSearch.tags.5')]): 	option_list.append(ps('AdvSearch.menu.5'))
		else:																				option_list.append(ps('AdvSearch.menu.5')+':  '+options[ps('AdvSearch.tags.5')])
		if (''==options[ps('AdvSearch.tags.6')]): 	option_list.append(ps('AdvSearch.menu.6'))
		else:																				option_list.append(ps('AdvSearch.menu.6')+':  '+options[ps('AdvSearch.tags.6')])
		if (''==options[ps('AdvSearch.tags.7')]): 	option_list.append(ps('AdvSearch.menu.7'))
		else:																				option_list.append(ps('AdvSearch.menu.7')+':  '+options[ps('AdvSearch.tags.7')])
		option_list.append(																						 ps('AdvSearch.menu.8'))
		r=askSelection(option_list,txtHeader)
		if   (r==0): ### Do Advanced Search
			_param['url']+='&q['+ps('AdvSearch.tags.1')+']='+options[ps('AdvSearch.tags.1')]; 
			_param['url']+='&q['+ps('AdvSearch.tags.2')+']='+options[ps('AdvSearch.tags.2')]; 
			_param['url']+='&q['+ps('AdvSearch.tags.3')+']='+options[ps('AdvSearch.tags.3')]; 
			_param['url']+='&q['+ps('AdvSearch.tags.5')+']='+options[ps('AdvSearch.tags.5')]; 
			_param['url']+='&q['+ps('AdvSearch.tags.6')+']='+options[ps('AdvSearch.tags.6')]; 
			_param['url']+='&q['+ps('AdvSearch.tags.4')+']='+options[ps('AdvSearch.tags.4')]; 
			### if (options['year_to'] is not ''): _param['url']+='&q[year_to]='+options['year_to']; 
			deb('Advanced Searching',_param['url'])
			listItems(section, _param['url'], startPage=options['startPage'], numOfPages=options['numOfPages'], chck='AdvancedSearch')
			### listItems(section, _param['url'], _param['pageno'], _param['pagecount'], _param['genre'], _param['year'], _param['title'],chck='AdvancedSearch')
			### listItems(section=, url=, startPage='1', numOfPages='1', genre='', year='', stitle='', season='', episode='', html='', chck=''): # List: Movies or TV Shows
		elif (r==1): ### Change Title
			r2=showkeyboard(txtMessage=options[ps('AdvSearch.tags.1')],txtHeader="Title:  "+options[ps('AdvSearch.tags.1')],passwordField=False)
			if (r2 is not False): options[ps('AdvSearch.tags.1')]=r2
		elif (r==2): ### Change Description
			r2=showkeyboard(txtMessage=options['description'],txtHeader="Description:  "+options['description'],passwordField=False)
			if (r2 is not False): options['description']=r2
		elif (r==3): ### Change Actor
			r2=showkeyboard(txtMessage=options[ps('AdvSearch.tags.2')],txtHeader="Actor:  "+options[ps('AdvSearch.tags.2')],passwordField=False)
			if (r2 is not False): options[ps('AdvSearch.tags.2')]=r2
		#elif (r==4): ### Change Country
		elif (r==5): ### Change Year From
			r2=dialogbox_number(Header='Year From:'+options[ps('AdvSearch.tags.5')],n='01/01/'+options[ps('AdvSearch.tags.5')],type=0)
			if (r2 is not False) and (len(r2)==4): options[ps('AdvSearch.tags.5')]=r2
			if (r2 is not False) and ('/' in r2):  options[ps('AdvSearch.tags.5')]=r2.split('/')[2] ## <<<
			if (r2 is not False) and ('-' in r2):  options[ps('AdvSearch.tags.5')]=r2.split('-')[2]
		elif (r==6): ### Change Year To
			r2=dialogbox_number(Header='Year To:'  +options[ps('AdvSearch.tags.6')],n='01/01/'+options[ps('AdvSearch.tags.6')],type=0)
			if (r2 is not False) and (len(r2)==4): options[ps('AdvSearch.tags.6')]=r2
			if (r2 is not False) and ('/' in r2):  options[ps('AdvSearch.tags.6')]=r2.split('/')[2] ## <<<
			if (r2 is not False) and ('-' in r2):  options[ps('AdvSearch.tags.6')]=r2.split('-')[2]
		#elif (r==7): ### Change Genre
		elif (r==8): ### Cancel Advanced Search
			eod(); return
		#elif (r== -1): ### escape // right click or such.
		#	eod(); return
		## 
	#
	eod()
	return



##### /\ ##### Search #####
### ############################################################################################################
### ############################################################################################################
### ############################################################################################################
##### Modes #####
def check_mode(mode=''):
	deb('Mode',mode)
	if (mode=='') or (mode=='main') or (mode=='MainMenu'): Menu_MainMenu()
	#elif (mode=='PlayVideo'): 						PlayVideo(_param['url'], _param['infoLabels'], _param['listitem'])
	elif (mode=='PlayVideo'): 						PlayVideo(_param['url'],title=_param['title'],studio=_param['studio'],img=_param['img'],showtitle=_param['showtitle'],plot=_param['plot'])
	elif (mode=='PlayVideoA'): 						PlayVideo(_param['url'],title=_param['title'],studio=_param['studio'],img=_param['img'],showtitle=_param['showtitle'],plot=_param['plot'],autoplay=True)
	elif (mode=='PlayVideoB'): 						PlayVideo(_param['url'],title=_param['title'],studio=_param['studio'],img=_param['img'],showtitle=_param['showtitle'],plot=_param['plot'])
	elif (mode=='PlayURL'): 							PlayURL(_param['url'])
	elif (mode=='PlayTrailer'): 					PlayTrailer(_param['url'], _param['title'], _param['year'], _param['img'])
	elif (mode=='Settings'): 							_addon.addon.openSettings() #_plugin.openSettings()
	#elif (mode=='LoadCategories'): 				Menu_LoadCategories(_param['section'])
	#elif (mode=='BrowseAtoZ'): 					BrowseAtoZ(_param['section'])
	#elif (mode=='BrowseYear'): 						Menu_BrowseByYear(_param['section'])
	elif (mode=='BrowseLast'): 						Menu_Last()
	elif (mode=='BrowseMenu2'): 					Menu_2()
	elif (mode=='BrowseGenre'): 					Menu_BrowseByGenre(_param['section'])
	elif (mode=='BrowseGenre2'): 					Menu_BrowseByGenre2(_param['section'])
	elif (mode=='BrowseAZ'): 							Menu_BrowseByAZ(_param['section'],_param['url'])
	elif (mode=='SelectAZ'): 							Select_AZ(_param['url'])
	elif (mode=='SelectSort'): 						Select_Sort(_param['url'],_param['title'])
	elif (mode=='SelectGenre'): 					Select_Genre(_param['url'])
	#elif (mode=='BrowseCountry'): 				Menu_BrowseByCountry(_param['section'])
	#elif (mode=='BrowseLatest'): 				BrowseLatest(_param['section'])
	#elif (mode=='BrowsePopular'): 				BrowsePopular(_param['section'])
	#elif (mode=='GetResults'): 					GetResults(_param['section'], genre, letter, page)
	elif (mode=='GetTitles'): 						listItems(_param['section'], _param['url'], _param['pageno'], _param['pagecount'], _param['genre'], _param['year'], _param['title'])
	elif (mode=='GetTitlesUpcoming'): 		listItems_Upcoming(_param['section'], _param['url'], _param['pageno'], _param['pagecount'], _param['genre'], _param['year'], _param['title'])
	elif (mode=='GetTitlesLatest'): 			listItems(_param['section'], _param['url'], _param['pageno'], _param['pagecount'], _param['genre'], _param['year'], _param['title'], chck=ps('LI.tv.latest.check'))
	elif (mode=='GetTitlesLatestWatched'): listItems(_param['section'],_param['url'], _param['pageno'], _param['pagecount'], _param['genre'], _param['year'], _param['title'], chck=ps('LI.tv.latest.watched.check'))
	elif (mode=='GetTitlesPopular'): 			listItems(_param['section'], _param['url'], _param['pageno'], _param['pagecount'], _param['genre'], _param['year'], _param['title'], chck=ps('LI.tv.popular.all.check'))
	elif (mode=='GetTitlesHDPopular'): 		listItems(_param['section'], _param['url'], _param['pageno'], _param['pagecount'], _param['genre'], _param['year'], _param['title'], chck=ps('LI.movies.popular.hd.check'))
	elif (mode=='GetTitlesOtherPopular'): listItems(_param['section'], _param['url'], _param['pageno'], _param['pagecount'], _param['genre'], _param['year'], _param['title'], chck=ps('LI.movies.popular.other.check'))
	elif (mode=='GetTitlesNewPopular'): 	listItems(_param['section'], _param['url'], _param['pageno'], _param['pagecount'], _param['genre'], _param['year'], _param['title'], chck=ps('LI.movies.popular.new.check'))
	elif (mode=='GetLinks'): 							lLs('325273032032525032503252352052305923'); listLinks(_param['section'], _param['url'], showtitle=_param['showtitle'], showyear=_param['showyear'])
	elif (mode=='GetEpisodes'): 					listEpisodes(_param['section'], _param['url'], _param['img'], _param['title'], _param['season'])
	elif (mode=='TextBoxFile'): 					TextBox2().load_file(_param['url'],_param['title']); eod()
	elif (mode=='TextBoxUrl'):  					TextBox2().load_url( _param['url'],_param['title']); eod()
	elif (mode=='SearchForAirDates'):  		search_for_airdates(_param['title']); eod()
	elif (mode=='Search'):  							doSearchNormal(_param['section'],_param['title'])
	elif (mode=='AdvancedSearch'):  			doSearchAdvanced(_param['section'],_param['title'])
	elif (mode=='Bookmarks'):  						Bookmarks(_param['section'],_param['url'],_param['title'])
	elif (mode=='listBookmarks'):  				listBookmarks(_param['section'],_param['url'])
	elif (mode=='FavoritesList'):  		  	fav__list(_param['section'],_param['subfav'])
	elif (mode=='FavoritesEmpty'):  	 		fav__empty(_param['section'],_param['subfav'])
	elif (mode=='FavoritesRemove'):  			fav__remove(_param['section'],_param['title'],_param['year'],_param['subfav'])
	elif (mode=='FavoritesAdd'):  		  	fav__add(_param['section'],_param['title'],_param['year'],_param['img'],_param['fanart'],_param['subfav'])
	elif (mode=='sunNote'):  		   				sunNote( header=_param['title'],msg=_param['plot'])
	elif (mode=='deadNote'):  		   			deadNote(header=_param['title'],msg=_param['plot'])
	elif (mode=='LibrarySaveMovie'):  		Library_SaveTo_Movies(_param['url'],_param['img'],_param['showtitle'],_param['showyear'])
	elif (mode=='LibrarySaveTV'):  				Library_SaveTo_TV(_param['section'], _param['url'],_param['img'],_param['showtitle'],_param['showyear'],_param['country'],_param['season'],_param['episode'],_param['episodetitle'])
	elif (mode=='LibrarySaveEpisode'):  	Library_SaveTo_Episode(_param['url'],_param['img'],_param['title'],_param['showyear'],_param['country'],_param['season'],_param['episode'],_param['episodetitle'])
	elif (mode=='PlayLibrary'): 					PlayLibrary(_param['section'], _param['url'], showtitle=_param['showtitle'], showyear=_param['showyear'])
	elif (mode=='Download'): 							print _param; DownloadRequest(_param['section'], _param['url'],_param['img'],_param['studio']); eod()
	elif (mode=='DownloadStop'): 					DownloadStop(); eod()
	#elif (mode=='LatestThreads'): 				News_LatestThreads(_param['url'],_param['title'])
	elif (mode=='GetLatestSearches'): 		listLatestSearches(_param['section'],_param['url'])
	elif (mode=='UsersShowProfileAccountInfo'): UsersShowPersonInfo(mode, _param['section'],_param['url'])
	elif (mode=='ChangeFanartList'):			ChangeFanartList(_param['section'],_param['subfav'],_param['url'],_param['fanart'],_param['img'],_param['studio'])
	elif (mode=='ChangeFanartUpdate'):		ChangeFanartUpdate(_param['section'],_param['subfav'],_param['url'],_param['title'])
	elif (mode=='TestProxies'):  		  		TestProxies()
	elif (mode=='GrabNewProxy'):  		  	GrabNewProxy()
	elif (mode=='AddVisit'):							
		try: visited_add(_param['title']); 	RefreshList(); 
		except: pass
	elif (mode=='RemoveVisit'):							
		try: visited_remove(_param['title']); RefreshList(); 
		except: pass
	elif (mode=='EmptyVisit'):						
		try: visited_empty(); RefreshList(); 
		except: pass
	elif (mode=='refresh_meta'):					refresh_meta(addpr('video_type',''),addpr('title',''),addpr('imdb_id',''),addpr('alt_id',''),addpr('year',''))
	elif (mode=='System.Exec'): 				eod(); xbmc.executebuiltin("XBMC.System.Exec(%s)" % _param['url']); xbmc.sleep(1000); DoA("Back"); 
	elif (mode=='System.ExecWait'): 		eod(); xbmc.executebuiltin("XBMC.System.ExecWait(%s)" % _param['url']); xbmc.sleep(1000); DoA("Back"); 
	else: deadNote(header='Mode:  "'+mode+'"',msg='[ mode ] not found.'); Menu_MainMenu()

# {'showyear': '', 'infoLabels': "
# {'Plot': '', 'Episode': '11', 'Title': u'Transformers Prime', 'IMDbID': '2961014', 'host': 'filenuke.com', 
# 'IMDbURL': 'http://anonym.to/?http%3A%2F%2Fwww.imdb.com%2Ftitle%2Ftt2961014%2F', 
# 'ShowTitle': u'Transformers Prime', 'quality': 'HDTV', 'Season': '3', 'age': '25 days', 
# 'Studio': u'Transformers Prime  (2010):  3x11 - Persuasion', 'Year': '2010', 'IMDb': '2961014', 
# 'EpisodeTitle': u'Persuasion'}", 'thetvdbid': '', 'year': '', 'special': '', 'plot': '', 
# 'img': 'http://static.solarmovie.so/images/movies/1659175_150x220.jpg', 'title': '', 'fanart': '', 'dbid': '', 'section': 'tv', 'pagesource': '', 'listitem': '<xbmcgui.ListItem object at 0x14C799B0>', 'episodetitle': '', 'thumbnail': '', 'thetvdb_series_id': '', 'season': '', 'labs': '', 'pageurl': '', 'pars': '', 'user': '', 'letter': '', 'genre': '', 'by': '', 'showtitle': '', 'episode': '', 'name': '', 'pageno': 0, 'pagecount': 1, 'url': '/link/show/1466546/', 'country': '', 'subfav': '', 'mode': 'Download', 'tomode': ''}

##### /\ ##### Modes #####
### ############################################################################################################
deb('param >> studio',_param['studio'])
deb('param >> season',_param['season'])
deb('param >> section',_param['section'])
deb('param >> img',_param['img'])
deb('param >> showyear',_param['showyear'])
deb('param >> showtitle',_param['showtitle'])
deb('param >> title',_param['title'])
deb('param >> url',_param['url']) ### Simply Logging the current query-passed / param -- URL
deb('param >> dbid',addpr('dbid'))
deb('param >> imdbid',addpr('imdbid'))
check_mode(_param['mode']) ### Runs the function that checks the mode and decides what the plugin should do. This should be at or near the end of the file.
### ############################################################################################################
### ############################################################################################################
### ############################################################################################################
