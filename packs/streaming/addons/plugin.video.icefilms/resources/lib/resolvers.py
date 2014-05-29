import xbmc,xbmcgui
import os
import urllib, urllib2
import cookielib
import re
import jsunpack

''' Use addon.common library for http calls '''
from addon.common.net import Net
from addon.common.addon import Addon
net = Net()

addon = Addon('plugin.video.icefilms')
datapath = addon.get_profile()

cookie_path = os.path.join(datapath, 'cookies')

USER_AGENT = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1500.72 Safari/537.36'
ACCEPT = 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'

def handle_captchas(html, data, dialog):

    puzzle_img = os.path.join(datapath, "solve_puzzle.png")
    
    #Check for type of captcha used
    solvemedia = re.search('<iframe src="(http://api.solvemedia.com.+?)"', html)
    recaptcha = re.search('<script type="text/javascript" src="(http://www.google.com.+?)">', html)
    numeric_captcha = re.compile("left:(\d+)px;padding-top:\d+px;'>&#(.+?);<").findall(html)    

    #SolveMedia captcha
    if solvemedia:
       dialog.close()
       html = net.http_GET(solvemedia.group(1)).content
       hugekey=re.search('id="adcopy_challenge" value="(.+?)">', html).group(1)
       
       #Check for alternate puzzle type - stored in a div
       alt_puzzle = re.search('<div><iframe src="(/papi/media.+?)"', html)
       if alt_puzzle:
           open(puzzle_img, 'wb').write(net.http_GET("http://api.solvemedia.com%s" % alt_puzzle.group(1)).content)
       else:
           open(puzzle_img, 'wb').write(net.http_GET("http://api.solvemedia.com%s" % re.search('<img src="(/papi/media.+?)"', html).group(1)).content)
       
       img = xbmcgui.ControlImage(450,15,400,130, puzzle_img)
       wdlg = xbmcgui.WindowDialog()
       wdlg.addControl(img)
       wdlg.show()
    
       xbmc.sleep(3000)

       kb = xbmc.Keyboard('', 'Type the letters in the image', False)
       kb.doModal()
       capcode = kb.getText()

       if (kb.isConfirmed()):
           userInput = kb.getText()
           if userInput != '':
               solution = kb.getText()
           elif userInput == '':
               raise Exception ('You must enter text in the image to access video')
       else:
           raise Exception ('Captcha Error')
       wdlg.close()
       data.update({'adcopy_challenge': hugekey,'adcopy_response': solution})

    #Google Recaptcha
    elif recaptcha:
        dialog.close()
        html = net.http_GET(recaptcha.group(1)).content
        part = re.search("challenge \: \\'(.+?)\\'", html)
        captchaimg = 'http://www.google.com/recaptcha/api/image?c='+part.group(1)
        img = xbmcgui.ControlImage(450,15,400,130,captchaimg)
        wdlg = xbmcgui.WindowDialog()
        wdlg.addControl(img)
        wdlg.show()

        xbmc.sleep(3000)

        kb = xbmc.Keyboard('', 'Type the letters in the image', False)
        kb.doModal()
        capcode = kb.getText()

        if (kb.isConfirmed()):
            userInput = kb.getText()
            if userInput != '':
                solution = kb.getText()
            elif userInput == '':
                raise Exception ('You must enter text in the image to access video')
        else:
            raise Exception ('Captcha Error')
        wdlg.close()
        data.update({'recaptcha_challenge_field':part.group(1),'recaptcha_response_field':solution})               

    #Numeric captcha - we can programmatically figure this out
    elif numeric_captcha:
        captcha = re.compile("left:(\d+)px;padding-top:\d+px;'>&#(.+?);<").findall(html)
        result = sorted(captcha, key=lambda ltr: int(ltr[0]))
        solution = ''.join(str(int(num[1])-48) for num in result)
        data.update({'code':solution})  
        
    return data


def resolve_180upload(url):

    try:
        dialog = xbmcgui.DialogProgress()
        dialog.create('Resolving', 'Resolving 180Upload Link...')
        dialog.update(0)
       
        addon.log_debug( '180Upload - Requesting GET URL: %s' % url)
        html = net.http_GET(url).content

        dialog.update(50)

        wrong_captcha = True
        
        while wrong_captcha:
        
            data = {}
            r = re.findall(r'type="hidden" name="(.+?)" value="(.+?)">', html)

            if r:
                for name, value in r:
                    data[name] = value
            else:
                raise Exception('Unable to resolve 180Upload Link')

            #Handle captcha
            data = handle_captchas(html, data, dialog)

            dialog.create('Resolving', 'Resolving 180Uploads Link...') 
            dialog.update(50)  
            
            addon.log_debug( '180Upload - Requesting POST URL: %s Data: %s' % (url, data))
            html = net.http_POST(url, data).content

            wrong_captcha = re.search('<div class="err">Wrong captcha</div>', html)
            if wrong_captcha:
                addon.show_ok_dialog(['Wrong captcha entered, try again'], title='Wrong Captcha', is_error=False)

        dialog.update(100)
        
        link = re.search('id="lnk_download" href="([^"]+)', html)
        if link:
            addon.log_debug( '180Upload Link Found: %s' % link.group(1))
            return link.group(1)
        else:
            raise Exception('Unable to resolve 180Upload Link')

    except Exception, e:
        addon.log_error('**** 180Upload Error occured: %s' % e)
        raise
    finally:
        dialog.close()


