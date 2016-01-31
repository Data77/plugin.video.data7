# -*- coding: utf-8 -*-
import urllib
import urllib2
import re
import os
import sys
import math
import xbmcgui
import xbmc
import xbmcaddon
import xbmcplugin
import base64
import json
import settings
import UParser
import cookielib

scriptID = sys.modules["__main__"].scriptID
ptv = xbmcaddon.Addon(scriptID)

HOST = 'Mozilla/5.0 (Windows NT 6.1; rv:17.0) Gecko/20100101 Firefox/17.0'
HISTORYFILE = xbmc.translatePath(ptv.getAddonInfo('profile') + "history.xml")

dbg = False

class Struct:
    def __init__(self, **entries): self.__dict__.update(entries)
    def __eq__(self, other): return self.__dict__ == other.__dict__
    def __neq__(self, other): return self.__dict__ != other.__dict__
    def __lt__(self, other):
        return self.number < other.number

class urlhelper:
    HOST = HOST
    HEADER = None
	
    def __init__(self):
        self.settings = settings.TVSettings()
        self.parser = UParser.UParser()

    def clearString(self,string):
        try:
            string = self.hp.unescape(urllib.unquote(string))
        except:
            pass

        string = string.replace('/u0144', "ń")
        string = string.replace('/u0142', "ł")
        string = string.replace('/u017c', "ż")
        string = string.replace('/u00f3', "ó")
        string = string.replace('/u017a', "ź")
        string = string.replace('/u0107', "ć")
        string = string.replace('/u0119', "ę")
        string = string.replace('/u015b', "ś")
        string = string.replace('/u0105', "ą")




        string = string.replace('<', " ")
        string = string.replace('>', " ")
        string = string.replace('\\', "/")
        string = string.replace('&#8230;', "-")
        string = string.replace('8217', "'")
        string = string.replace('oacute;', "ó")
        string = string.replace('&#039;', "'")
        string = string.replace('&amp;', "&")
        string = string.replace('&quot;', '"')        
        string = string.replace('\t', ' ')
        string = string.replace('\n', ' ')
        string = string.replace('&#', '')
        string = string.replace('&', '')
        while '  ' in string:
           string = string.replace('  ', ' ')
        return string.strip()

    def getEmpty(self):
        return Struct(pageData = None, items= [], first = None)

    def getMatches(self, url, regex, array, singleElement=False, postdata=None, headers=None, referer = None):
        query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'save_cookie': False, 'load_cookie': False, 'use_post': True, 'return_data': True , "headers" : headers,"referer" : referer}       
        pageData = self.getURLRequestData(query_data, postdata)
        match = re.compile(regex, re.DOTALL | re.IGNORECASE).findall(pageData)
        returnData = Struct(pageData = pageData, items= [], first = None)
        if not singleElement:
            if len(match) > 0 :			
                for i in range(len(match)):
                    entry = {}
                    #print 'MATCH:' + str(i)
                    for x in range(len(array)):
                        entry[array[x]] = ""
                        if(len(match[i]) > x):
                            entry[array[x]] = match[i][x]
                    
                    returnData.items.append(entry)    
        else:
            if len(match) > 0 :			
                #print "len:::" +
                for i in range(len(array)):
                    #print "MATCHES::::" + str(i) + " " + str(match[i]) + " :::
                    #" + array[i]
                    entry = {}
                    entry[array[i]] = match[i]
                    returnData.items.append(entry)
                
        if len(returnData.items) > 0:
            returnData.first = returnData.items[0]
        return returnData

    def getMatches2(self, url, prefilterRegex, regex, array, postdata=None, headers=None, referer=None):
        query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'save_cookie': False, 'load_cookie': False, 'use_post': True, 'return_data': True, "headers" : headers, "referer" : referer }       
        pageData = self.getURLRequestData(query_data, postdata)
        returnData = Struct(pageData = pageData, items= [])
        
        match0 = re.compile(prefilterRegex, re.DOTALL | re.IGNORECASE).findall(pageData)
        
        if len(match0) == 0:
            return returnData

        for basematch in match0:
            match = re.compile(regex, re.DOTALL | re.IGNORECASE).findall(basematch)
        
            if len(match) > 0:			
                for i in range(len(match)):
                    entry = {}
                    for x in range(len(array)):
                        entry[array[x]] = ""
                        if(len(match[i]) > x):
                            entry[array[x]] = match[i][x]

                    returnData.items.append(entry)    
                
        return returnData

    def getMatches3(self, urls, prefilterRegex, regex, array):
        allitems = []

        for url in urls:
            retValue = self.getMatches2(url, prefilterRegex, regex, array)
            allitems.extend(retValue.items)
        retValue.items = allitems
        
        return retValue

    
    def getURLRequestData(self, params={}, post_data=None):
        
        def urlOpen(req, customOpeners):
            if len(customOpeners) > 0:
                opener = urllib2.build_opener(*customOpeners)
                response = opener.open(req)
            else:
                response = urllib2.urlopen(req)
            return response
        
        cj = cookielib.MozillaCookieJar()

        response = None
        req = None
        out_data = None
        opener = None
        referer = None
		
        if 'host' in params:
            host = params['host']
        else:
            host = self.HOST
			
        if 'header' in params:
            headers = params['header']
        elif None != self.HEADER:
            headers = self.HEADER
        else:
            headers = { 'User-Agent' : host }

        if dbg == 'true':
                log.info('pCommon - getURLRequestData() -> params: ' + str(params))
                log.info('pCommon - getURLRequestData() -> params: ' + str(headers))

        customOpeners = []
        #cookie support
        if 'use_cookie' not in params and 'cookiefile' in params and ('load_cookie' in params or 'save_cookie' in params):
            params['use_cookie'] = True 
        
        if params.get('use_cookie', False):
            customOpeners.append(urllib2.HTTPCookieProcessor(cj))
            if params.get('load_cookie', True):
                cj.load(params['cookiefile'], ignore_discard = True)

        if None != post_data:
            if dbg == 'true': log.info('pCommon - getURLRequestData() -> post data: ' + str(post_data))
            if params.get('raw_post_data', False):
                dataPost = post_data
            else:
                dataPost = urllib.urlencode(post_data)
            req = urllib2.Request(params['url'], dataPost, headers)
        else:
            req = urllib2.Request(params['url'], None, headers)

			
        if 'referer' in params:
			req.add_header('Referer', params['referer'])

        if not params.get('return_data', False):
            out_data = urlOpen(req, customOpeners)
        else:
            gzip_encoding = False
            try:
                response = urlOpen(req, customOpeners)
                if response.info().get('Content-Encoding') == 'gzip':
                    gzip_encoding = True
                data = response.read()
                response.close()
            except urllib2.HTTPError, e:
                if e.code == 404:
                    if dbg == 'true': log.info('pCommon - getURLRequestData() -> !!!!!!!! 404 - page not found handled')
                    if e.fp.info().get('Content-Encoding') == 'gzip':
                        gzip_encoding = True
                    data = e.fp.read()
                    #e.msg
                    #e.headers
                else:
                    #printExc()
                    raise 
    
            try:
                if gzip_encoding:
                    if dbg == 'true': log.info('pCommon - getURLRequestData() -> Content-Encoding == gzip')
                    buf = StringIO(data)
                    f = gzip.GzipFile(fileobj=buf)
                    out_data = f.read()
                else:
                    out_data = data
            except:
                out_data = data
 
        if params.get('use_cookie', False) and params.get('save_cookie', False):
            cj.save(params['cookiefile'], ignore_discard = True)

        return out_data 
        
    def get_captcha(self, imgUrl):
        try:
            img = xbmcgui.ControlImage(450, 0, 400, 130, imgUrl)
            wdlg = xbmcgui.WindowDialog()
            wdlg.addControl(img)
            wdlg.show()
            xbmc.sleep(500)
            kb = xbmc.Keyboard('', 'Type the letters in the image', False)
            kb.doModal()
            if (kb.isConfirmed()):
                solution = kb.getText()
                if solution == '':
                    raise Exception('You must enter text in the image to access video')
                else:
                    return solution
            else:
                raise Exception('Captcha Error')
        finally:
            wdlg.close()
       



class reflectionHelper:
    def get_class_name(self,mod_name):
        output = ""

        # Split on the _ and ignore the 1st word plugin
        words = mod_name.split("_")[1]
        
        # Capitalise the first letter of each word and add to string
        for word in words:
            output += word.title()
        return mod_name