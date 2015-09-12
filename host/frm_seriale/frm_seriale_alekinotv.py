# -*- coding: utf-8 -*-
import urllib, urllib2, re, os, sys, math
import xbmcgui, xbmc, xbmcaddon, xbmcplugin
from urlparse import urlparse, parse_qs
import urlparser, base64
import json, libCommon2

class frm_seriale_alekinotv():
    def __init__(self):
        self.mainUrl = "http://alekino.tv" 
        self.name = "Alekino"
        self.up = urlparser.urlparser()
        self.color = ''
        self.displayname = "Ale kino"
        self.urlhelper = libCommon2.urlhelper()
         
    def getPopular(self):
        #http://alekino.tv/m/serieslast
         array =  self.urlhelper.getMatches2(self.mainUrl + "/seriale-online", '<!-- popularne dzisiaj -->(.*?)<!-- /ostatnio dodane odcinki -->','<td class="title" .*?tyle="width:200px;"><a href="(.*?)">(.*?)</a></td>', ['url', 'title','imgUrl', 'description'])
        
         #return self.urlhelper.getMatches2(self.mainUrl + "/seriale-online", '<div class="box-new-line">.*?padding-left.*?<ul class="inline">(?P<group>.*?)</div>\s*?<div class="p10">\s*?</div>','<img.*?src="(?P<imgUrl>.*?)" alt=.*?</a>\s*?<a href="(?P<url>.*?)" data-toggle="tooltip" title=""  class="pl" style=".*?">(?P<title>.*?)<br />', ['imgUrl', 'url', 'title', 'description'])
         # make unique
         array.items = dict((v['url'],v) for v in array.items).values()
         return array


    
    def getEpisodes(self, url):
        print self.mainUrl + url
        array = self.urlhelper.getMatches(self.mainUrl + url, '<span class="w">(.*?)</span>\s*?</td>\s*?<td class="episode">\s*?<a class="o" href="(.*?)">(.*?)</a>', ['number', 'url', 'title', 'description'])
        array.items = reversed(array.items)
        return array    

    def getAlphabetic(self, letters):
        searchString = '['+ "|".join(letters) + ']' 
        array = self.urlhelper.getMatches2(self.mainUrl + "/seriale-online" ,'<div class="offset1 span10 std-module std-serials-letter" id="letter_'+ searchString+'">(.*?)</div>', '<a href="\s*(.*?)" class="pl-corners">(<span class="label label-important">NOWE</span>|)(.*?)(<span class=".*?">.*?|)</span></a>', ['url','#ignore' ,'title','#ignore','imgUrl' ,'description'])
        return array    

    def search(self, searchString):
       return self.urlhelper.getMatches2(self.mainUrl + '/szukaj?query='+ urllib.quote_plus(searchString), '<!-- Znalezione seriale -->(?P<group>.*?)<!-- /Znalezione seriale -->','<img src="(.*?)".*?</a>\s*?<a href="(.*?)" class="en pl-white">(.*?)</a>', ['imgUrl', 'url', 'title', 'description', ])
 
   # server links for video
    def getPlaySource(self, url):
        pageData = self.urlhelper.getMatches(self.mainUrl + url, '<h1 class="movie-title"><a href=".*?">.*?</a><br/>\s*?(.*?)\s*?</h1>.*?<a href="#" data-type="player" data-version="standard" data-id="(.*?)">', ['title','id'], False)
        links = {}
        for linkFound in pageData.items:
            pageData = self.urlhelper.getMatches(self.mainUrl + "/players/init/" + linkFound["id"] + "?mobile=false", '"data":"(.*?)"', ['id'], True)

            hash = pageData.first["id"].replace('\\','')
            post_data = {'hash': hash}
            pageData = self.urlhelper.getMatches(self.mainUrl + "/players/get", '<iframe src="(.*?)"', ['id'], True, post_data)
            if pageData.first:
             linkVideo = self.up.getVideoLink(pageData.first["id"].decode('utf8'))
             links[self.urlhelper.clearString(linkFound["title"])] =  linkVideo + '|Referer='+self.mainUrl+'/assets/alekino.tv/swf/player.swf'
        print "LINKS::::" + str(links)
        return links;