def resolve_megafiles(url):

    try:
        dialog = xbmcgui.DialogProgress()
        dialog.create('Resolving', 'Resolving MegaFiles Link...')
        dialog.update(0)
        
        addon.log_debug('MegaFiles - Requesting GET URL: %s' % url)
        html = net.http_GET(url).content

        dialog.update(50)

        wrong_captcha = True
        
        while wrong_captcha:
        
            data = {}
            r = re.findall(r'type="hidden" name="(.+?)" value="(.+?)">', html)

            if r:
                for name, value in r:
                    data[name] = value
            else:
                raise Exception('Unable to resolve MegaFiles Link')

            #Handle captcha
            data = handle_captchas(html, data, dialog)

            dialog.create('Resolving', 'Resolving MegaFiles Link...') 
            dialog.update(50)                  

            addon.log_debug('MegaFiles - Requesting POST URL: %s' % url)
            html = net.http_POST(url, data).content

            wrong_captcha = re.search('<div class="err">Wrong captcha</div>', html)
            if wrong_captcha:
                addon.show_ok_dialog(['Wrong captcha entered, try again'], title='Wrong Captcha', is_error=False)
            
        dialog.update(100)
        
        link = re.search("var download_url = '(.+?)';", html)
        if link:
            addon.log_debug('MegaFiles Link Found: %s' % link.group(1))
            return link.group(1)
        else:
            raise Exception('Unable to resolve MegaFiles Link')

    except Exception, e:
        addon.log_error('**** MegaFiles Error occured: %s' % e)
        raise
    finally:
        dialog.close()
        
        
def resolve_vidhog(url):

    try:
        
        #Show dialog box so user knows something is happening
        dialog = xbmcgui.DialogProgress()
        dialog.create('Resolving', 'Resolving VidHog Link...')
        dialog.update(0)
        
        addon.log_debug('VidHog - Requesting GET URL: %s' % url)
        html = net.http_GET(url).content

        dialog.update(50)
        
        #Check page for any error msgs
        if re.search('This server is in maintenance mode', html):
            raise Exception('File is currently unavailable on the host')
        if re.search('<b>File Not Found</b>', html):
            raise Exception('File has been deleted')

        filename = re.search('<strong>\(<font color="red">(.+?)</font>\)</strong><br><br>', html).group(1)
        extension = re.search('(\.[^\.]*$)', filename).group(1)
        guid = re.search('http://vidhog.com/(.+)$', url).group(1)
        
        vid_embed_url = 'http://vidhog.com/vidembed-%s%s' % (guid, extension)
        
        request = urllib2.Request(vid_embed_url)
        request.add_header('User-Agent', USER_AGENT)
        request.add_header('Accept', ACCEPT)
        request.add_header('Referer', url)
        response = urllib2.urlopen(request)
        redirect_url = re.search('(http://.+?)video', response.geturl()).group(1)
        download_link = redirect_url + filename
        
        dialog.update(100)

        return download_link
        
    except Exception, e:
        addon.log_error('**** VidHog Error occured: %s' % e)
        raise
    finally:
        dialog.close()

        
def resolve_vidplay(url):

    try:
        
        #Show dialog box so user knows something is happening
        dialog = xbmcgui.DialogProgress()
        dialog.create('Resolving', 'Resolving VidPlay Link...')
        dialog.update(0)
        
        addon.log_debug('VidPlay - Requesting GET URL: %s' % url)
        html = net.http_GET(url).content

        dialog.update(50)
        
        #Check page for any error msgs
        if re.search('This server is in maintenance mode', html):
            raise Exception('File is currently unavailable on the host')
        if re.search('<b>File Not Found</b>', html):
            raise Exception('File has been deleted')

        filename = re.search('<h4>(.+?)</h4>', html).group(1)
        extension = re.search('(\.[^\.]*$)', filename).group(1)
        guid = re.search('http://vidplay.net/(.+)$', url).group(1)
        
        vid_embed_url = 'http://vidplay.net/vidembed-%s%s' % (guid, extension)
        
        request = urllib2.Request(vid_embed_url)
        request.add_header('User-Agent', USER_AGENT)
        request.add_header('Accept', ACCEPT)
        request.add_header('Referer', url)
        response = urllib2.urlopen(request)
        redirect_url = re.search('(http://.+?)video', response.geturl()).group(1)
        download_link = redirect_url + filename
        
        dialog.update(100)

        return download_link
        
    except Exception, e:
        addon.log_error('**** VidPlay Error occured: %s' % e)
        raise
    finally:
        dialog.close()
        

