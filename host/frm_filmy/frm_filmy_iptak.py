# -*- coding: utf-8 -*-
import urllib, urllib2, re, os, sys, math
import xbmcgui, xbmc, xbmcaddon, xbmcplugin
from urlparse import urlparse, parse_qs
import urlparser, base64
import json, libCommon2

class frm_filmy_iptak():
    def __init__(self):
        self.mainUrl = "http://iptak.pl" 
        self.name = "Iptak"
        self.color = 'Fe1680E1'
        self.displayname = "Iptak"
        self.urlhelper = libCommon2.urlhelper()
         
    def getPopular(self):
        return self.urlhelper.getMatches3([self.mainUrl + "/kategoria/wszystkie"], '(?P<group>.*)','<div id="item".*?>\s*?<a title="(.*?)" href="(.*?)">\s*?<img src="(.*?)"', ['title', 'url', 'imgUrl', 'description'])
    
    def search(self, searchString):
       return self.urlhelper.getMatches3([self.mainUrl + '/page/1/?by=date&h&y&s='+ urllib.quote_plus(searchString),self.mainUrl + '/page/2/?by=date&h&y&s='+ urllib.quote_plus(searchString)],'(?P<group>.*)','<div id="item".*?>\s*?<a title="(.*?)" href="(.*?)">\s*?<img src="(.*?)"', ['title', 'url', 'imgUrl', 'description'])
 
   # server links for video
    def getPlaySource(self, url):
       #{playMovie("23307475","cda"){playMovie("95492e0","cda");}
       #http://iptak.pl/dodatki/php/ogladaj2.php?g=23307475&host=cda 
        pageData = self.urlhelper.getMatches(url, '\{playMovie\("(.*?)","(.*?)"\);\}', ['id','host'])
        #http://www.cda.pl/video/23307475
        return {"Stream 1": "http://www.cda.pl/video/" + pageData.first["id"] }
