# -*- coding: utf-8 -*-
import urllib, urllib2, re, os, sys, math
import xbmcgui, xbmc, xbmcaddon, xbmcplugin
from urlparse import urlparse, parse_qs
import urlparser, base64
import json, libCommon2

class frm_filmy_zalukajtv():
    def __init__(self):
        self.mainUrl = "http://zalukaj.com" 
        self.name = "Zalukaj"
        self.color = "e11Fe680"
        self.up = urlparser.urlparser()
        self.displayname = "Zalukaj TV"
        self.urlhelper = libCommon2.urlhelper()

# lista z pierwszej strony    
    def getPopular(self):
        return self.urlhelper.getMatches(self.mainUrl,'<div class="tivief4">.*?<div style="float:left;"><img style=".*?" src="(.*?)"/></div>\s*?<div class="rmk23m4">\s*?<h3><a href="(.*?)" title="(.*?)">', ['imgUrl', 'url', 'title','description'])

# search - lista z pierwszej strony ( po prawej)    
    def search(self, searchString):
       postdata = {"searchinput" : searchString.replace("+", " ") }
       returnValue = self.urlhelper.getMatches2(self.mainUrl + '/szukaj','.*','<div class="tivief4">.*?<div style="float:left;"><img style=".*?" src="(.*?)"/></div>\s*?<div class="rmk23m4">\s*?<h3><a href="(.*?)" title="(.*?)">', ['imgUrl', 'url', 'title','description'], postdata)
       return returnValue

# link  do servera
    def getPlaySource(self, url):
        links = {}
        pageData = self.urlhelper.getMatches(url, '<iframe allowTransparency="true" src="(.*?)"', ['id'], True)
        if pageData.first:
            playerUrl = self.mainUrl + pageData.first["id"]+"&x=1"
            pageData = self.urlhelper.getMatches(playerUrl, 'hrefx="(.*?)"><span>(.*?)</span></a>', ["id","title"])
            if pageData.items:
                for item in pageData.items:
                    pageData = self.urlhelper.getMatches(self.mainUrl + pageData.first["id"]+"&x=1", '<iframe src="(.*?)" width=".*?" height=".*?" frameborder="0" scrolling="no"></iframe>', ["id"], True)
                    links["Wersja " + item["title"]] = pageData.first["id"]
            else:
                 pageData = self.urlhelper.getMatches(playerUrl, '<iframe src="(.*?)" width=".*?" height=".*?" frameborder="0" scrolling="no"></(iframe)>', ["id","dummy"])
                 links["Wersja 1"] = pageData.first["id"]
        else:
            pageData = self.urlhelper.getMatches(url, 'bold;" href="(.*?)" target="_blank">Ogladaj', ['id'], True)
            links["Wersja 1"] = pageData.first["id"]

        print " ZALUKAJ"" :INKS FOUND " + str(links)
        return links