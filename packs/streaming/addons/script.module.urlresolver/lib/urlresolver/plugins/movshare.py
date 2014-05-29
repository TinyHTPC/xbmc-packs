"""
    urlresolver XBMC Addon
    Copyright (C) 2011 t0mm0

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
"""

"""
RogerThis - 14/8/2011
Site: http://www.movshare.net
movshare hosts both avi and flv videos
"""

import re
from t0mm0.common.net import Net
import urllib2
from urlresolver.plugnplay.interfaces import UrlResolver
from urlresolver.plugnplay.interfaces import PluginSettings
from urlresolver.plugnplay import Plugin

class MovshareResolver(Plugin, UrlResolver, PluginSettings):
    implements = [UrlResolver, PluginSettings]
    name = "movshare"

    def __init__(self):
        p = self.get_setting('priority') or 100
        self.priority = int(p)
        self.net = Net()
        

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        """ Human Verification """
        try:
            self.net.http_HEAD(web_url)
            html = self.net.http_GET(web_url).content
        except urllib2.URLError, e:
            common.addon.log_error('movshare: got http error %d fetching %s' %
                                  (e.code, web_url))
            return False
               
        """movshare can do both flv and avi. There is no way I know before hand
        if the url going to be a flv or avi. So the first regex tries to find 
        the avi file, if nothing is present, it will check for the flv file.
        "param name="src" is for avi
        "flashvars.file=" is for flv
        """
        r = re.search('<param name="src" value="(.+?)"', html)
        if not r:
            r = re.search('flashvars.file="(.+?)"', html)
        if r:
            stream_url = r.group(1)
        else:
            common.addon.log_error('movshare: stream url not found')
            return False
                                    
        return stream_url
        

    def get_url(self, host, media_id):
        return 'http://www.movshare.net/video/%s' % media_id
        
        
    def get_host_and_id(self, url):
        r = re.search('//(.+?)/video/([0-9a-z]+)', url)
        if r:
            return r.groups()
        else:
            return False


    def valid_url(self, url, host):
        if self.get_setting('enabled') == 'false': return False
        return re.match('http://(?:www.)?movshare.net/video/',
                        url) or 'movshare' in host
