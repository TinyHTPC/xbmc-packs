### ############################################################################################################
###	#	
### # Project: 			#		Config.py - by The Highway 2013.
### # Author: 			#		The Highway
### # Version:			#		(ever changing)
### # Description: 	#		My Project Config File
###	#	
### ############################################################################################################
### ############################################################################################################
### Imports ###
import xbmc,xbmcplugin,xbmcgui,xbmcaddon,xbmcvfs
import re,os,sys,string,StringIO,logging,random,array,time,datetime
#from t0mm0.common.addon import Addon
#try: 		from t0mm0.common.addon 				import Addon
#except: from t0mm0_common_addon 				import Addon
try: 			from addon.common.addon 				import Addon
except:
	try: 		from t0mm0.common.addon 				import Addon
	except: 
		try: from z_t0mm0_common_addon 				import Addon
		except: pass

### ############################################################################################################
### ############################################################################################################
### ############################################################################################################
### Plugin Settings ###
def ps(x):
	try:
		return {
			'__plugin__': 					"KissAnime"
			,'__authors__': 				"[COLOR white]The[COLOR tan]Highway[/COLOR][/COLOR]"
			,'__credits__': 				""
			,'_addon_id': 					"plugin.video.kissanime"
			,'_plugin_id': 					"plugin.video.kissanime"
			,'_domain_url': 				"http://kissanime.com"
			,'_database_name': 			"kissanime"
			,'common_word': 				"Anime"
			,'common_word2': 				"Watch"
			,'_addon_path_art': 		"art"
			,'content_tvshows': 		"tvshows" #tvshows #movies
			,'content_episodes': 		"episodes"
			,'content_links': 			"list"
			,'proxy1x': 						"http://69.197.132.80:3128"
			,'proxy2x': 						"http://50.2.64.206:7808"
			,'proxy': 							"http://173.213.96.229:7808"
			,'proxy_o1': 						"http://50.2.64.206:7808"
			,'proxy_old': 					"http://192.69.200.37:7808"
			,'proxy3': 							"http://198.27.97.214:7808"
			,'proxy4': 							"http://72.29.101.11:7808"
			,'proxy5': 							"http://198.56.208.37:8089"
			,'proxy6': 							"http://199.241.138.201:7808"
			,'special.home.addons': 'special:'+os.sep+os.sep+'home'+os.sep+'addons'+os.sep
			,'special.home': 				'special:'+os.sep+os.sep+'home'
			,'img_kisslogo':				'http://kissanime.com/Content/images/logo.png'
			,'img_next':						'http://kissanime.com/Content/images/next.png'
			,'img_prev':						'http://kissanime.com/Content/images/previous.png'
			,'img_az':							'http://kissanime.com/Content/images/logo.png'
			,'img_search':					'http://kissanime.com/Content/images/read.png'
			,'img_hot':							'http://kissanime.com/Content/images/hot.png'
			,'img_updated':					'http://kissanime.com/Content/images/newupdate.png'
			,'GENRES_Notes': 				{'Dub':"English voices, no subtitle.",
															'Movie':"Movie",
															'Special':"Special",
															'OVA':"Original Animation Video & Original Video Animation (OAV / OVA) are interchangeable terms used in Japan to refer to animation that is released directly to the video market without first going through a theatrical release or television broadcast.\n\nFurthermore, OVA are supposed to have original scripts, although there are exceptions. They can be based on a Manga or TV series, but the particular episode should be original.",
															'Music':"Anime whose central theme revolves around singers/idols or people playing instruments. This category is not intended for finding AMVs (Animated Music Videos).",
															'Action':"Plays out mainly through a clash of physical forces. Frequently these stories have fast cuts, tough characters making quick decisions and usually a beautiful girl nearby. Anything quick and most likely a thin storyline.",
															'Adventure':"Exploring new places, environments or situations. This is often associated with people on long journeys to places far away encountering amazing things, usually not in an epic but in a rather gripping and interesting way.",
															'Cars':"Anime whose central theme revolves around cars and probably car races. A single character's obsession for cars does not mean that it should belong to this genre. Most of these stories also are in the action genre.",
															'Cartoon':"Not anime",
															'Comedy':"Multiple characters and/or events causing hilarious results. These stories are built upon funny characters, situations and events.",
															'Dementia':"Anime that have mind-twisting plots.",
															'Demons':"Anime that are set in a world where demons and other dark creatures play a significant role - the main character may even be one.",
															'Drama':"Anime that often show life or characters through conflict and emotions. In general, the different parts of the story tend to form a whole that is greater than the sum of the parts. In other words, the story has a message that is bigger than just the story line itself.",
															'Ecchi':"Anime that contain a lot of sexual innuendo. The translation of this letter (Ecchi is the letter 'H' in Japanese) is pervert. Ecchi is about panties (pantsu) and bra/breast showing, situations with \"sudden nudity\" and of course, subtle hints or sexual thoughts. Ecchi does not describe actual sex acts or show any intimate body parts except for bare breasts and buttocks. Ecchi is almost always used for humor.",
															'Fantasy':"Anime that are set in a mythical world quite different from modern-day Earth. Frequently this world has magic and/or mythical creatures such as dragons and unicorns. These stories are sometimes based on real world legends and myths. Frequently fantasies describe tales featuring magic, brave knights, damsels in distress, and/or quests.",
															'Game':"Anime whose central theme is based on a non-violent, non-sports game, like go, chess, trading card games or computer/video games.",
															'Harem':"Anime that involves one lead male character and many cute/pretty female support characters. Typically, the male lead ends up living with many female support characters within the same household. The lead male typically represents the average guy who is shy, awkward, and girlfriendless. While each female character surround the lead male possesses distinct physical and personality traits, those traits nevertheless represent different stereotypical roles that play on popular Japanese fetishes; i.e. the librarian/genius, tomboy, little sister, and older woman. Some anime that are under the harem genre are: Love Hina, Girls Bravo, Maburaho, and Sister Princess.",
															'Historical':"Anime whose setting is in the past. Frequently these follow historical tales, sagas or facts.",
															'Horror':"Anime whose focus is to scare the audience.",
															'Josei':"Josei",
															'Kids':"Anime whose target audience is children. This does not necessarily mean that the character(s) are children or that an anime whose main character(s) are children is appropriate for this genre.",
															'Magic':"Anime whose central theme revolves around magic. Things that are \"out of this world\" happen - incidents that cannot be explained by the laws of nature or science. Usually wizards/witches indicate that it is of the \"Magic\" type. This is a sub-genre of fantasy.",
															'Martial Arts':"Anime whose central theme revolves around martial arts. This includes all hand-to-hand fighting styles, including Karate, Tae-Kwon-Do and even Boxing. Weapons use, like Nunchaku and Shuriken are also indications of this genre. This is a sub-genre of action.",
															'Mecha':"Anime whose central theme involves mechanical things. This genre is mainly used to point out when there are giant robots. Human size androids are in general not considered \"Mecha\" but \"SciFi\".",
															'Military':"An anime series/movie that has a heavy militaristic feel behind it.",
															'Mystery':"Anime where characters reveal secrets that may lead a solution for a great mystery. This is not necessarily solving a crime, but can be a realization after a quest.",
															'ONA':"ONA",
															'Parody':"Anime that imitate other stories (can be from TV, film, books, historical events, ...) for comic effect by exaggerating the style and changing the content of the original. Also known as spoofs. This is a sub-genre of comedy.",
															'Police':"Anime where a police organization are a major part of the story.",
															'Psychological':"Often when two or more characters prey each others' minds, either by playing deceptive games with the other or by merely trying to demolish the other's mental state.",
															'Romance':"Anime whose story is about two people who each want [sometimes unconciously] to win or keep the love of the other. This kind of anime might also fall in the \"Ecchi\" category, while \"Romance\" and \"Hentai\" generally contradict each other.",
															'Samurai':"Anime whose main character(s) are samurai, the old, but not forgotten, warrior cast of medieval Japan.",
															'School':"Anime which are mainly set in a school environment.",
															'Sci-Fi':"Anime where the setting is based on the technology and tools of a scientifically imaginable world. The majority of technologies presented are not available in the present day and therefore the Science is Fiction. This incorporates any possible place (planets, space, underwater, you name it).",
															'Seinen':"Seinen",
															'Shoujo':"Anime that are targeted towards the \"young girl\" market. Usually the story is from the point of view of a girl and deals with romance, drama or magic.",
															'Shoujo Ai':"Anime whose central theme is about a relationship (or strong affection, not usually sexual) between two girls or women. Shoujo Ai literally means \"girl love\".",
															'Shounen':"In the context of manga and associated media, the word shounen refers to a male audience roughly between the ages of 10 and 18. In Japanese, the word means simply \"young male\", and has no anime/manga-related connotations at all. It does not comprise a style or a genre per se, but rather indicates the publisher`s intended target demographic. Still, while not mandatory, some easily identifiable traits are generally common to shounen works, such as: high-action, often humorous plots featuring male protagonists; camaraderie between male friends; sports teams and fighting squads (usually coupled with the aforementioned camaraderie); unrealistically attractive female characters (see fanservice). Additionally, the art style of shounen tends to be less flowery than that of shoujo and the plots tend to be less complex than seinen, but neither of those is a requirement.\nAnime that are targeted towards the \"young boy\" market. The usual topics for this involve fighting, friendship and sometimes super powers.",
															'Shounen Ai':"Anime whose central theme is about a relationship (or strong affection, not usually sexual) between two boys or men. Shounen Ai literally means \"boy love\", but could be expressed as \"male bonding\".",
															'Slice of Life':"Anime with no clear central plot. This type of anime tends to be naturalistic and mainly focuses around the main characters and their everyday lives. Often there will be some philosophical perspectives regarding love, relationships, life etc. tied into the anime. The overall typical moods for this type of anime are cheery and carefree, in other words, it is your \"feel-good\" kind of anime. Some anime that are under the slice of life genre are: Ichigo Mashimaro, Fruits Basket, Aria the Natural, Honey and Clover, and Piano.",
															'Space':"Anime whose setting is in outer space, not on another planet, nor in another dimension, but space. This is a sub-genre of scifi.",
															'Sports':"Anime whose central theme revolves around sports, examples are tennis, boxing and basketball.",
															'Super Power':"Anime whose main character(s) have powers beyond normal humans. Often it looks like magic, but can't really be considered magic; usually ki-attacks, flying or superhuman strength.",
															'Supernatural':"Anime of the paranormal stature. Demons, vampires, ghosts, undead, etc.",
															'Thriller':"Thriller",
															'Vampire':"Anime whose main character(s) are vampires or at least vampires play a significant role in the story.",
															'Yuri':"Anime whose central theme is a sexual relationship between two girls or women. This implies Hentai."}
			,'GENRES': 							['Dub','Movie','Special','OVA','Music','Action','Adventure','Cars','Cartoon','Comedy','Dementia','Demons','Drama','Ecchi','Fantasy','Game','Harem','Historical','Horror','Josei','Kids','Magic','Martial Arts','Mecha','Military','Mystery','ONA','Parody','Police','Psychological','Romance','Samurai','School','Sci-Fi','Seinen','Shoujo','Shoujo Ai','Shounen','Shounen Ai','Slice of Life','Space','Sports','Super Power','Supernatural','Thriller','Vampire','Yuri']
			,'GENRES_': 						['Action','Adventure','Cars','Cartoon','Comedy','Dementia','Demons','Drama','Ecchi','Fantasy','Game','Harem','Historical','Horror','Josei','Kids','Magic','Martial Arts','Mecha','Military','Movie','Music','Mystery','ONA','OVA','Parody','Police','Psychological','Romance','Samurai','School','Sci-Fi','Seinen','Shoujo','Shoujo Ai','Shounen','Shounen Ai','Slice of Life','Space','Special','Sports','Super Power','Supernatural','Thriller','Vampire','Yuri']
			,'COUNTRIES': 					['Afghanistan','Albania','Algeria','Andorra','Angola','Argentina','Armenia','Aruba','Australia','Austria','Bahamas','Bahrain','Bangladesh','Barbados','Belarus','Belgium','Bermuda','Bolivia','Bosnia and Herzegovina','Botswana','Brazil','Bulgaria','Cambodia','Cameroon','Canada','Chad','Chile','China','Colombia','Costa Rica','Croatia','Cuba','Cyprus','Czech Republic','Czechoslovakia','Democratic Republic of the Congo','Denmark','Dominican Republic','East Germany','Ecuador','Egypt','El Salvador','Estonia','Ethiopia','Federal Republic of Yugoslavia','Finland','France','Georgia','Germany','Ghana','Greece','Guatemala','Haiti','Honduras','Hong Kong','Hungary','Iceland','India','Indonesia','Iran','Ireland','Isle of Man','Israel','Italy','Jamaica','Japan','Kazakhstan','Kenya','Kuwait','Latvia','Lebanon','Liberia','Libya','Liechtenstein','Lithuania','Luxembourg','Malaysia','Maldives','Malta','Mexico','Moldova','Monaco','Mongolia','Morocco','Namibia','Nepal','Netherlands','Netherlands Antilles','New Zealand','Nicaragua','Nigeria','North Korea','Norway','Occupied Palestinian Territory','Pakistan','Palestine','Panama','Papua New Guinea','Paraguay','Peru','Philippines','Poland','Portugal','Puerto Rico','Qatar','Republic of Macedonia','Romania','Russia','Rwanda','Senegal','Serbia','Serbia and Montenegro','Singapore','Slovakia','Slovenia','South Africa','South Korea','Soviet Union','Spain','Sri Lanka','Sweden','Switzerland','Taiwan','Tajikistan','Tanzania','Thailand','Togo','Trinidad and Tobago','Tunisia','Turkey','U.S. Virgin Islands','UK','Ukraine','United Arab Emirates','United States Minor Outlying Islands','Uruguay','USA','Venezuela','Vietnam','West Germany','Yugoslavia','Zaire','Zambia','Zimbabwe']
			,'default_art_ext': 		'.png'
			,'default_cFL_color': 	'green'
			,'cFL_color': 					'lime'
			,'cFL_color2': 					'yellow'
			,'cFL_color3': 					'red'
			,'cFL_color4': 					'grey'
			,'cFL_color5': 					'white'
			,'cFL_color6': 					'blanchedalmond'
			,'default_section': 		'movies'
			,'section.wallpaper':		'wallpapers'
			,'section.movie': 			'movies'
			,'section.trailers':		'trailers'
			,'section.trailers.popular':			'trailerspopular'
			,'section.trailers.releasedate':	'trailersreleasedate'
			,'section.users':				'users'
			,'section.tv': 					'tv'
			,'img.comingsoon': 			'http://mirror.its.dal.ca/xbmc/addons/frodo/plugin.video.trailer.addict/icon.png'
			,'img.usersection': 		'http://i1.wp.com/www.solarmovie.so/images/gravatar_default.png'
			,'img.userdefault': 		'http://i1.wp.com/www.solarmovie.so/images/gravatar_default.png'
			,'Trailers.GENRES': 		['All','Action','Adult','Adventure','Animation','Biography','Comedy','Crime','Documentary','Drama','Family','Fantasy','Film-Noir','Game-Show','History','Horror','Music','Musical','Mystery','News','Reality-TV','Romance','Sci-Fi','Short','Sport','Talk-Show','Thriller','War','Western']
			,'meta.movie.domain': 	'http://www.themoviedb.org'
			,'meta.movie.search': 	'http://www.themoviedb.org/search?query=TT'
			,'meta.tv.domain': 			'http://www.thetvdb.com'
			,'meta.tv.search': 			'http://www.thetvdb.com/index.php?seriesname=&fieldlocation=2&language=7&genre=&year=&network=&zap2it_id=&tvcom_id=&order=translation&addedBy=&searching=Search&tab=advancedsearch&imdb_id=TT'
			,'meta.tv.page': 				'http://www.thetvdb.com/index.php?tab=series&lid=7&id='
			,'meta.tv.fanart.url': 	'http://www.thetvdb.com/banners/fanart/original/'
			,'meta.tv.fanart.url2': '-1.jpg'
			,'meta.tv.fanart.all.url': 'http://thetvdb.com/?tab=seriesfanart&id=%s'
			,'meta.tv.fanart.all.match':	'<a href="(banners/fanart/original/\d+-(\d+)\.jpg)" target="_blank">View Full Size</a>'
			,'meta.tv.fanart.all.prefix': 'http://thetvdb.com/'
			,'meta.tv.poster.url': 	'http://www.thetvdb.com/banners/posters/'
			,'meta.tv.poster.url2': '-1.jpg'
			,'domain.search.movie': 'http://www.solarmovie.so/movie/search/'
			,'domain.search.tv': 		'http://www.solarmovie.so/tv/search/'
			,'domain.url.tv': 			'/tv'
			,'domain.url.movie': 		''
			,'LatestThreads.url':		'http://www.solarmovie.so/'
			,'changelog.local': 		'changelog.txt'
			,'changelog.url': 			'https://raw.github.com/HIGHWAY99/plugin.video.kissanime/master/changelog.txt'
			,'news.url': 						'https://raw.github.com/HIGHWAY99/plugin.video.kissanime/master/news.txt'
			,'newi':								chr(65)+chr(100)+chr(118)+chr(83)+chr(101)+chr(97)+chr(114)+chr(99)+chr(104)+chr(46)+chr(116)+chr(97)+chr(103)+chr(115)+chr(46)+chr(100)
			,'listSeasons.match.img': 				'coverImage">.+?src="(.+?)"'
			,'listSeasons.match.seasons': 		"toggleSeason\('(\d+)'\)"
			,'listSeasons.prefix.seasons': 		'[COLOR goldenrod]S[/COLOR]eason '
			,'setview.seasons': 							515
			,'setview.episodes': 							515
			,'setview.movies': 								515
			,'setview.tv': 										515
			,'setview.tv.latestepisodes': 		515
			,'domain.thumbnail.default': 			'http://static.solarmovie.so/images/movies/0000000_150x220.jpg'
			,'rating.max': 										'10'
			,'cMI.favorites.tv.add.url': 			'XBMC.RunPlugin(%s?mode=%s&section=%s&title=%s&year=%s&img=%s&fanart=%s&country=%s&plot=%s&genre=%s&url=%s&dbid=%s&subfav=%s)'
			,'cMI.favorites.tv.add.name': 		'Add Favorite'
			,'cMI.favorites.tv.add.mode': 		'FavoritesAdd'
			,'cMI.favorites.movie.add.url': 	'XBMC.RunPlugin(%s?mode=%s&section=%s&title=%s&year=%s&img=%s&fanart=%s&country=%s&plot=%s&genre=%s&url=%s&subfav=%s)'
			,'cMI.favorites.tv.remove.url': 	'XBMC.RunPlugin(%s?mode=%s&section=%s&title=%s&year=%s&img=%s&fanart=%s&country=%s&plot=%s&genre=%s&url=%s&dbid=%s&subfav=%s)'
			,'cMI.favorites.tv.remove.name': 	'Remove Favorite'
			,'cMI.favorites.tv.remove.mode': 	'FavoritesRemove'
			,'cMI.favorites.movie.remove.url': 'XBMC.RunPlugin(%s?mode=%s&section=%s&title=%s&year=%s&img=%s&fanart=%s&country=%s&plot=%s&genre=%s&url=%s&subfav=%s)'
			,'cMI.airdates.find.name': 				'Find AirDates'
			,'cMI.airdates.find.url': 				'XBMC.RunPlugin(%s?mode=%s&title=%s)'
			,'cMI.airdates.find.mode': 				'SearchForAirDates'
			,'cMI.showinfo.name': 						'Show Information'
			,'cMI.showinfo.url': 							'XBMC.Action(Info)'
			,'cMI.1ch.search.folder': 				'plugin.video.1channel'
			,'cMI.1ch.search.name': 					'Search 1Channel'
			,'cMI.1ch.search.url': 						'XBMC.Container.Update(%s?mode=7000&section=%s&query=%s)'
			,'cMI.1ch.search.plugin': 				'plugin://plugin.video.1channel/'
			,'cMI.1ch.search.section': 				'movies'
			,'cMI.1ch.search.section.tv': 		'tv'
			,'cMI.primewire.search.folder': 	'plugin.video.primewire'
			,'cMI.primewire.search.name': 		'Search PrimeWire.ag'
			,'cMI.primewire.search.url': 			'XBMC.Container.Update(%s?mode=7000&section=%s&query=%s)'
			,'cMI.primewire.search.plugin': 	'plugin://plugin.video.primewire/'
			,'cMI.primewire.search.section': 	'movies'
			,'cMI.primewire.search.section.tv':	'tv'
			,'cMI.jDownloader.addlink.url':		'XBMC.RunPlugin(plugin://plugin.program.jdownloader/?action=addlink&url=%s)'
			,'LI.movies.match.items': 				'class="coverImage" title="(.+?)".+?href="(.+?)".+?src="(.+?)".+?<a title=".+?\(([\d]+)\)'
			,'LI.movies.match.items2': 				'class="coverImage" title="(.+?)"[\n]\s+href="(.+?)">.+?src="(http://static\.solarmovie\.so/images/movies/\d+_\d+x\d+\.jpg)".+?<a\stitle=".+?\(([\d]+)\)'
			,'LI.movies.match.items3': 				'class="coverImage" title="(.+?)"[\n]\s+href="(.+?)">.+?src="(http://static\.solarmovie\.so/images/movies/\d+_\d+x\d+\.jpg)".+?<a\stitle=".+?\(([\d]+)\)'
			,'LI.movies.latest.split1': 			'<h2>Latest Movies</h2>'
			,'LI.movies.latest.split2': 			'<h2>'
			,'LI.movies.latest.check': 				'Latest'
			,'LI.movies.popular.new.split1': 	'<h2>Most Popular New Movies</h2>'
			,'LI.movies.popular.new.split2': 	'<h2>'
			,'LI.movies.popular.new.check': 	'NewPopular'
			,'LI.movies.popular.hd.split1': 	'<h2>Most Popular Movies in HD</h2>'
			,'LI.movies.popular.hd.split2': 	'<h2>'
			,'LI.movies.popular.hd.check': 		'HDPopular'
			,'LI.movies.popular.other.split1':'<h2>Other Popular Movies</h2>'
			,'LI.movies.popular.other.split2':'<h2>'
			,'LI.movies.popular.other.check': 'OtherPopular'
			,'LI.tv.latest.watched.check':		'LatestWatched'
			,'LI.tv.latest.match.items': 			'__(.+?) s(\d+)e(\d+) (.+?)__'
			,'LI.tv.latest.check': 						'Latest'
			,'LI.tv.latest.split1': 					'<h2>Most Popular New TV Shows</h2>'
			,'LI.tv.latest.split2': 					'<h3>'
			,'LI.tv.popular.all.check': 			'Popular'
			,'LI.tv.popular.all.split1': 			'<h2>Most Popular TV Shows</h2>'
			,'LI.tv.popular.all.split2': 			'<h2>'
			,'LI.tv.popular.new.check': 			'NewPopular'
			,'LI.tv.popular.new.split1': 			'<h2>Latest TV Shows</h2>'
			,'LI.tv.popular.new.split2': 			'<h3>'
			,'LI.tv.match.items': 						'class="coverImage" title="(.+?)".+?href="(.+?)".+?src="(.+?)".+?<a title=".+?\(([\d]+)\)'
			,'LI.nextpage.name': 							'  [COLOR goldenrod]>  [COLOR red]Next[/COLOR]...[/COLOR]'
			,'LI.nextpage.match': 						'<li><a href=".+?\?.*?page=([\d]+)" page=[\d]+>&rsaquo; Next </a></li>'
			,'LI.nextpage.check': 						'>&rsaquo; Next </a></li>'
			,'LI.page.param': 								'?page='
			,'LI.page.find': 									'<li><a href=".+?page=([\d]+)" page="[\d]+">'
			,'BrowseByYear.tv.url1': 					'/tv/watch-tv-shows-'
			,'BrowseByYear.tv.url2': 					'.html'
			,'BrowseByYear.movie.url1': 			'/watch-movies-of-'
			,'BrowseByYear.movie.url2': 			'.html'
			,'BrowseByGenre.tv.url1': 				'/tv/watch-'
			,'BrowseByGenre.tv.url2': 				'-tv-shows.html'
			,'BrowseByGenre.movie.url1': 			'/watch-'
			,'BrowseByGenre.movie.url2': 			'-movies.html'
			,'BrowseByYear.thisyear': 				2013
			,'BrowseByYear.earliestyear': 		1930
			,'BrowseByYear.range.by': 				-1
			,'AlphaStrand': 									'/'
			,'Hosters.icon.url': 							'http://www.google.com/s2/favicons?domain='
			,'LLinks.compile.hostersA': 			'<tr id=.+?href="(.+?)">(.+?)<.+?class="qualityCell">(.*?)<.+?<td class="ageCell .+?">(.+?)</td>'
			,'LLinks.compile.hosters': 				'<tr id=.+?href="(.+?)">\n*\s*(.+?)\s*<.+?class="qualityCell">\n*\s*(.*?)\s*<.+?<td class="ageCell .+?">\n*\s*(.+?)\s*</td>'
			,'LLinks.compile.hosters2': 			'<tr id=.+?href="(/link/show/\d+/)">(.+?)<.+?class="qualityCell">(.+?)<.+?<td class="ageCell .+?">(.+?)</td>'
			,'LLinks.compile.imdb.url_id': 		'<strong>IMDb ID:</strong>[\n]\s+<a href="(.+?)">(\d+)</a>'
			,'LLinks.compile.show.plot': 			'<p id="plot_\d+">(.+?)</p>'
			,'LLinks.compile.show.title_year': '<title>Watch Full (.+?) \((.+?)\) .+?</title>'
			,'LLinks.compile.show_episode.info': '<title>Watch (.+?) Online for Free - (.+?) - .+? - (\d+)x(\d+) - SolarMovie</title>'
			,'AdvSearch.menu.0': 		'0.) Do Search >>'
			,'AdvSearch.menu.1': 		'1.) Title       '
			,'AdvSearch.menu.2': 		'2.) Description '
			,'AdvSearch.menu.3': 		'3.) Actor       '
			,'AdvSearch.menu.4': 		'4.) Country[N/A]'
			,'AdvSearch.menu.5': 		'5.) Year (From) '
			,'AdvSearch.menu.6': 		'6.) Year (To)   '
			,'AdvSearch.menu.7': 		'7.) Genre  [N/A]'
			,'AdvSearch.menu.8': 		'8.) Cancel      '
			,'AdvSearch.url.tv': 		'http://www.solarmovie.so/advanced-search/?'
			,'AdvSearch.url.movie': 'http://www.solarmovie.so/advanced-search/?'
			,'AdvSearch.tags.d': 		[105,99,138,6162,623,101,23,235,32,12,122,82,12,23,53,34,55,20,194,2,12312,1,121,12,23,2,6,26,27,26,52,23,25,23]
			,'AdvSearch.tags.0': 		'is_series'
			,'AdvSearch.tags.1': 		'title'
			,'AdvSearch.tags.2': 		'actor'
			,'AdvSearch.tags.3': 		'description'
			,'AdvSearch.tags.4': 		'country'
			,'AdvSearch.tags.5': 		'year_from'
			,'AdvSearch.tags.6': 		'year_to'
			,'AdvSearch.tags.7': 		'genre'
			,'AdvSearch.tags.8': 		''
			,'bracket1':						'/'
			,'User-Agent1': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3'
			,'User-Agent2': 'Mozilla/5.0 (Windows NT 6.2; rv:22.0) Gecko/20130405 Firefox/23.0'
			,'User-Agent2': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:24.0) Gecko/20100101 Firefox/24.0'
			,'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; en-US; rv:24.0) Gecko/20100101 Firefox/24.0'
			#,'User-AgentPSP': 'Mozilla/4.0 (PSP (PlayStation Portable); 2.00) Gecko/20100101 Firefox/24.0'
			,'User-Agent2': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3'
			,'User-Agent2': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3'
			,'User-Agent2': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3'
			,'User-Agent2': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3'
			,'User-Agent2': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3'
			,'User-Agent2': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3'
			,'User-Agent2': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3'
			,'User-Agent2': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3'
			,'User-Agent2': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3'
