


from sickbeard.helpers import sanitizeSceneName
from sickbeard import name_cache
from sickbeard import logger
from sickbeard import db

_schema_created = False
def _check_for_schema():
    global _schema_created
    if not _schema_created:
        myDB = db.DBConnection()
        myDB.action('CREATE TABLE if not exists custom_exceptions (exception_id INTEGER PRIMARY KEY, tvdb_id INTEGER KEY, show_name TEXT)')
        _schema_created = True
 
# fast dynamic cache (held in memory only)       
_dyn_cache = {}

def get_custom_exceptions(tvdb_id):
    """
    Given a tvdb_id, return a list of all the custom scene exceptions.
    """
    if not tvdb_id:
        return []
    
    global _dyn_cache
    try: 
        return _dyn_cache[str(tvdb_id)]
    except KeyError:
        pass    # no cached value, just fall through to lookup
    
    _check_for_schema()
    myDB = db.DBConnection()
        
    exceptions = myDB.select("SELECT show_name FROM custom_exceptions WHERE tvdb_id = ?", [tvdb_id])
    result = [cur_exception["show_name"] for cur_exception in exceptions]
    _dyn_cache[str(tvdb_id)] = result # store for later
    return result

def get_custom_exception_by_name(show_name):
    """
    Given a show name, return the tvdbid of the exception, None if no exception
    is present.
    """

    myDB = db.DBConnection()
    _check_for_schema()
    
    # try the obvious case first
    exception_result = myDB.select("SELECT tvdb_id FROM custom_exceptions WHERE LOWER(show_name) = ?", [show_name.lower()])
    if exception_result:
        return int(exception_result[0]["tvdb_id"])

    all_exception_results = myDB.select("SELECT show_name, tvdb_id FROM custom_exceptions")
    for cur_exception in all_exception_results:

        cur_exception_name = cur_exception["show_name"]
        cur_tvdb_id = int(cur_exception["tvdb_id"])

        if show_name.lower() in (cur_exception_name.lower(), sanitizeSceneName(cur_exception_name).lower().replace('.',' ')):
            logger.log(u"Custom exception lookup got tvdb id "+str(cur_tvdb_id)+u", using that", logger.DEBUG)
            return cur_tvdb_id

    return None

def set_custom_exceptions(tvdb_id, show_names):
    """
    Set custom exception list for a show.
    'show_names' is a list of show names.
    """
    global _dyn_cache
    
    if not show_names:
        show_names = []
        
    myDB = db.DBConnection()
    _check_for_schema()

    changed_exceptions = False

    # get a list of the existing exceptions for this ID
    existing_exceptions = [x["show_name"] for x in myDB.select("SELECT * FROM custom_exceptions WHERE tvdb_id = ?", [tvdb_id])]
        
    for show_name in show_names:
        # if this exception isn't already in the DB then add it
        if show_name not in existing_exceptions:
            myDB.action("INSERT INTO custom_exceptions (tvdb_id, show_name) VALUES (?,?)", [tvdb_id, show_name])
            changed_exceptions = True
            
    # also need to delete anything we have in the db which is not now in show_names
    for show_name in existing_exceptions:
        if show_name not in show_names:
            myDB.action('DELETE FROM custom_exceptions where tvdb_id = ? and show_name = ?', [tvdb_id, show_name])
            changed_exceptions = True

    # since this could invalidate the results of the cache we clear it out after updating
    if changed_exceptions:
        name_cache.clearCache()
        
    # put the new list into the dynamic cache
    _dyn_cache[str(tvdb_id)] = show_names