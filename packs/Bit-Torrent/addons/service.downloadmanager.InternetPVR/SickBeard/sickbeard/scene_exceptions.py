# Author: Nic Wolfe <nic@wolfeden.ca>
# URL: http://code.google.com/p/sickbeard/
#
# This file is part of Sick Beard.
#
# Sick Beard is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Sick Beard is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Sick Beard.  If not, see <http://www.gnu.org/licenses/>.

import re

from sickbeard import helpers
from sickbeard import name_cache
from sickbeard import logger
from sickbeard import db
from sickbeard.custom_exceptions import get_custom_exceptions, get_custom_exception_by_name 

# use the built-in if it's available (python 2.6), if not use the included library
try:
    import json
except ImportError:
    from lib import simplejson as json
    
# fast dynamic cache (held in memory only)       
_dyn_cache = {}

def get_scene_exceptions(tvdb_id, ignoreCustom=False):
    """
    Given a tvdb_id, return a list of all the scene exceptions.
    """
    global _dyn_cache
    
    if not tvdb_id:
        return []

    try: 
        scene_exceptions = _dyn_cache[str(tvdb_id)]
    except KeyError:
        myDB = db.DBConnection("cache.db")
        scene_exceptions = [x["show_name"] for x in myDB.select("SELECT show_name FROM scene_exceptions WHERE tvdb_id = ?", [tvdb_id])]
        _dyn_cache[str(tvdb_id)] = scene_exceptions

    if ignoreCustom:
        return scene_exceptions
    else:
        return list(set(scene_exceptions + get_custom_exceptions(tvdb_id)))


def get_scene_exception_by_name(show_name):
    """
    Given a show name, return the tvdbid of the exception, None if no exception
    is present.
    """

    myDB = db.DBConnection("cache.db")

    # try the obvious case first
    exception_result = myDB.select(u"SELECT tvdb_id FROM scene_exceptions WHERE LOWER(show_name) = ?", [show_name.lower()])
    if exception_result:
        return int(exception_result[0]["tvdb_id"])

    all_exception_results = myDB.select(u"SELECT show_name, tvdb_id FROM scene_exceptions")
    for cur_exception in all_exception_results:

        cur_exception_name = cur_exception["show_name"]
        cur_tvdb_id = int(cur_exception["tvdb_id"])

        if show_name.lower() in (cur_exception_name.lower(), helpers.sanitizeSceneName(cur_exception_name).lower().replace('.', ' ')):
            logger.log(u"Scene exception lookup got tvdb id "+str(cur_tvdb_id)+u", using that", logger.DEBUG)
            return cur_tvdb_id
        
    
    # if we get to here, try custom_exceptions instead
    return get_custom_exception_by_name(show_name)
    #return None


def retrieve_exceptions():
    """
    Looks up the exceptions on the show-api server, parses them into a dict, and inserts them into the
    scene_exceptions table in cache.db. Also clears the scene name cache.
    """
    global _dyn_cache
    
    exception_dict = {}

    # Moved the exceptions onto our show-api server (to allow for future source merging)
    url = 'http://show-api.tvtumbler.com/api/exceptions'

    logger.log(u"Check scene exceptions update")
    url_data = helpers.getURL(url)

    if url_data is None:
        logger.log(u"Check scene exceptions update failed. Unable to get URL: " + url, logger.ERROR)
        return
    else:
        exception_dict = json.loads(url_data)
        myDB = db.DBConnection("cache.db")
        changed_exceptions = False

        # write all the exceptions we got off the net into the database
        for cur_tvdb_id in exception_dict:
            
            # update our cache
            _dyn_cache[str(cur_tvdb_id)] = exception_dict[cur_tvdb_id]

            # get a list of the existing exceptions for this ID
            existing_exceptions = [x["show_name"] for x in myDB.select("SELECT * FROM scene_exceptions WHERE tvdb_id = ?", [cur_tvdb_id])]

            for cur_exception in exception_dict[cur_tvdb_id]:
                # if this exception isn't already in the DB then add it
                if cur_exception not in existing_exceptions:
                    logger.log(u'Adding exception %s: %s' % (cur_tvdb_id, cur_exception), logger.DEBUG)
                    myDB.action("INSERT INTO scene_exceptions (tvdb_id, show_name) VALUES (?,?)", [cur_tvdb_id, cur_exception])
                    changed_exceptions = True
                    
            # check for any exceptions which have been deleted
            for cur_exception in existing_exceptions:
                if cur_exception not in exception_dict[cur_tvdb_id]:
                    logger.log(u'Removing exception %s: %s' % (cur_tvdb_id, cur_exception), logger.DEBUG)
                    myDB.action("DELETE FROM scene_exceptions WHERE tvdb_id = ? AND show_name = ?", [cur_tvdb_id, cur_exception])
                    changed_exceptions = True

        # since this could invalidate the results of the cache we clear it out after updating
        if changed_exceptions:
            logger.log(u"Updated scene exceptions")
            name_cache.clearCache()
        else:
            logger.log(u"No scene exceptions update needed")