def resolve_sharebees(url):

    try:
        
        if addon.get_setting('sharebees-account') == 'true':
            addon.log_debug('ShareBees - Setting Cookie file')
            cookiejar = os.path.join(cookie_path,'sharebees.lwp')
            net.set_cookies(cookiejar)
        
        #Show dialog box so user knows something is happening
        dialog = xbmcgui.DialogProgress()
        dialog.create('Resolving', 'Resolving ShareBees Link...')       
        dialog.update(0)
        
        addon.log_debug('ShareBees - Requesting GET URL: %s' % url)
        html = net.http_GET(url).content
        
        dialog.update(50)
        
        #Set POST data values
        #op = re.search('''<input type="hidden" name="op" value="(.+?)">''', html, re.DOTALL).group(1)
        op = 'download1'
        usr_login = re.search('<input type="hidden" name="usr_login" value="(.*?)">', html).group(1)
        postid = re.search('<input type="hidden" name="id" value="(.+?)">', html).group(1)
        fname = re.search('<input type="hidden" name="fname" value="(.+?)">', html).group(1)
        method_free = "method_free"
        
        data = {'op': op, 'usr_login': usr_login, 'id': postid, 'fname': fname, 'referer': url, 'method_free': method_free}
        
        addon.log_debug('ShareBees - Requesting POST URL: %s DATA: %s' % (url, data))
        html = net.http_POST(url, data).content
        
        dialog.update(100)

        link = None
        sPattern = '''<div id="player_code">.*?<script type='text/javascript'>(eval.+?)</script>'''
        r = re.search(sPattern, html, re.DOTALL + re.IGNORECASE)
        
        if r:
            sJavascript = r.group(1)
            sUnpacked = jsunpack.unpack(sJavascript)
            
            #Grab first portion of video link, excluding ending 'video.xxx' in order to swap with real file name
            #Note - you don't actually need the filename, but for purpose of downloading via Icefilms it's needed so download video has a name
            sPattern  = '''("video/divx"src="|addVariable\('file',')(.+?)video[.]'''
            r = re.search(sPattern, sUnpacked)              
            
            #Video link found
            if r:
                link = r.group(2) + fname
                return link

        if not link:
            addon.log_debug('***** ShareBees - Link Not Found')
            raise Exception("Unable to resolve ShareBees")

    except Exception, e:
        addon.log_error('**** ShareBees Error occured: %s' % e)
        raise
    finally:
        dialog.close()


def resolve_movreel(url):

    try:

        if addon.get_setting('movreel-account') == 'true':
            addon.log('MovReel - Setting Cookie file')
            cookiejar = os.path.join(cookie_path,'movreel.lwp')
            net.set_cookies(cookiejar)

        #Show dialog box so user knows something is happening
        dialog = xbmcgui.DialogProgress()
        dialog.create('Resolving', 'Resolving Movreel Link...')       
        dialog.update(0)
        
        addon.log('Movreel - Requesting GET URL: %s' % url)
        html = net.http_GET(url).content
        
        dialog.update(33)
        
        #Check page for any error msgs
        if re.search('This server is in maintenance mode', html):
            addon.log_error('***** Movreel - Site reported maintenance mode')
            raise Exception('File is currently unavailable on the host')

        #Set POST data values
        op = re.search('<input type="hidden" name="op" value="(.+?)">', html).group(1)
        postid = re.search('<input type="hidden" name="id" value="(.+?)">', html).group(1)
        method_free = re.search('<input type="(submit|hidden)" name="method_free" (style=".*?" )*value="(.*?)">', html).group(3)
        method_premium = re.search('<input type="(hidden|submit)" name="method_premium" (style=".*?" )*value="(.*?)">', html).group(3)
        
        if method_free:
            usr_login = ''
            fname = re.search('<input type="hidden" name="fname" value="(.+?)">', html).group(1)
            data = {'op': op, 'usr_login': usr_login, 'id': postid, 'referer': url, 'fname': fname, 'method_free': method_free}
        else:
            rand = re.search('<input type="hidden" name="rand" value="(.+?)">', html).group(1)
            data = {'op': op, 'id': postid, 'referer': url, 'rand': rand, 'method_premium': method_premium}
        
        addon.log('Movreel - Requesting POST URL: %s DATA: %s' % (url, data))
        html = net.http_POST(url, data).content

        #Only do next post if Free account, skip to last page for download link if Premium
        if method_free:
            #Check for download limit error msg
            if re.search('<p class="err">.+?</p>', html):
                addon.log_error('***** Download limit reached')
                errortxt = re.search('<p class="err">(.+?)</p>', html).group(1)
                raise Exception(errortxt)
    
            dialog.update(66)
            
            #Set POST data values
            data = {}
            r = re.findall(r'type="hidden" name="(.+?)" value="(.+?)">', html)
    
            if r:
                for name, value in r:
                    data[name] = value
            else:
                addon.log_error('***** Movreel - Cannot find data values')
                raise Exception('Unable to resolve Movreel Link')

            addon.log('Movreel - Requesting POST URL: %s DATA: %s' % (url, data))
            html = net.http_POST(url, data).content

        #Get download link
        dialog.update(100)
        link = re.search('<a href="(.+)">Download Link</a>', html)
        if link:
            return link.group(1)
        else:
        	  raise Exception("Unable to find final link")

    except Exception, e:
        addon.log_error('**** Movreel Error occured: %s' % e)
        raise
    finally:
        dialog.close()


