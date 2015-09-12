# -*- coding: utf-8 -*-
import urllib, urllib2, re, os, sys, math
import xbmcgui, xbmc, xbmcaddon, xbmcplugin
from urlparse import urlparse, parse_qs
import urlparser, base64
import json, libCommon2

class frm_filmy_alekinotv():
    def __init__(self):
        self.mainUrl = "http://alekino.tv" 
        self.name = "Alekino"
        self.up = urlparser.urlparser()
        self.color = 'FFeFe690'
        self.displayname = "Ale kino"
        self.urlhelper = libCommon2.urlhelper()
         
    def getPopular(self):
        return self.urlhelper.getMatches3([self.mainUrl + "/filmy?sorting=movie.created&p=1",self.mainUrl + "/filmy?sorting=movie.created&p=2", self.mainUrl + "/filmy?sorting=movie.created&p=3",self.mainUrl + "/filmy?sorting=movie.created&p=4"], '(?P<group>.*)','<div class="pull-left thumb" style="background-image:url\((.*?)\);"><a href="(.*?)">.*?>([^<]*?)</small>', ['imgUrl', 'url', 'title', 'description'])
    
    def search(self, searchString):
       return self.urlhelper.getMatches2(self.mainUrl + '/szukaj?query='+ urllib.quote_plus(searchString), '<!-- Znalezione filmy -->(?P<group>.*?)<!-- Znalezione seriale -->','<img src="(.*?)".*?</a>\s*?<a href="(.*?)" class="en pl-white">(.*?)</a>', ['imgUrl', 'url', 'title', 'description', ])
 
   # server links for video
    def getPlaySource(self, url):
       
        pageData = self.urlhelper.getMatches(self.mainUrl + url, '<div class="player-wrapper" id="player_(.*?)">', ['id'], True)
        links = {}
        for linkFound in pageData.items:
            pageData = self.urlhelper.getMatches(self.mainUrl + "/players/init/" + linkFound["id"] + "?mobile=false", '"data":"(.*?)"', ['id'], True)
            hash = pageData.first["id"].replace('\\','')
            post_data = {'hash': hash}
            pageData = self.urlhelper.getMatches(self.mainUrl + "/players/get", '<iframe.*?src="(.*?)"', ['id'], True, post_data)
            if pageData.first:
             linkVideo = self.up.getVideoLink(pageData.first["id"].decode('utf8'))
             links[self.urlhelper.clearString("Źródło: " + linkFound["id"])] =  linkVideo + '|Referer='+self.mainUrl+'/assets/alekino.tv/swf/player.swf'
        print "LINKS::::" + str(links)
        return links;