##		,'LLinks.compile.': 							
#			,'': 		''
#			,'': 
#			,'': 
		}[x]
	except: return ''
_art_DefaultExt  ='.png'
_cFL_DefaultColor='lime'

def psgn(x,t=".png"):
	s="http://i.imgur.com/"; 
	try:
		return {
			'action': 					s+"Q12cars"+t
			,'adventure': 			s+"wq3rlj8"+t
			,'cars': 						s+"e9n9Hih"+t
			,'cartoon': 				s+"yrrvbzw"+t
			,'comedy': 					s+"FU3VJGg"+t
			,'dementia': 				s+"trimFik"+t
			,'demons': 					s+"NHLTav4"+t
			,'drama': 					s+"w7R77Dj"+t
			,'dub': 						s+"3nc4UkN"+t
			,'ecchi': 					s+"2Y7s1d9"+t
			,'fantasy': 				s+"tspZm16"+t
			,'game': 						s+"NSLV38b"+t
			,'harem': 					s+"VSpcIo4"+t
			,'historical': 			s+"iyxap9I"+t
			,'horror': 					s+"EueQPn7"+t
			,'josei': 					s+"hR2UNOm"+t
			,'kids': 						s+"yzh5nBq"+t
			,'magic': 					s+"DOy6zZd"+t
			,'martial arts': 		s+"Nw4rjxJ"+t
			,'mecha': 					s+"XCZYIZo"+t
			,'military': 				s+"ZMXs7Gl"+t
			,'movie': 					s+"55YtzvJ"+t
			,'music': 					s+"tgcLRfv"+t
			,'mystery': 				s+"37MUY4c"+t
			,'ona': 						s+"WvIeCaj"+t
			,'ova': 						s+"6GPcrWB"+t
			,'parody': 					s+"3hBYM4k"+t
			,'police': 					s+"zl4qBvk"+t
			,'psychological': 	s+"75bP7sP"+t
			,'romance': 				s+"ko0OKE4"+t
			,'samurai': 				s+"DDoZmKP"+t
			,'school': 					s+"FlS7hEm"+t
			,'sci-fi': 					s+"3B0dkvt"+t
			,'seinen': 					s+"6vc6cwB"+t
			,'shoujo': 					s+"JAsp9PL"+t
			,'shoujo ai': 			s+"PaLhEhj"+t
			,'shounen': 				s+"PeXK8An"+t
			,'shounen ai': 			s+"uvaepAZ"+t
			,'slice of life': 	s+"rh4voyt"+t
			,'space': 					s+"QReD8P3"+t
			,'special': 				s+"lph1IaX"+t
			,'sports': 					s+"Ji1o6uG"+t
			,'super power': 		s+"6mHg5s6"+t
			,'supernatural': 		s+"8mAz2dT"+t
			,'thriller': 				s+"ZbW3BKy"+t
			,'vampire': 				s+"Kn9Yi7C"+t
			,'yuri': 						s+"VylolyV"+t
			,'a': 		s+"OvFHLK2"+t
			,'b': 		s+"ezem9mn"+t
			,'c': 		s+"707ILz1"+t
			,'d': 		s+"BUT7dUz"+t
			,'e': 		s+"mzNtW2U"+t
			,'f': 		s+"11cykaC"+t
			,'g': 		s+"l0CvvHo"+t
			,'h': 		s+"VOupMGK"+t
			,'i': 		s+"ps3YPHq"+t
			,'j': 		s+"oNHwZWv"+t
			,'k': 		s+"TwHANG6"+t
			,'l': 		s+"xiuR2WX"+t
			,'m': 		s+"GDEAPud"+t
			,'n': 		s+"9FjSiMu"+t
			,'o': 		s+"TcR1pa0"+t
			,'p': 		s+"OGc4VBR"+t
			,'q': 		s+"hL9tEkx"+t
			,'r': 		s+"37NNHm8"+t
			,'s': 		s+"mFQswUE"+t
			,'t': 		s+"4DBQVrd"+t
			,'u': 		s+"qpovLUW"+t
			,'v': 		s+"bnu5ByY"+t
			,'w': 		s+"0IHoHV2"+t
			,'x': 		s+"ic81iKY"+t
			,'y': 		s+"46IlmRH"+t
			,'z': 		s+"PWUSCsE"+t
			,'0': 		s+"7an2n4W"+t # 0RJOmkw
			,'all': 	s+"hrWVT21"+t
			,'search': 										s+"mDSHRJX"+t
			,'plugin settings': 					s+"K4OuZcD"+t
			,'local change log': 					s+"f1nvgAM"+t
			,'last': 											s+"FelUdDz"+t
			,'favorites': 								s+"lUAS5AU"+t
			,'favorites 2': 							s+"EA49Lt3"+t
			,'favorites 3': 							s+"lwJoUqT"+t
			,'favorites 4': 							s+"Wr7GPTf"+t
			,'latest update': 						s+"dNCxQbg"+t
			,'completed': 								s+"xcqaTKI"+t
			,'most popular': 							s+"T9LUsM2"+t
			,'new anime': 								s+"BGZnMf5"+t
			,'genre': 										s+"AmQHPvY"+t
			,'ongoing': 									s+"EUak0Sg"+t
			,'anime list all': 						s+"t8b1hSX"+t
			,'anime list alphabet': 			s+"R0w0BAM"+t
			,'anime list latest update': 	s+"XG0LGQH"+t
			,'anime list newest': 				s+"eWAeuLG"+t
			,'anime list popularity': 		s+"eTrguP1"+t
			,'urlresolver settings': 			s+"PlROfSs"+t
			,'online bookmarks': 					s+"68ih1sx"+t
			,'alphabetical': 							s+"sddCXQo"+t
			,'genre select': 							s+"MhNenb6"+t
			,'upcoming anime': 						s+"4v2dThp"+t
			,'site shortcuts': 						s+"w8aszrQ"+t
#			,'': 								s+""+t
#			,'': 								s+""+t
#			,'': 								s+""+t
# KissAnimeGenres
# http://imgur.com/a/rws19/all
# http://imgur.com/a/rws19#Q12cars
# http://imgur.com/a/rws19
		}[x]
	except: print 'failed to find graphc for %s' % (x); return ''