def resolve_billionuploads(url):

    try:

        #Show dialog box so user knows something is happening
        dialog = xbmcgui.DialogProgress()
        dialog.create('Resolving', 'Resolving BillionUploads Link...')       
        dialog.update(0)
        
        addon.log('BillionUploads - Requesting GET URL: %s' % url)
        cookie_file = os.path.join(cookie_path,'billionuploads.lwp')
        
        cj = cookielib.LWPCookieJar()
        if os.path.exists(cookie_file):
            try: cj.load(cookie_file,True)
            except: cj.save(cookie_file,True)
        else: cj.save(cookie_file,True)
        
        normal = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
        headers = [
            ('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:25.0) Gecko/20100101 Firefox/25.0'),
            ('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'),
            ('Accept-Language', 'en-US,en;q=0.5'),
            ('Accept-Encoding', ''),
            ('DNT', '1'),
            ('Connection', 'keep-alive'),
            ('Pragma', 'no-cache'),
            ('Cache-Control', 'no-cache')
        ]
        normal.addheaders = headers
        class NoRedirection(urllib2.HTTPErrorProcessor):
            # Stop Urllib2 from bypassing the 503 page.
            def http_response(self, request, response):
                code, msg, hdrs = response.code, response.msg, response.info()
                return response
            https_response = http_response
        opener = urllib2.build_opener(NoRedirection, urllib2.HTTPCookieProcessor(cj))
        opener.addheaders = normal.addheaders
        response = opener.open(url).read()
        decoded = re.search('(?i)var z="";var b="([^"]+?)"', response)
        if decoded:
            decoded = decoded.group(1)
            z = []
            for i in range(len(decoded)/2):
                z.append(int(decoded[i*2:i*2+2],16))
            decoded = ''.join(map(unichr, z))
            incapurl = re.search('(?i)"GET","(/_Incapsula_Resource[^"]+?)"', decoded)
            if incapurl:
                incapurl = 'http://billionuploads.com'+incapurl.group(1)
                opener.open(incapurl)
                cj.save(cookie_file,True)
                response = opener.open(url).read()
                
        captcha = re.search('(?i)<iframe src="(/_Incapsula_Resource[^"]+?)"', response)
        if captcha:
            captcha = 'http://billionuploads.com'+captcha.group(1)
            opener.addheaders.append(('Referer', url))
            response = opener.open(captcha).read()
            formurl = 'http://billionuploads.com'+re.search('(?i)<form action="(/_Incapsula_Resource[^"]+?)"', response).group(1)
            resource = re.search('(?i)src=" (/_Incapsula_Resource[^"]+?)"', response)
            if resource:
                import random
                resourceurl = 'http://billionuploads.com'+resource.group(1) + str(random.random())
                opener.open(resourceurl)
            recaptcha = re.search('(?i)<script type="text/javascript" src="(https://www.google.com/recaptcha/api[^"]+?)"', response)
            if recaptcha:
                response = opener.open(recaptcha.group(1)).read()
                challenge = re.search('''(?i)challenge : '([^']+?)',''', response)
                if challenge:
                    challenge = challenge.group(1)
                    captchaimg = 'https://www.google.com/recaptcha/api/image?c=' + challenge
                    img = xbmcgui.ControlImage(450,15,400,130,captchaimg)
                    wdlg = xbmcgui.WindowDialog()
                    wdlg.addControl(img)
                    wdlg.show()
                    
                    xbmc.sleep(3000)
                    
                    kb = xbmc.Keyboard('', 'Please enter the text in the image', False)
                    kb.doModal()
                    capcode = kb.getText()
                    if (kb.isConfirmed()):
                        userInput = kb.getText()
                        if userInput != '': capcode = kb.getText()
                        elif userInput == '':
                            logerror('BillionUploads - Image-Text not entered')
                            xbmc.executebuiltin("XBMC.Notification(Image-Text not entered.,BillionUploads,2000)")              
                            return None
                    else: return None
                    wdlg.close()
                    captchadata = {}
                    captchadata['recaptcha_challenge_field'] = challenge
                    captchadata['recaptcha_response_field'] = capcode
                    opener.addheaders = headers
                    opener.addheaders.append(('Referer', captcha))
                    resultcaptcha = opener.open(formurl,urllib.urlencode(captchadata)).info()
                    opener.addheaders = headers
                    response = opener.open(url).read()
                    
        ga = re.search('(?i)"text/javascript" src="(/ga[^"]+?)"', response)
        if ga:
            jsurl = 'http://billionuploads.com'+ga.group(1)
            p  = "p=%7B%22appName%22%3A%22Netscape%22%2C%22platform%22%3A%22Win32%22%2C%22cookies%22%3A1%2C%22syslang%22%3A%22en-US%22"
            p += "%2C%22userlang%22%3A%22en-US%22%2C%22cpu%22%3A%22WindowsNT6.1%3BWOW64%22%2C%22productSub%22%3A%2220100101%22%7D"
            opener.open(jsurl, p)
            response = opener.open(url).read()
