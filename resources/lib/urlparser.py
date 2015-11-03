import mrknow_urlparser
import re
import libCommon2
import time

try:
    import urlresolver
except ImportError:
    print 'No urlresolver module'


class urlparser:
    def __init__(self):
        self.up = mrknow_urlparser.mrknow_urlparser()
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
        
            #openload fix
        if host == 'openload.co':
            url = url.replace('/video/','/embed/')
            url = url.replace('.co','.io')
        
        if host == 'video.tt':
            url = url.replace('/video/','/embed/')
            url = url.replace('watch_video.php?v=','')

        if host.endswith('dwn.so'):
            url = self.resolveDwnSo(url)
            return url
        if host.endswith('allmyvideos.net'):
            url = self.resolveAllmyvideosNet(url)
            return url

        if returnUrl != '':
            print "## Url found in my UrlParser: " + str(returnUrl)
            return returnUrl

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
        return nUrl	

    def resolveAllmyvideosNet(self, url,referer=''):
        pageData = self.urlhelper.getMatches(url, '"file" : "(.*?)"', ['url'], True)
        if pageData.first:
            return pageData.first['url']

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