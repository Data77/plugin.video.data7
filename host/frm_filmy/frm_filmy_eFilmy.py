# -*- coding: utf-8 -*-
import urllib, urllib2, re, os, sys, math
import xbmcgui, xbmc, xbmcaddon, xbmcplugin
from urlparse import urlparse, parse_qs
import urlparser, base64
import json, libCommon2, base64

class frm_filmy_eFilmy():
    def __init__(self):
        self.mainUrl = "http://www.efilmy.tv/" 
        self.name = "eFilmy"
        self.color = "FeE11680"
        self.up = urlparser.urlparser()
        self.displayname = "eFilmy net"
        self.urlhelper = libCommon2.urlhelper()

# lista z pierwszej strony    
    def getPopular(self):
        #self.mainUrl + "/filmy,p1.html", self.mainUrl + "/filmy,p2.html"
        retValue = self.urlhelper.getMatches3([self.mainUrl + "/filmy,sort-date-DESC.html",self.mainUrl + "/filmy,p1.html" ],'.*',  '<a title="Film ([^<]*?) online" href="([^<]*?)"><img class="poster" src="([^<]*?)" alt="[^<]*?" pagespeed_url_hash=', ['title', 'url', 'imgUrl', 'description'])
        if retValue.items:
            for item in retValue.items:
                item["imgUrl"] = self.mainUrl + item["imgUrl"] 

        return retValue
     
# search - lista z pierwszej strony ( po prawej)    
    def search(self, searchString):
       postdata = {"word" : urllib.quote_plus(searchString) }
       retValue = self.urlhelper.getMatches2(self.mainUrl + '/szukaj.html','.*','<a href="([^<]*?)"><img class="poster" src="([^<]*?)"><a>\s*?<a href="[^<]*?" class="title_pl">([^<]*?)</a>', ['url', 'imgUrl', 'title', 'description'], postdata)
       if retValue.items:
            for item in retValue.items:
                item["imgUrl"] = self.mainUrl + item["imgUrl"] 
       return retValue

# link  do servera
    def getPlaySource(self, url):
        links = {}
        
        pageData = self.urlhelper.getMatches(self.mainUrl + url, 'class="playername"><span>.*?<em>(.*?)</em></span>.*?<em>(.*?)</em></span></div></span>.*?id="play_(.*?)".*?<div id="(.*?)" alt="n" class="embedbg">', ['server', 'version', 'number' ,'id'])
       # print "EFILMY::::" + str(pageData.first)
        for item in pageData.items:
        #    print "EFILMY222::::" + str(item["id"])
            playerUrl = self.mainUrl + "seriale.php?cmd=show_player&id=" + item["id"]
            pageData = self.urlhelper.getMatches(playerUrl, 'document.write\(Base64.decode\("(.*?)"\)', ["id"], True)
         #   print "EFILMY23232::::" + str(pageData.first)
           
            if pageData.first:
                iframe = base64.b64decode(pageData.first["id"])
          #      print "EFILMY333::::" + str(iframe)
            
                mylink = re.compile('<IFRAME.*?SRC="(.*?)"',re.DOTALL | re.IGNORECASE).findall(iframe)
                #print "EFILMY444::::" + str(mylink)
                if "efilmy" in mylink[0]:
                    pageData = self.urlhelper.getMatches(mylink[0], ' <div id="playerVidzer">.*?<a href="(.*?)" .*?</a>', ["id"], True)
                    if pageData.first:
                        mylink[0] = pageData.first["id"]  
                
                if not item["server"]:
                    item["server"] = "Podstawowy"
                    item["number"]  = "1"
                    item["version"]  = "nieznana"
                
                links[item["server"] + " - " + item["version"]] = mylink[0]
           
        if len(links) == 0:
            d = xbmcgui.Dialog()
            d.ok('Błąd przy przetwarzaniu.', 'Problem. Wejdź na dowolny film/serial na  ' + self.mainUrl + ' i wpisz captcha !')
        #print "

        return links