#         pid = re.search('(?i)PID=([^"]+?)"', response)
#         if pid:
#             normal.addheaders += [('Cookie','D_UID='+pid.group(1)+';')]
#             opener.addheaders = normal.addheaders
        if re.search('(?i)url=/distil_r_drop.html', response) and filename:
            url += '/' + filename
            response = normal.open(url).read()
        jschl=re.compile('name="jschl_vc" value="(.+?)"/>').findall(response)
        if jschl:
            jschl = jschl[0]    
            maths=re.compile('value = (.+?);').findall(response)[0].replace('(','').replace(')','')
            domain_url = re.compile('(https?://.+?/)').findall(url)[0]
            domain = re.compile('https?://(.+?)/').findall(domain_url)[0]
            final= normal.open(domain_url+'cdn-cgi/l/chk_jschl?jschl_vc=%s&jschl_answer=%s'%(jschl,eval(maths)+len(domain))).read()
            html = normal.open(url).read()
        else: html = response
        
        if dialog.iscanceled(): return None
        dialog.update(25)
        
        #Check page for any error msgs
        if re.search('This server is in maintenance mode', html):
            addon.log_error('***** BillionUploads - Site reported maintenance mode')
            raise Exception('File is currently unavailable on the host')

        # Check for file not found
        if re.search('File Not Found', html):
            addon.log_error('***** BillionUploads - File Not Found')
            raise Exception('File Not Found - Likely Deleted')  

        data = {}
        r = re.findall(r'type="hidden" name="(.+?)" value="(.*?)">', html)
        for name, value in r: data[name] = value
        
        if dialog.iscanceled(): return None
        
        captchaimg = re.search('<img src="((?:http://|www\.)?BillionUploads.com/captchas/.+?)"', html)            
        if captchaimg:

            img = xbmcgui.ControlImage(550,15,240,100,captchaimg.group(1))
            wdlg = xbmcgui.WindowDialog()
            wdlg.addControl(img)
            wdlg.show()
            
            kb = xbmc.Keyboard('', 'Please enter the text in the image', False)
            kb.doModal()
            capcode = kb.getText()
            if (kb.isConfirmed()):
                userInput = kb.getText()
                if userInput != '': capcode = kb.getText()
                elif userInput == '':
                    showpopup('BillionUploads','[B]You must enter the text from the image to access video[/B]',5000, elogo)
                    return None
            else: return None
            wdlg.close()
            
            data.update({'code':capcode})
        
        if dialog.iscanceled(): return None
        dialog.update(50)
        
        data.update({'submit_btn':''})
        enc_input = re.compile('decodeURIComponent\("(.+?)"\)').findall(html)
        if enc_input:
            dec_input = urllib2.unquote(enc_input[0])
            r = re.findall(r'type="hidden" name="(.+?)" value="(.*?)">', dec_input)
            for name, value in r:
                data[name] = value
        extradata = re.compile("append\(\$\(document.createElement\('input'\)\).attr\('type','hidden'\).attr\('name','(.*?)'\).val\((.*?)\)").findall(html)
        if extradata:
            for attr, val in extradata:
                if 'source="self"' in val:
                    val = re.compile('<textarea[^>]*?source="self"[^>]*?>([^<]*?)<').findall(html)[0]
                data[attr] = val.strip("'")
        r = re.findall("""'input\[name="([^"]+?)"\]'\)\.remove\(\)""", html)
        
        for name in r: del data[name]
        
        normal.addheaders.append(('Referer', url))
        html = normal.open(url, urllib.urlencode(data)).read()
        cj.save(cookie_file,True)
        
        if dialog.iscanceled(): return None
        dialog.update(75)
        
        def custom_range(start, end, step):
            while start <= end:
                yield start
                start += step

        def checkwmv(e):
            s = ""
            i=[]
            u=[[65,91],[97,123],[48,58],[43,44],[47,48]]
            for z in range(0, len(u)):
                for n in range(u[z][0],u[z][1]):
                    i.append(chr(n))
            t = {}
            for n in range(0, 64): t[i[n]]=n
            for n in custom_range(0, len(e), 72):
                a=0
                h=e[n:n+72]
                c=0
                for l in range(0, len(h)):            
                    f = t.get(h[l], 'undefined')
                    if f == 'undefined': continue
                    a = (a<<6) + f
                    c = c + 6
                    while c >= 8:
                        c = c - 8
                        s = s + chr( (a >> c) % 256 )
            return s

        dll = re.compile('<input type="hidden" id="dl" value="(.+?)">').findall(html)
        if dll:
            dl = dll[0].split('GvaZu')[1]
            dl = checkwmv(dl);
            dl = checkwmv(dl);
        else:
            alt = re.compile('<source src="([^"]+?)"').findall(html)
            if alt:
                dl = alt[0]
            else:
                addon.log_error('***** BillionUploads - No Video File Found')
                raise Exception('Unable to resolve - No Video File Found')  
        
        if dialog.iscanceled(): return None
        dialog.update(100)                    

        return dl
        
    except Exception, e:
        addon.log_error('**** BillionUploads Error occured: %s' % e)
        raise
    finally:
        dialog.close()


