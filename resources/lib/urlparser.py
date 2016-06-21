import re
import libCommon2
import time
import urlparse
import xbmcaddon
import os

#import resolver
try:
    import urlresolver
except:
    print 'No urlresolver module'

try:
    import mrknow_urlparser
except:
    print 'No mrknow_urlparser module'
	
HOST = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.101 Safari/537.36'
ptv = xbmcaddon.Addon()

class urlparser:
    def __init__(self):
		try:
			self.up = mrknow_urlparser.mrknow_urlparser()
		
		except:
			print 'No urlresolver module'

		self.COOKIEFILECDA = ptv.getAddonInfo('path') + os.path.sep + "cookies" + os.path.sep + "cdapl.cookie"
		self.urlhelper = libCommon2.urlhelper()

        


    def getHostName(self, url, nameOnly=False):
        hostName = ''
        match = re.search('http://(.+?)/', url)
        match1 = re.search('https://(.+?)/', url)
        if match:
            hostName = match.group(1)
            if (nameOnly):
                n = hostName.split('.')
                hostName = n[-2]
        elif match1:
            hostName = match1.group(1)
            if (nameOnly):
                n = hostName.split('.')
                hostName = n[-2]
        return hostName


    def getVideoLink(self, url,referer=''):
        host = self.getHostName(url)
        subUrl = ''
        print "## Url to resolve in UrlParser(host:" + host + "): " + str(url)

        
        returnUrl = ''
        #streamin fix
        if host == 'streamin.to':
            url = url.replace('/video','')
        
        #vidto.me fix
        if host == 'vidto.me':
            url = url.replace('/v/','/')
        
        #efilmy.net
        if 'efilmy.net' in host:
            pageData = self.urlhelper.getMatches(url, ' <div id="playerVidzer">.*?<a href="(.*?)" .*?</a>', ["id"], True)
            if pageData.first:
                returnUrl = pageData.first["id"]  
        
        if host.endswith('alltube.tv'):
            print "## Url found in ALLTUBE: " + str(url)
            url = self.resolveAlltubeTv(url)
            host = self.getHostName(url)
     
        print "HOSTNAME:::" + host
   
            #openload fix
        if host == 'openload.co':
            url = url.replace('/video/','/embed/')
            url = url.replace('.co','.io')
        
        if host == 'video.tt':
            url = url.replace('/video/','/embed/')
            url = url.replace('watch_video.php?v=','')

        if host.endswith('dwn.so'):
            url = self.resolveDwnSo(url)
            return { 'video': url, "subtitles": subUrl }

        if host.endswith('allmyvideos.net'):
            url = self.resolveAllmyvideosNet(url)
            return { 'video': url, "subtitles": subUrl }

        #if host.endswith('ebd.cda.pl'):
        #    url = self.resolveEbdcda(url)
        #    print "## Url found in CDA: " + str(url)
        #    return { 'video': url, "subtitles": subUrl }
      
        #if host.endswith('cda.pl'):
        #    url = self.resolveCDA(url,referer)
        #    print "## Url found in CDA: " + str(url)
        #    return { 'video': url, "subtitles": subUrl }

        if host.endswith('cda.pl'):
            url = self.parserCDA2(url,referer)
            print "## Url found in CDA: " + str(url)
            return { 'video': url, "subtitles": subUrl }


        # look for subtitles
        if 'openload' in host:
            subUrl = self.resolveOpenloadSubtitles(url)
            

        if host.endswith('vshare.io'):
            url = self.resolveVSHARE(url,referer)
            print "## Url found in VSHARE.IO: " + str(url)
            return { 'video': url, "subtitles": subUrl }


        if returnUrl != '':
            print "## Url found in my UrlParser: " + str(returnUrl)
            return { 'video': returnUrl, "subtitles": subUrl }

        nUrl = ''   
        try:
            nUrl = self.up.getVideoLink(url, referer)
            print "## Url found in mrKnowUrlParser: " + str(url)
        except:
            pass
 

        # unknow sources
        if nUrl == '' or nUrl == url:        
            nnUrl = urlresolver.resolve(url) 
            if nnUrl == False:
                nUrl = url
            else:
                nUrl = nnUrl
            print "Unknow source url: " + str(nnUrl)

        print "## Url found in UrlParser: " + str(nUrl)


        return { 'video': nUrl, "subtitles": subUrl }







