# Credits: Daledude, WestCoast13
# Awesome efficient lightweight code.
# last modified 19 March 2011
# added support for TVDB search for show, seasons, episodes
# also searches imdb (using http://www.imdbapi.com/) for missing info in movies or tvshows

import simplejson
import urllib, re
from datetime import datetime
import time
from t0mm0.common.net import Net  
from t0mm0.common.addon import Addon       
net = Net()
addon = Addon('script.module.metahandler')

class TMDB(object):
    '''
    This class performs TMDB and IMDB lookups.
    
    First call is made to TMDB by either IMDB ID or Name/Year depending on what is supplied. If movie is not found
    or if there is data missing on TMDB, another call is made to IMDB to fill in the missing information.       
    '''  
    
    def __init__(self, api_key='b91e899ce561dd19695340c3b26e0a02', view='json', lang='en'):
        #view = yaml json xml
        self.view = view
        self.lang = lang
        self.api_key = api_key
        self.url_prefix = 'http://api.themoviedb.org/2.1'
        self.imdb_api = 'http://www.imdbapi.com/?i=%s'
        self.imdb_name_api = 'http://www.imdbapi.com/?t=%s'
        self.imdb_nameyear_api = 'http://www.imdbapi.com/?t=%s&y=%s' 


    def __clean_name(self, mystring):
        newstring = ''
        for word in mystring.split(' '):
            if word.isalnum()==False:
                w = ""          
                for i in range(len(word)):
                    if(word[i].isalnum()):              
                        w+=word[i]
                word = w
            newstring += ' ' + word
        return newstring.strip()


    def _do_request(self, method, values):
        '''
        Request JSON data from TMDB
        
        Args:
            method (str): Type of TMDB request to make
            values (str): Value to use in TMDB lookup request
                        
        Returns:
            DICT of meta data found on TMDB
            Returns None when not found or error requesting page
        '''      
        url = "%s/%s/%s/%s/%s/%s" % (self.url_prefix, method, self.lang, self.view, self.api_key, values)
        addon.log('Requesting TMDB : %s' % url, 0)
        try:
            meta = simplejson.loads(net.http_GET(url).content)[0]
        except Exception, e:
            addon.log("Error connecting to TMDB: %s " % e, 4)
            return None

        if meta == 'Nothing found.':
            return None
        else:
            addon.log('TMDB Meta: %s' % meta, 0)
            return meta


    def _do_request_all(self, method, values):
        '''
        Request JSON data from TMDB, returns all matches found
        
        Args:
            method (str): Type of TMDB request to make
            values (str): Value to use in TMDB lookup request
                        
        Returns:
            DICT of meta data found on TMDB
            Returns None when not found or error requesting page
        '''      
        url = "%s/%s/%s/%s/%s/%s" % (self.url_prefix, method, self.lang, self.view, self.api_key, values)
        addon.log('Requesting TMDB : %s' % url, 0)
        try:
            meta = simplejson.loads(net.http_GET(url).content)
        except Exception, e:
            addon.log("Error connecting to TMDB: %s " % e, 4)
            return None

        if meta == 'Nothing found.':
            return None
        else:
            addon.log('TMDB Meta: %s' % meta, 0)
            return meta


    def _convert_date(self, string, in_format, out_format):
        ''' Helper method to convert a string date to a given format '''
        
        #Legacy check, Python 2.4 does not have strptime attribute, instroduced in 2.5
        if hasattr(datetime, 'strptime'):
            strptime = datetime.strptime
        else:
            strptime = lambda date_string, format: datetime(*(time.strptime(date_string, format)[0:6]))
        
        #strptime = lambda date_string, format: datetime(*(time.strptime(date_string, format)[0:6]))
        try:
            a = strptime(string, in_format).strftime(out_format)
        except Exception, e:
            addon.log('************* Error Date conversion failed: %s' % e, 4)
            return None
        return a
        
        
    def _upd_key(self, meta, key):
        ''' Helper method to check if a key exists and if it has valid data, returns True if key needs to be udpated with valid data '''    
        if meta.has_key(key) == False :
            return True 
        else:
            try:
                bad_list = ['', '0.0', '0', 0, 'None', '[]', 'No overview found.', 'TBD', 'N/A', None]
                if meta[key] in bad_list:
                    return True
                else:
                    return False
            except:
                return True


    def search_imdb(self, name, imdb_id='', year=''):
        '''
        Search IMDB by either IMDB ID or Name/Year      
        
        Args:
            name (str): full name of movie you are searching            
        Kwargs:
            imdb_id (str): IMDB ID
            year (str): 4 digit year of video, recommended to include the year whenever possible
                        to maximize correct search results.
                        
        Returns:
            DICT of meta data or None if cannot be found.
        '''        
        #Set IMDB API URL based on the type of search we need to do
        if imdb_id:
            url = self.imdb_api % imdb_id
        else:
            name = urllib.quote(name)
            if year:
                url = self.imdb_nameyear_api % (name, year)
            else:
                url = self.imdb_name_api % name

        try:
            addon.log('Requesting IMDB : %s' % url, 0)
            meta = simplejson.loads(net.http_GET(url).content)
            addon.log('IMDB Meta: %s' % meta, 0)
        except Exception, e:
            addon.log("Error connecting to IMDB: %s " % e, 4)
            return {}

        if meta['Response'] == 'True':
            return meta
        else:
            return {}
        

    def update_imdb_meta(self, meta, imdb_meta):
        '''
        Update dict TMDB meta with data found on IMDB where appropriate
        
        Args:
            meta (dict): typically a container of meta data found on TMDB
            imdb_meta (dict): container of meta data found on IMDB
                       
        Returns:
            DICT of updated meta data container
        '''        
        addon.log('Updating current meta with IMDB', 0)
        
        if self._upd_key(meta, 'overview') and self._upd_key(meta, 'plot'):
            addon.log('-- IMDB - Updating Overview', 0)
            if imdb_meta.has_key('Plot'):
                meta['overview']=imdb_meta['Plot']           
        
        if self._upd_key(meta, 'released') and self._upd_key(meta, 'premiered'):
            addon.log('-- IMDB - Updating Premiered', 0)
            
            temp=self._convert_date(imdb_meta['Released'], '%d %b %Y', '%Y-%m-%d')
            #May have failed, lets try a different format
            if not temp:
                temp=self._convert_date(imdb_meta['Released'], '%b %Y', '%Y-%m-%d')
            
            if temp:
                meta['released'] = temp
            else:
                if imdb_meta['Year'] != 'N/A':
                    meta['released'] = imdb_meta['Year'] + '-01-01'
        
        if self._upd_key(meta, 'posters'):
            addon.log('-- IMDB - Updating Posters', 0)
            temp=imdb_meta['Poster']
            if temp != 'N/A':
                meta['cover_url']=temp
        
        if self._upd_key(meta, 'rating'):
            addon.log('-- IMDB - Updating Rating', 0)
            imdb_rating = imdb_meta['imdbRating']
            if imdb_rating not in ('N/A', '', None):
                meta['rating'] = imdb_rating
            else:
                if meta.has_key('tmdb_rating'):
                    meta['rating'] = meta['tmdb_rating']

        if self._upd_key(meta, 'certification'):
            if imdb_meta['Rated']:
                addon.log('-- IMDB - Updating MPAA', 0)
                meta['certification'] = imdb_meta['Rated']

        if self._upd_key(meta, 'director'):
            if imdb_meta['Director']:
                addon.log('-- IMDB - Updating Director', 0)
                meta['director'] = imdb_meta['Director']

        if self._upd_key(meta, 'writer'):
            if imdb_meta['Writer']:
                addon.log('-- IMDB - Updating Writer', 0)
                meta['writer'] = imdb_meta['Writer']

        if not self._upd_key(imdb_meta, 'imdbVotes'):
            meta['votes'] = imdb_meta['imdbVotes']
        else:
            meta['votes'] = ''
                
        if self._upd_key(meta, 'genre'):
            addon.log('-- IMDB - Updating Genre', 0)
            temp=imdb_meta['Genre']
            if temp != 'N/A':
                meta['genre']=temp
                
        if self._upd_key(meta, 'runtime') and self._upd_key(meta, 'duration'):
            addon.log('-- IMDB - Updating Runtime', 0)
            temp=imdb_meta['Runtime']
            if temp != 'N/A':
                dur=0
                scrape=re.compile('([0-9]+) h ([0-9]+) min').findall(temp)
                if len(scrape) > 0:
                    dur = (int(scrape[0][0]) * 60) + int(scrape[0][1])
                scrape=re.compile('([0-9]+) hr').findall(temp)
                if len(scrape) > 0:
                    dur = int(scrape[0]) * 60
                scrape=re.compile(' ([0-9]+) ([0-9]+) min').findall(temp)
                if len(scrape) > 0:
                    dur = dur + int(scrape[0][1])
                else: # No hrs in duration
                    scrape=re.compile('([0-9]+) min').findall(temp)
                    if len(scrape) > 0:
                        dur = dur + int(scrape[0])
                meta['runtime']=str(dur)
        
        meta['imdb_id'] = imdb_meta['imdbID']       
        return meta


    # video_id is either tmdb or imdb id
    def _get_version(self, video_id):
        ''' Helper method to start a TMDB getVersion request '''    
        return self._do_request('Movie.getVersion', video_id)


    def _get_info(self, tmdb_id):
        ''' Helper method to start a TMDB getInfo request '''            
        return self._do_request('Movie.getInfo', tmdb_id)
        

    def _search_movie(self, name, year=''):
        ''' Helper method to start a TMDB Movie.search request - search by Name/Year '''
        name = urllib.quote(self.__clean_name(name))
        if year:
            name = name + '+' + year
        return self._do_request('Movie.search',name)
        

    def tmdb_search(self, name):
        '''
        Used primarily to update a single movie meta data by providing a list of possible matches
        
        Returns a tuple of matches containing movie name and imdb id
        
        Args:
            name (str): full name of movie you are searching            
                        
        Returns:
            DICT of matches
        '''
        return self._do_request_all('Movie.search',urllib.quote(name))
        
        
    def tmdb_lookup(self, name, imdb_id='', tmdb_id='', year=''):
        '''
        Main callable method which initiates the TMDB/IMDB meta data lookup
        
        Returns a final dict of meta data    
        
        Args:
            name (str): full name of movie you are searching            
        Kwargs:
            imdb_id (str): IMDB ID
            tmdb_id (str): TMDB ID
            year (str): 4 digit year of video, recommended to include the year whenever possible
                        to maximize correct search results.
                        
        Returns:
            DICT of meta data
        ''' 
        meta = {}
        
        #If we don't have an IMDB ID or TMDB ID let's try searching TMDB first by movie name
        if not imdb_id and not tmdb_id:
            meta = self._search_movie(name,year)              
            if meta:
                tmdb_id = meta['id']
                imdb_id = meta['imdb_id']
            
            #Didn't get a match by name at TMDB, let's try IMDB by name
            else:
                meta = self.search_imdb(name, year=year)
                if meta:
                    imdb_id = meta['imdbID']                         

        #If we don't have a tmdb_id yet but do have imdb_id lets see if we can find it
        elif imdb_id and not tmdb_id:
            addon.log('IMDB ID found, attempting to get TMDB ID', 0)
            meta = self._get_version(imdb_id)
            if meta:
                tmdb_id = meta['id']

        if tmdb_id:
            meta = self._get_info(tmdb_id)

            if meta is None: # fall through to IMDB lookup
                meta = {}
            else:               
                
                #Set rating to 0 so that we can force it to be grabbed from IMDB
                meta['tmdb_rating'] = meta['rating']
                meta['rating'] = 0
                
                #Update any missing information from IDMB
                #if meta['overview'] == 'None' or meta['overview'] == '' or meta['overview'] == 'TBD' or meta['overview'] == 'No overview found.' or meta['rating'] == 0 or meta['runtime'] == 0 or meta['runtime'] == None or str(meta['genres']) == '[]' or str(meta['posters']) == '[]' or meta['released'] == None or meta['certification'] == None:
                #addon.log('Some info missing in TMDB for Movie *** %s ***. Will search imdb for more' % imdb_id, 0)
                addon.log('Requesting IMDB for extra information: %s' % imdb_id, 0)
                imdb_meta = self.search_imdb(name, imdb_id)
                if imdb_meta:
                    meta = self.update_imdb_meta(meta, imdb_meta)
        
        #If all else fails, and we don't have a TMDB id
        else:
            imdb_meta = self.search_imdb(name, imdb_id, year)
            if imdb_meta:
                meta = self.update_imdb_meta({}, imdb_meta)
       
        return meta