def resolve_epicshare(url):

    try:
        
        puzzle_img = os.path.join(datapath, "epicshare_puzzle.png")
        
        #Show dialog box so user knows something is happening
        dialog = xbmcgui.DialogProgress()
        dialog.create('Resolving', 'Resolving EpicShare Link...')
        dialog.update(0)
        
        addon.log('EpicShare - Requesting GET URL: %s' % url)
        html = net.http_GET(url).content

        dialog.update(50)
        
        #Check page for any error msgs
        if re.search('This server is in maintenance mode', html):
            addon.log_error('***** EpicShare - Site reported maintenance mode')
            raise Exception('File is currently unavailable on the host')
        if re.search('<b>File Not Found</b>', html):
            addon.log_error('***** EpicShare - File not found')
            raise Exception('File has been deleted')

        wrong_captcha = True
        
        while wrong_captcha:
        
            data = {}
            r = re.findall(r'type="hidden" name="(.+?)" value="(.+?)">', html)

            if r:
                for name, value in r:
                    data[name] = value
            else:
                addon.log_error('***** EpicShare - Cannot find data values')
                raise Exception('Unable to resolve EpicShare Link')

            #Handle captcha
            data = handle_captchas(html, data, dialog)
            
            dialog.create('Resolving', 'Resolving EpicShare Link...') 
            dialog.update(50) 
                
            addon.log('EpicShare - Requesting POST URL: %s' % url)
            html = net.http_POST(url, data).content

            wrong_captcha = re.search('<div class="err">Wrong captcha</div>', html)
            if wrong_captcha:
                addon.show_ok_dialog(['Wrong captcha entered, try again'], title='Wrong Captcha', is_error=False)            
        
        dialog.update(100)
        
        link = re.search('product_download_url=(.+?)"', html)
        if link:
            addon.log('EpicShare Link Found: %s' % link.group(1))
            return link.group(1)
        else:
            addon.log_error('***** EpicShare - Cannot find final link')
            raise Exception('Unable to resolve EpicShare Link')
        
    except Exception, e:
        addon.log_error('**** EpicShare Error occured: %s' % e)
        raise

    finally:
        dialog.close()


def resolve_megarelease(url):

    try:
        
        #Show dialog box so user knows something is happening
        dialog = xbmcgui.DialogProgress()
        dialog.create('Resolving', 'Resolving MegaRelease Link...')
        dialog.update(0)
        
        addon.log('MegaRelease - Requesting GET URL: %s' % url)
        html = net.http_GET(url).content

        dialog.update(50)
        
        #Check page for any error msgs
        if re.search('This server is in maintenance mode', html):
            addon.log_error('***** MegaRelease - Site reported maintenance mode')
            raise Exception('File is currently unavailable on the host')
        if re.search('<b>File Not Found</b>', html):
            addon.log_error('***** MegaRelease - File not found')
            raise Exception('File has been deleted')

        filename = re.search('You have requested <font color="red">(.+?)</font>', html).group(1)
        filename = filename.split('/')[-1]
        extension = re.search('(\.[^\.]*$)', filename).group(1)
        guid = re.search('http://megarelease.org/(.+)$', url).group(1)
        
        vid_embed_url = 'http://megarelease.org/vidembed-%s%s' % (guid, extension)
        
        request = urllib2.Request(vid_embed_url)
        request.add_header('User-Agent', USER_AGENT)
        request.add_header('Accept', ACCEPT)
        request.add_header('Referer', url)
        response = urllib2.urlopen(request)
        redirect_url = re.search('(http://.+?)video', response.geturl()).group(1)
        download_link = redirect_url + filename
        
        dialog.update(100)

        return download_link
        
    except Exception, e:
        addon.log_error('**** MegaRelease Error occured: %s' % e)
        raise
    finally:
        dialog.close()


