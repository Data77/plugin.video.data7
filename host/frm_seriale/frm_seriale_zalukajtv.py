# -*- coding: utf-8 -*-
import urllib, urllib2, re, os, sys, math
import xbmcgui, xbmc, xbmcaddon, xbmcplugin
from urlparse import urlparse, parse_qs
import urlparser, base64
import json, libCommon2

class frm_seriale_zalukajtv():
    def __init__(self):
        self.mainUrl = "http://zalukaj.tv" 
        self.name = "Zalukaj"
        self.color = "e11Fe680"
        self.up = urlparser.urlparser()
        self.displayname = "Zalukaj TV"
        self.urlhelper = libCommon2.urlhelper()
# lista z pierwszej strony    
    def getPopular(self):
        return self.urlhelper.getMatches2(self.mainUrl + "/seriale",'<div class="blok1">(?P<group>.*?)<div class="doln">&nbsp;</div>',  'div class="latest tooltip">\s*?<a href="(.*?)" title="(.*?)"><img alt=".*?" src="(.*?)"></a>', ['url', 'title', 'imgUrl', 'description'])

    def getAlphabetic(self, letters):        
        searchString = '['+ "|".join(letters) + ']' 
        return self.urlhelper.getMatches2(self.mainUrl + '/seriale','<div id="two">(?P<group>.*?)<div class="doln"></div>','<td class="wef32f"><a href="([^<]*?)" title="[^<]*?">('+searchString+'[^<]*?)</a>', ['url', 'title', 'description', 'imgUrl'])


# lista odcinków - jeden request per sezon    
    def getEpisodes(self, url):
        url = self.mainUrl + url

        array = self.urlhelper.getMatches(url, '<a style="line-height:0px;" href="(.*?)"', ['url'],True)
        if array.first:
            url = array.first["url"]
        
        array = self.urlhelper.getMatches2(url, '<div id="sezony"(?P<group>.*?)<div class="doln2"></div>', '<a class="sezon" href="([^"]*?)"[^>]*?>(.*?)</a>', ['url','title'])
        list = []
        for item in array.items:
            res =  self.urlhelper.getMatches2(self.mainUrl + item["url"], '<div id="odcinkicat">(?P<group>.*?)<div class="doln2">','<div align="left" id="sezony".*?>(.*?)<a href="(.*?)" title="(.*?)">', ['number', 'url', 'title','description'])
            for resItem in reversed(res.items):
                list.append(resItem)
        array.items = reversed(list)
        return array    

# search - lista z pierwszej strony ( po prawej)    
    def search(self, searchString):
       searchString = urllib.quote_plus(searchString) 
       return self.urlhelper.getMatches2(self.mainUrl + '/seriale','<div id="two">(?P<group>.*?)<div class="doln"></div>','<td class="wef32f"><a href="([^<]*?)" title="[^<]*?">([^<]*?'+searchString+'[^<]*?)</a>', ['url', 'title', 'description', 'imgUrl'])

# link  do servera
    def getPlaySource(self, url):
        links = {}
        pageData = self.urlhelper.getMatches(url, '<iframe allowTransparency="true" src="(.*?)"', ['id'], True)
        #print "ZALUKAJ::" + pageData.first["id"]
        if pageData.first:
            playerUrl = self.mainUrl + pageData.first["id"]+"&x=1"
            pageData = self.urlhelper.getMatches(playerUrl, 'href="(.*?)"><span>(.*?)</span></a>', ["id","title"])
            if pageData.items:
                for item in pageData.items:
                    pageData = self.urlhelper.getMatches(self.mainUrl + pageData.first["id"]+"&x=1", '<iframe src="(.*?)" width=".*?" height=".*?" frameborder="0" scrolling="no"></iframe>', ["id"], True)
                    links["Wersja " + item["title"]] = pageData.first["id"]
            else:
                 pageData = self.urlhelper.getMatches(playerUrl, '<iframe src="(.*?)" width=".*?" height=".*?" frameborder="0" scrolling="no"></iframe>', ["id"], True)
                 links["Wersja 1"] = pageData.first["id"]
        else:
            pageData = self.urlhelper.getMatches(url, 'bold;" href="(.*?)" target="_blank">Ogladaj', ['id'], True)
            links["Wersja 1"] = pageData.first["id"]
        print "ZALUKAJ::" + str(links)  
        return links