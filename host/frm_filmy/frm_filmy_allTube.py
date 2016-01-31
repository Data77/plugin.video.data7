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

class frm_filmy_allTube():
    def __init__(self):
        self.mainUrl = "http://alltube.tv/" 
        self.name = "AllTube"
        self.color = "EeF7DFAF"
        self.up = urlparser.urlparser()
        self.displayname = "All Tube"
        self.urlhelper = libCommon2.urlhelper()

# lista z pierwszej strony
    def getPopular(self):
        result = self.urlhelper.getMatches2(self.mainUrl,'<h2>ostatnio dodane Filmy</h2>(.*?)<h2>','<div class="row">.*?<a href="([^<]*?)">.*?<img src="([^<]*?)"[^<]*?class="img-responsive">.*?<h3>([^<]*?)</h3>', ['url','imgUrl','title','description'])
        return result 

# search - lista z pierwszej strony ( po prawej)
    def search(self, searchString):
       postdata = {"search" : searchString.replace("+", " ") }
       return self.urlhelper.getMatches2(self.mainUrl + '/szukaj','.*','<a href="(([^<]*?)/film/([^<]*?))">(.*?)</a>', ['url', 'n1','n2', 'title','imgUrl', 'description'], postdata)
       

# link do servera
    def getPlaySource(self, url):
        links = {}
        
        pageData = self.urlhelper.getMatches(url, '([^>]*?)</td>.*?data-urlhost="([^>]*?)".*?data-version="([^>]*?)".*?<div class="rate">([^>]*?)%</div>.*?</tr>', ['server',  'url', 'version', 'percent'])
      

        for item in pageData.items:
            links[item["server"] + " - " + item["version"] + ' (' + item["percent"] +'%)' ] = item["url"]
        
        return links