def resolve_lemupload(url):

    try:
        
        #Show dialog box so user knows something is happening
        dialog = xbmcgui.DialogProgress()
        dialog.create('Resolving', 'Resolving LemUploads Link...')
        dialog.update(0)
        
        addon.log('LemUploads - Requesting GET URL: %s' % url)
        html = net.http_GET(url).content

        dialog.update(50)
        
        #Check page for any error msgs
        if re.search('This server is in maintenance mode', html):
            addon.log_error('***** LemUploads - Site reported maintenance mode')
            raise Exception('File is currently unavailable on the host')
        if re.search('<b>File Not Found</b>', html):
            addon.log_error('***** LemUpload - File not found')
            raise Exception('File has been deleted')

        filename = re.search('<h2>(.+?)</h2>', html).group(1)
        extension = re.search('(\.[^\.]*$)', filename).group(1)
        guid = re.search('http://lemuploads.com/(.+)$', url).group(1)
        
        vid_embed_url = 'http://lemuploads.com/vidembed-%s%s' % (guid, extension)
        
        request = urllib2.Request(vid_embed_url)
        request.add_header('User-Agent', USER_AGENT)
        request.add_header('Accept', ACCEPT)
        request.add_header('Referer', url)
        response = urllib2.urlopen(request)
        redirect_url = re.search('(http://.+?)video', response.geturl()).group(1)
        download_link = redirect_url + filename
        
        dialog.update(100)

        return download_link
        
    except Exception, e:
        addon.log_error('**** LemUploads Error occured: %s' % e)
        raise
    finally:
        dialog.close()


def resolve_hugefiles(url):

    try:

        puzzle_img = os.path.join(datapath, "hugefiles_puzzle.png")
        
        #Show dialog box so user knows something is happening
        dialog = xbmcgui.DialogProgress()
        dialog.create('Resolving', 'Resolving HugeFiles Link...')       
        dialog.update(0)
        
        addon.log('HugeFiles - Requesting GET URL: %s' % url)
        html = net.http_GET(url).content
        
        dialog.update(50)
        
        #Check page for any error msgs
        if re.search('>No such file', html):
            addon.log_error('***** HugeFiles - File Not Found')
            raise Exception('File Not Found')

        wrong_captcha = True
        
        while wrong_captcha:
        
            #Set POST data values
            data = {}
            r = re.findall(r'type="hidden" name="(.+?)" value="(.+?)">', html)
            
            if r:
                for name, value in r:
                    data[name] = value
            else:
                addon.log_error('***** HugeFiles - Cannot find data values')
                raise Exception('Unable to resolve HugeFiles Link')
            
            data['method_free'] = 'Free Download'
            file_name = data['fname']

            #Handle captcha
            data = handle_captchas(html, data, dialog)
            
            dialog.create('Resolving', 'Resolving HugeFiles Link...') 
            dialog.update(50)             
            
            addon.log('HugeFiles - Requesting POST URL: %s DATA: %s' % (url, data))
            html = net.http_POST(url, data).content

            solvemedia = re.search('<iframe src="(http://api.solvemedia.com.+?)"', html)
            recaptcha = re.search('<script type="text/javascript" src="(http://www.google.com.+?)">', html)
            numeric_captcha = re.compile("left:(\d+)px;padding-top:\d+px;'>&#(.+?);<").findall(html)   

            if solvemedia or recaptcha or numeric_captcha:
                addon.show_ok_dialog(['Wrong captcha entered, try again'], title='Wrong Captcha', is_error=False)
            else:
                wrong_captcha = False
            
        #Get download link
        dialog.update(100)

        sPattern = '''<div id="player_code">.*?<script type='text/javascript'>(eval.+?)</script>'''
        r = re.findall(sPattern, html, re.DOTALL|re.I)
        if r:
            sUnpacked = jsunpack.unpack(r[0])
            sUnpacked = sUnpacked.replace("\\'","")
            r = re.findall('file,(.+?)\)\;s1',sUnpacked)
            if not r:
               r = re.findall('name="src"[0-9]*="(.+?)"/><embed',sUnpacked)
            return r[0]
        else:
            addon.log_error('***** HugeFiles - Cannot find final link')
            raise Exception('Unable to resolve HugeFiles Link')
        
    except Exception, e:
        addon.log_error('**** HugeFiles Error occured: %s' % e)
        raise
    finally:
        dialog.close()


