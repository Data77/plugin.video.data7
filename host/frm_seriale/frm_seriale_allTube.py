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

class frm_seriale_allTube():
    def __init__(self):
        self.mainUrl = "http://alltube.tv/" 
        self.name = "AllTube"
        self.color = "EeF7DFAF"
        self.up = urlparser.urlparser()
        self.displayname = "All Tube"
        self.urlhelper = libCommon2.urlhelper()

# lista z pierwszej strony
    def getPopular(self):
        result = self.urlhelper.getMatches2(self.mainUrl+'seriale-online/','(.*)','<a href="([^"]*?)">.*?<img src="([^"]*?)"[^>]*?alt="([^"]*?)"', ['url', 'imgUrl','title','description'])
        return result 

# lista odcinków - jeden request per sezon
    def getEpisodes(self, url):
        array = self.urlhelper.getMatches(url,'<li class="episode"><a href="(.*?)">(\[.*?\])(.*?)</a></li>', ['url','number','title','description'])
        array.items = sorted(array.items, reverse=True) 
        return array    

    def getAlphabetic(self, letters):
        searchString = '[' + "|".join(letters) + ']' 
        return self.urlhelper.getMatches(self.mainUrl + 'seriale-online/',' <li data-letter="' + searchString + '"><a href="(.*?)">(.*?)</a></li>', ['url', 'title', 'imgUrl', 'description'])


# search - lista z pierwszej strony ( po prawej)
    def search(self, searchString):
       postdata = {"search" : searchString.replace("+", " ") }
       return self.urlhelper.getMatches2(self.mainUrl + '/szukaj','.*','<a href="(([^<]*?)/serial/([^<]*?))">(.*?)</a>', ['url', 'n1','n2', 'title','imgUrl', 'description'], postdata)
       

# link do servera
    def getPlaySource(self, url):
        links = {}
        1
        pageData = self.urlhelper.getMatches(url, '<img src="[^>]*?" alt="([^>]*?)">[^<]*?<.td>[^<]*?<td style="width: 100px;">.*?class="watch" data-iframe="([^"]*?)">.*?class="text-center">([^<]*?)</td>.*?<div class="rate">([^<]*?)</div>', ['server',  'url', 'version', 'percent'])  
      
        i = 0
        for item in pageData.items:
            i=i+1
            num = str(i)
            if i<10:
                num = "0"+str(i)
            links[num + '. ' +item["server"] + " - " + item["version"] + ' (' + item["percent"] +')' ] =  base64.b64decode(item["url"])
        
        return links