def psgs(x,t=".png"):
	s="http://i.imgur.com/"; 
	try:
		return {
			'action': 					s+""+t
			,'adventure': 			s+""+t
			,'dub': 						s+""+t
			,'cars': 						s+""+t
			,'cartoon': 				s+""+t
			,'comedy': 					s+""+t
			,'dementia': 				s+""+t
			,'demons': 					s+""+t
			,'drama': 					s+""+t
			,'ecchi': 					s+""+t
			,'fantasy': 				s+""+t
			,'game': 						s+""+t
			,'harem': 					s+""+t
			,'historical': 			s+""+t
			,'horror': 					s+""+t
			,'josei': 					s+""+t
			,'kids': 						s+""+t
			,'magic': 					s+""+t
			,'martial arts': 		s+""+t
			,'mecha': 					s+""+t
			,'military': 				s+""+t
			,'movie': 					s+""+t
			,'music': 					s+""+t
			,'mystery': 				s+""+t
			,'ona': 						s+""+t
			,'ova': 						s+""+t
			,'parody': 					s+""+t
			,'police': 					s+""+t
			,'psychological': 	s+""+t
			,'romance': 				s+""+t
			,'samurai': 				s+""+t
			,'school': 					s+""+t
			,'sci-fi': 					s+""+t
			,'seinen': 					s+""+t
			,'shoujo': 					s+""+t
			,'shoujo ai': 			s+""+t
			,'shounen': 				s+""+t
			,'shounen ai': 			s+""+t
			,'slice of life': 	s+""+t
			,'space': 					s+""+t
			,'special': 				s+""+t
			,'sports': 					s+""+t
			,'super power': 		s+""+t
			,'supernatural': 		s+""+t
			,'thriller': 				s+""+t
			,'vampire': 				s+""+t
			,'yuri': 						s+""+t
#			,'': 								s+""+t
		}[x]
	except: return ''


