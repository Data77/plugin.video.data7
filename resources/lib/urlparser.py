import mrknow_urlparser
import re

try:
    import urlresolver
except ImportError:
    print 'No urlresolver module'


class urlparser:
    def __init__(self):
        self.up = mrknow_urlparser.mrknow_urlparser()

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

        #streamin fix
        if host == 'streamin.to':
            url = url.replace('/video','')
        #openload fix
        if host == 'openload.co':
            url = url.replace('/video','/embed')
            url = url.replace('.co','.io')

        #vidto.me fix
        if host == 'vidto.me':
            url = url.replace('/v/','/')

        nUrl = self.up.getVideoLink(url, referer)
    
        # unknow sources
        if nUrl=='':        
            nnUrl = urlresolver.resolve(url) 
            if nnUrl == False:
                nUrl = url
            else:
                nUrl = nnUrl
            print "Unknow source url: " + str(nnUrl)

        print "X Url found in UrlParser: " + str(nUrl)
        return nUrl	