def resolve_entroupload(url):

    try:

        #Show dialog box so user knows something is happening
        dialog = xbmcgui.DialogProgress()
        dialog.create('Resolving', 'Resolving EntroUpload Link...')       
        dialog.update(0)
        
        addon.log('EntroUpload - Requesting GET URL: %s' % url)
        html = net.http_GET(url).content
        
        dialog.update(50)
        
        #Check page for any error msgs
        if re.search('<b>File Not Found</b>', html):
            addon.log_error('***** EntroUpload - File Not Found')
            raise Exception('File Not Found')

        #Set POST data values
        data = {}
        r = re.findall(r'type="hidden" name="(.+?)" value="(.+?)">', html)
        
        if r:
            for name, value in r:
                data[name] = value
        else:
            addon.log_error('***** EntroUpload - Cannot find data values')
            raise Exception('Unable to resolve EntroUpload Link')
        
        data['method_free'] = 'Free Download'
        file_name = data['fname']

        addon.log('EntroUpload - Requesting POST URL: %s DATA: %s' % (url, data))
        html = net.http_POST(url, data).content

        #Get download link
        dialog.update(100)

        sPattern =  '<script type=(?:"|\')text/javascript(?:"|\')>(eval\('
        sPattern += 'function\(p,a,c,k,e,d\)(?!.+player_ads.+).+np_vid.+?)'
        sPattern += '\s+?</script>'
        r = re.search(sPattern, html, re.DOTALL + re.IGNORECASE)
        if r:
            sJavascript = r.group(1)
            sUnpacked = jsunpack.unpack(sJavascript)
            sPattern  = '<embed id="np_vid"type="video/divx"src="(.+?)'
            sPattern += '"custommode='
            r = re.search(sPattern, sUnpacked)
            if r:
                return r.group(1)
            else:
                addon.log_error('***** EntroUpload - Cannot find final link')
                raise Exception('Unable to resolve EntroUpload Link')
        else:
            addon.log_error('***** EntroUpload - Cannot find final link')
            raise Exception('Unable to resolve EntroUpload Link')
        
    except Exception, e:
        addon.log_error('**** EntroUpload Error occured: %s' % e)
        raise
    finally:
        dialog.close()


def resolve_donevideo(url):

    try:

        #Show dialog box so user knows something is happening
        dialog = xbmcgui.DialogProgress()
        dialog.create('Resolving', 'Resolving DoneVideo Link...')       
        dialog.update(0)
        
        addon.log('DoneVideo - Requesting GET URL: %s' % url)
        html = net.http_GET(url).content
    
        data = {}
        r = re.findall(r'type="hidden" name="(.+?)" value="(.+?)">', html)
        
        if r:
          for name, value in r:
              data[name] = value
        else:
            addon.log_error('***** DoneVideo - Cannot find data values')
            raise Exception('Unable to resolve DoneVideo Link')
        
        data['method_free'] = 'Continue to Video'
        addon.log('DoneVideo - Requesting POST URL: %s' % url)
        
        html = net.http_POST(url, data).content
        
        dialog.update(50)
                
        r = re.findall(r'type="hidden" name="(.+?)" value="(.+?)">', html)
        
        if r:
          for name, value in r:
              data[name] = value
        else:
          addon.log_error('Could not resolve link')
        
        data['method_free'] = 'Continue to Video'
        
        addon.log('DoneVideo - Requesting POST URL: %s' % url)
        
        html = net.http_POST(url, data).content

        #Get download link
        dialog.update(100)
        
        sPattern = '''<div id="player_code">.*?<script type='text/javascript'>(eval.+?)</script>'''
        r = re.search(sPattern, html, re.DOTALL + re.IGNORECASE)

        if r:
          sJavascript = r.group(1)
          sUnpacked = jsunpack.unpack(sJavascript)
          sUnpacked = sUnpacked.replace("\\","")
                   
        r = re.search("addVariable.+?'file','(.+?)'", sUnpacked)
                
        if r:
            return r.group(1)
        else:
            sPattern  = '<embed id="np_vid"type="video/divx"src="(.+?)'
            sPattern += '"custommode='
            r = re.search(sPattern, sUnpacked)
            if r:
                return r.group(1)
            else:
                addon.log_error('***** DoneVideo - Cannot find final link')
                raise Exception('Unable to resolve DoneVideo Link')

    except Exception, e:
        addon.log_error('**** DoneVideo Error occured: %s' % e)
        raise
    finally:
        dialog.close()