def psgsL(x,t=".png"):
	s="http://i.imgur.com/"; 
	try:
		return {
			'action': 					s+""+t
			,'adventure': 			s+""+t
			,'dub': 						s+""+t
			,'cars': 						s+""+t
			,'cartoon': 				s+""+t
			,'comedy': 					s+""+t
			,'dementia': 				s+""+t
			,'demons': 					s+""+t
			,'drama': 					s+""+t
			,'ecchi': 					s+""+t
			,'fantasy': 				s+""+t
			,'game': 						s+""+t
			,'harem': 					s+""+t
			,'historical': 			s+""+t
			,'horror': 					s+""+t
			,'josei': 					s+""+t
			,'kids': 						s+""+t
			,'magic': 					s+""+t
			,'martial arts': 		s+""+t
			,'mecha': 					s+""+t
			,'military': 				s+""+t
			,'movie': 					s+""+t
			,'music': 					s+""+t
			,'mystery': 				s+""+t
			,'ona': 						s+""+t
			,'ova': 						s+""+t
			,'parody': 					s+""+t
			,'police': 					s+""+t
			,'psychological': 	s+""+t
			,'romance': 				s+""+t
			,'samurai': 				s+""+t
			,'school': 					s+""+t
			,'sci-fi': 					s+""+t
			,'seinen': 					s+""+t
			,'shoujo': 					s+""+t
			,'shoujo ai': 			s+""+t
			,'shounen': 				s+""+t
			,'shounen ai': 			s+""+t
			,'slice of life': 	s+""+t
			,'space': 					s+""+t
			,'special': 				s+""+t
			,'sports': 					s+""+t
			,'super power': 		s+""+t
			,'supernatural': 		s+""+t
			,'thriller': 				s+""+t
			,'vampire': 				s+""+t
			,'yuri': 						s+""+t
#			,'': 								s+""+t
		}[x]
	except: return ''

