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
from urlparse import urlparse, parse_qs
import urlparser
import base64
import json
import libCommon2  
import operator

class frm_seriale_seriestv():
    def __init__(self):
        self.mainUrl = "http://stream-tv2.co/" 
        self.name = "SeriesTv"
        self.color = "EeF7DFAF"
        self.up = urlparser.urlparser()
        self.displayname = "Series tv"
        self.urlhelper = libCommon2.urlhelper()

# lista z pierwszej strony
    def getPopular(self):
        result = self.urlhelper.getEmpty()
        return result 

# lista odcinków - jeden request per sezon
    def getEpisodes(self, url):
        array = self.urlhelper.getMatches(url,'<li><a href="(.*?)"[^>]*?>.*?Season([^>]*?) Episode (\d{0,2})[<|\s](/a> –|\s|–|&#8211)(.*?)(</li>|</a>)', ['url','number','number1','fu','title','bar','description'])
        
        for item in array.items:
            number = item["number"].strip()
            number1 = item["number1"].strip()
            
            item["title"] = item["title"].replace(';','')

            if int(item["number"]) < 10:
                number =  '0' + number
            if int(item["number1"]) < 10:
                number1 =  '0' + number1 
            item["number"]= '(s' + number + 'e' + number1 + ') '

        array.items = sorted(array.items, reverse=True) 
        
        return array    

    def getAlphabetic(self, letters):
        searchString = '[' + "|".join(letters) + ']' 
        return self.urlhelper.getMatches(self.mainUrl,'<li><a href="(.*?)">('+searchString+'[^<]*?)</a>', ['url', 'title', 'imgUrl', 'description'])


# search - lista z pierwszej strony ( po prawej)
    def search(self, searchString):
       return self.urlhelper.getMatches(self.mainUrl,'<li><a href="([^<]*?)">([^<]*?'+searchString+'[^<]*?)</a>', ['url', 'title', 'imgUrl', 'description'])


# link do servera
    def getPlaySource(self, url):
        links = {}
        
        pageData = self.urlhelper.getMatches(url, '<b>(.*?)</b></span><br />.*?<IFRAME SRC="(.*?)" [^>]*?></IFRAME>', ['server', 'url'])
        i = 0
        for item in pageData.items:
            i = i + 1 
            links[str(i) +'. '+ item["server"]] = item["url"]
        
        return links