# SPECIFIC RESOLVERS

    def resolveAllmyvideosNet(self, url,referer=''):
        pageData = self.urlhelper.getMatches(url, '"file" : "(.*?)"', ['url'], True)

        if pageData.first:
            return pageData.first['url']


    def resolveOpenloadSubtitles(self, url):
        result = self.urlhelper.getMatches(url.replace('http://', 'https://'),'<track kind="captions" src="(.*?)"', ['url'], singleElement=True)        
        
        print "resolveOpenloadSubtitles::::" + str(result.items)

        nUrl = ""

        if result.items:
            nUrl = result.items[0]["url"]
            print "resolveOpenloadSubtitles::::" + str(nUrl)

            return nUrl
        

    def resolveAlltubeTv(self, url,referer=''):
        print "resolveAlltubeTv::::" + str(url)

        result = self.urlhelper.getMatches(url,'<iframe src="(.*?)"', ['url'], singleElement=True)        
        
        print "resolveAlltubeTv::::" + str(result.items)

        nUrl = ""

        if result.items:
            nUrl = result.items[0]["url"].replace("\\", "")
            print "resolveAlltubeTv::::" + str(nUrl)

            return nUrl
 
        return ""



    def resolveVSHARE(self, url,referer=''):
        print "resolveVSHARE::::" + str(url)

        result = self.urlhelper.getMatches(url,"url\:.'(.*?)'", ['url'], singleElement=True)        
        
        print "resolveVSHARE2::::" + str(result.items)

        nUrl = ""

        if result.items:
            nUrl = result.items[0]["url"].replace("\\", "")
            print "resolveVSHARE25::::" + str(nUrl)

            return nUrl

        result = self.urlhelper.getMatches(url,'\"bitrates\"\:\[\{"url":"(.*?)",', ['url'], singleElement=True)        
        
        print "resolveVSHARE3::::" + str(result.items)

        if result.items:
            nUrl = result.items[0]["url"].replace("\\", "")
            print "resolveVSHARE4::::" + str(nUrl)

            return nUrl

        return ""


    def resolveDwnSo(self, url,referer=''):
        print "resolveDwnSo0::::" + str(url)
        
        pageData = self.urlhelper.getMatches(url, "SWFObject\('http://st.dwn.so/player/play4.swf\?v=(.*?)\&yk=(.*?)','.*?','(.*?)','.*?','.*?'\);", ['ds','yk','width'])
        nUrl = ''
        
        print "resolveDwnSo1::::" + str(pageData.first)

        if pageData.first:
            timestamp = int(time.time())

            self.urlhelper.getMatches('http://st.dwn.so/xml/second.php?uid=' + str(timestamp) + '&regular=1', '(.*?)', ['url'],True, postdata = None, headers = None, referer = url)


            nUrl = 'http://st.dwn.so/xml/videolink.php?v=' + pageData.first['ds'] + '&yk=' + pageData.first['yk'] + '&width=' + pageData.first['width'] + '&id=' + str(timestamp) + '&u=undefined' 

            pageData = self.urlhelper.getMatches(nUrl, 'un="(.*?)"', ['url'],True)

            print "resolveDwnSo2::::" + str(pageData.first)
            if pageData.first:
                nUrl = pageData.first["url"] 

        return nUrl

    def resolveEbdcda(self, url):
        print "resolveEbdcda::::" + str(url)

        # document.getElementById('mediaplayer-23573963').href =
        # 'http://vrbx047.cda.pl/Ae7DAEHvmGQQWDMoZVOSNA/1464313703/vlcbc2ee06d4bcbafc0e505799757f4483.mp4';
            
        result = self.urlhelper.getMatches(url,"document\.getElementById\('.*?'\)\.href.?=.?'(.*?)'", ['url'], singleElement=True)        
        
        print "resolveEbdcda::::" + str(result.items)

        nUrl = ""

        if result.items:
            nUrl = result.items[0]["url"].replace("\\", "")
            print "resolveEbdcda::::" + str(nUrl)

            return nUrl
 
        return ""



    def resolveCDA(self, url , referer, showwindow=''):
        
        ##http://www.cda.pl/video/72199896 HTTP/1.1
        ##http://ebd.cda.pl/740x487/72199896
        #http://www.cda.pl/video/722826df
        match = re.compile("http://[^/]*?/[^/]*?/(.*?)$", re.DOTALL | re.IGNORECASE).findall(url)

        if len(match) > 0:
            print str(match)
            return self.resolveEbdcda("http://ebd.cda.pl/740x487/" + match[0])            

        query_data = {'url': url.replace('m.cda.pl', 'www.cda.pl'), 'use_host': True, 'host': HOST, 'use_cookie': False,
                        'use_post': False, 'return_data': True}
        link = self.urlhelper.getURLRequestData(query_data)
        match = re.search("""file: ['"](.+?)['"],""", link)
        match2 = re.compile('<a data-quality="(.*?)" (.*?)>(.*?)</a>', re.DOTALL).findall(link)
        match3 = re.search("url: '(.*?)'", link)
        if match2 and showwindow == 'bitrate':
            tab = []
            tab2 = []
            for i in range(len(match2)):
                match3 = re.compile('href="(.*?)"', re.DOTALL).findall(match2[i][1])
                if match3:
                    tab.append('Wideo bitrate - ' + match2[i][2])
                    tab2.append(match3[0])
            d = xbmcgui.Dialog()
            video_menu = d.select("Wybór jakości video", tab)

            if video_menu != "":
                #print("AMAMAMA ",video_menu)
                #print("TABBBBBBBBBBBBBBBBBBBBBBBBB",tab,tab2[video_menu])
                url = match2[video_menu][0]
                query_data = {'url': 'http://www.cda.pl' + tab2[video_menu], 'use_host': True, 'host': HOST, 'use_cookie': False,                       'use_post': False, 'return_data': True}
                link = self.cm.getURLRequestData(query_data)
                match = re.search("""file: ['"](.+?)['"],""", link)
                match3 = re.search("url: '(.*?)'", link)
        if match:
            linkVideo = match.group(1) + '|Cookie="PHPSESSID=1&Referer=http://static.cda.pl/player5.9/player.swf'
        elif match3:
            linkVideo = match3.group(1) + '|Cookie="PHPSESSID=1&Referer=http://static.cda.pl/player5.9/player.swf'
        else:
            linkVideo = ''
        return linkVideo



    def parserCDA2(self,url,referer,showwindow=''):
        
        myparts = urlparse.urlparse(url)
        #self.log(myparts.path)
        inUrl = url
        videoUrls = ''
        vidMarker = '/video/'
        if vidMarker not in myparts.path:
            vid = myparts.path.split('/')[-1]
            inUrl = 'http://ebd.cda.pl/620x368/' + vid + "?"

        if vidMarker in myparts.path:
            print("A",myparts.path,myparts.path.replace(vidMarker,''))
            vid = myparts.path.replace(vidMarker,'').split("/")[0]
            inUrl = 'http://ebd.cda.pl/620x368/' + vid + "?"

        query_data = {'url': inUrl, 'use_host': True, 'host': HOST, 'use_cookie': True, 'save_cookie': False, 'load_cookie': True, 'cookiefile': self.COOKIEFILECDA, 'use_post': False, 'return_data': True}
        link = self.urlhelper.getURLRequestData(query_data)
        #self.log(inUrl)
        match2 = re.compile('<a data-quality="(.*?)"(.*?)>(.*?)</a>', re.DOTALL).findall(link)


        if match2 and showwindow == 'bitrate':
            tab = []
            tab2 = []

            for i in range(len(match2)):
                if 'data-video_id=' in match2[i][1]:
                    match3 = re.compile('data-video_id="(.*?)".*href="(.*?)"').findall(match2[i][1])
                    #self.log("Cda link1 - http://ebd.cda.pl/620x368/"+
                    #match3[0][0] + match3[0][1])
                    if match3:
                        tab.append('Wideo bitrate - ' + match2[i][2])
                        tab2.append('http://ebd.cda.pl/620x368/' + vid + match3[0][1])
                else:
                    match3 = re.compile('href="(.*?)"', re.DOTALL).findall(match2[i][1])
                    #self.log("Cda link2 - " + match3[0])
                    if match3:
                        tab.append('Wideo bitrate - ' + match2[i][2])
                        tab2.append(match3[0])

            d = xbmcgui.Dialog()
            video_menu = d.select("Wybór jakości video", tab)


            if video_menu != "":
                url = tab2[video_menu]
                query_data = {'url': url, 'use_host': True, 'host': HOST, 'use_cookie': True, 'save_cookie': False, 'load_cookie': True, 'cookiefile': self.COOKIEFILECDA,  'use_post': False, 'return_data': True}
                link = self.urlhelper.getURLRequestData(query_data)
                #self.log('LINK ####: %s ' % query_data)

        match20 = re.search("file: '(.*?)mp4'", link)
        if match20:
            return match20.group(1) + 'mp4|Cookie=PHPSESSID=1&Referer=http://static.cda.pl/flowplayer/flash/flowplayer.commercial-3.2.18.swf'


        match3 = re.search("duration: '(.*?)',\s*url: '(.*?)',", link)
        match5 = re.compile("eval(.*?)\{\}\)\)", re.DOTALL).findall(link)
        match9 = re.search("\$\.get\((.*?),{id:(.*?),ts:(.*?),k:'(.*?)'}",link)

        if match9:
            url2 = 'http://ebd.cda.pl/a/o?id=' + match9.group(2) + '&ts=' + match9.group(3) + '&k=' + match9.group(4)
            query_data = {'url': url2, 'use_host': True, 'host': HOST, 'use_cookie': False, 'use_post': False, 'return_data': True}
            link2 = self.urlhelper.getURLRequestData(query_data)

        if match5:

            from utils import unpackstd
            mojestr = match5[0]
            mojestr = mojestr.replace("\\'","")
            decoded = unpackstd.unpack(mojestr)
            match7 = re.search('src="(.*?).mp4"',decoded)
            if match7:
                return match7.group(1) + '.mp4|Cookie=PHPSESSID=1&Referer=http://static.cda.pl/flowplayer/flash/flowplayer.commercial-3.2.18.swf'

        if match3:
            videoUrls = match3.group(2) + '|Cookie=PHPSESSID=1&Referer=http://static.cda.pl/flowplayer/flash/flowplayer.commercial-3.2.18.swf'

        return videoUrls