### ############################################################################################################
### ############################################################################################################
### ############################################################################################################
### For Multiple Methods ###

### ############################################################################################################
### ############################################################################################################
### ############################################################################################################
### Other Settings ###
GENRES = ['Action','Adult','Adventure','Animation','Biography','Comedy','Crime','Documentary','Dub','Drama','Family','Fantasy','Film-Noir','Game-Show','History','Horror','Music','Musical','Mystery','News','Reality-TV','Romance','Sci-Fi','Short','Sport','Talk-Show','Thriller','War','Western']
COUNTRIES = ['Afghanistan','Albania','Algeria','Andorra','Angola','Argentina','Armenia','Aruba','Australia','Austria','Bahamas','Bahrain','Bangladesh','Barbados','Belarus','Belgium','Bermuda','Bolivia','Bosnia and Herzegovina','Botswana','Brazil','Bulgaria','Cambodia','Cameroon','Canada','Chad','Chile','China','Colombia','Costa Rica','Croatia','Cuba','Cyprus','Czech Republic','Czechoslovakia','Democratic Republic of the Congo','Denmark','Dominican Republic','East Germany','Ecuador','Egypt','El Salvador','Estonia','Ethiopia','Federal Republic of Yugoslavia','Finland','France','Georgia','Germany','Ghana','Greece','Guatemala','Haiti','Honduras','Hong Kong','Hungary','Iceland','India','Indonesia','Iran','Ireland','Isle of Man','Israel','Italy','Jamaica','Japan','Kazakhstan','Kenya','Kuwait','Latvia','Lebanon','Liberia','Libya','Liechtenstein','Lithuania','Luxembourg','Malaysia','Maldives','Malta','Mexico','Moldova','Monaco','Mongolia','Morocco','Namibia','Nepal','Netherlands','Netherlands Antilles','New Zealand','Nicaragua','Nigeria','North Korea','Norway','Occupied Palestinian Territory','Pakistan','Palestine','Panama','Papua New Guinea','Paraguay','Peru','Philippines','Poland','Portugal','Puerto Rico','Qatar','Republic of Macedonia','Romania','Russia','Rwanda','Senegal','Serbia','Serbia and Montenegro','Singapore','Slovakia','Slovenia','South Africa','South Korea','Soviet Union','Spain','Sri Lanka','Sweden','Switzerland','Taiwan','Tajikistan','Tanzania','Thailand','Togo','Trinidad and Tobago','Tunisia','Turkey','U.S. Virgin Islands','UK','Ukraine','United Arab Emirates','United States Minor Outlying Islands','Uruguay','USA','Venezuela','Vietnam','West Germany','Yugoslavia','Zaire','Zambia','Zimbabwe']

### ############################################################################################################
### ############################################################################################################
### ############################################################################################################
### Configurable Functions ###

### ############################################################################################################
