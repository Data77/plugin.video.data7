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
import base64
import _random
import random

class frm_seriale_eFilmy():
    def __init__(self):
        self.mainUrl = "http://www.efilmy.tv/" 
        self.name = "eFilmy"
        self.color = "BBF156A0"
        self.up = urlparser.urlparser()
        self.displayname = "eFilmy net"
        self.urlhelper = libCommon2.urlhelper()

# lista z pierwszej strony
    def getPopular(self):
        retValue = self.urlhelper.getMatches2(self.mainUrl + "/seriale.html",'<div class="prawo-kontener">(?P<group>.*?)<div class="pagin">',  '<a class="overimage" href="(.*?).html">(.*?)</a>.*?class="sposter" src="(.*?)" pagespeed_url_hash', ['url','title','imgUrl', 'description'])
        if retValue.items:
            for item in retValue.items:
                item["url"] = self.mainUrl + item["url"] + ".html"
                item["imgUrl"] = self.mainUrl + item["imgUrl"] 

        return retValue

# lista odcinków - jeden request per sezon
    def getEpisodes(self, url):
        print "URLS:::" + url
        array = self.urlhelper.getMatches(url,'<li><a title=".*?" href="([^<]*?)">([^<]*?) <span class="bold">([^<]*?)</span>', ['url','number','title','description'])
        #print "TEST:::" + str(array.items)
        array.items = array.items

        return array    

    def getAlphabetic(self, letters):
        letters = letters.lower()
        retValue = self.urlhelper.getMatches(self.mainUrl + '/js/menu.js','var serials_pl =\[(.*?)\];\s*?var serials_seo =\[(.*?)\];', ['titles', 'links'])
        titles = str(retValue.items[0]["titles"]).split('",')        
        links = str(retValue.items[0]["links"]).split('",')
        items = []
        for i in range(len(titles)):
            #print "EFIL:::" + titles[i].lstrip().replace(" ","").lower()[1] +
            #"|| LETT:" + letters
            if titles[i].lstrip().replace(" ","").lower()[1] in letters:
                items.append({"url":self.mainUrl + "serial," + links[i].lstrip('"') + ".html", "title" : titles[i].lstrip('"'), "description" : "", "imgUrl" : "" })
        retValue.items = items
        return retValue


# search - lista z pierwszej strony ( po prawej)
    def search(self, searchString):
        searchString = urllib.quote_plus(searchString).lower() 
        retValue = self.urlhelper.getMatches(self.mainUrl + '/js/menu.js','var serials_pl =\[(.*?)\];\s*?var serials_seo =\[(.*?)\];', ['titles', 'links'])
        titles = str(retValue.items[0]["titles"]).split('",')        
        links = str(retValue.items[0]["links"]).split('",')
        items = []
        for i in range(len(titles)):
            if searchString in titles[i].lower():
               items.append({"url":self.mainUrl + "serial," + links[i].lstrip('"') + ".html", "title" : titles[i].lstrip('"'), "description" : "", "imgUrl" : "" })
        retValue.items = items
        return retValue

# link do servera
    def getPlaySource(self, url):
       
        links = {}
        
        pageData = self.urlhelper.getMatches(self.mainUrl + url, 'class="playername"><span>.*?<em>(.*?)</em></span>.*?<em>(.*?)</em></span></div></span>.*?id="play_(.*?)".*?<div id="(.*?)" alt="n" class="embedbg">', ['server', 'version', 'number' ,'id'])
        
        for item in pageData.items:
            playerUrl = self.mainUrl + "seriale.php?cmd=show_player&id=" + item["id"]
            pageData = self.urlhelper.getMatches(playerUrl, 'document.write\(Base64.decode\("(.*?)"\)', ["id"], True)
           
            if pageData.first:
                iframe = base64.b64decode(pageData.first["id"])
            
                mylink = re.compile('<IFRAME.*?SRC="(.*?)"',re.DOTALL | re.IGNORECASE).findall(iframe)
                
                if not item["server"]:
                    item["server"] = "Podstawowy"
                    item["number"] = "1"
                    item["version"] = "nieznana"
                
                links[item["server"] + " - " + item["version"]] = mylink[0]
            #Captcha
            else:
                id = item["id"][:-2]
                mode = 's'
                captcha = self.urlhelper.get_captcha("http://www.efilmy.tv/mirrory.php?cmd=generate_captcha&" + str(random.random()))

                if captcha:
                    postdata = {"captcha":captcha, "id" : id, "mode" : mode}
                    referer = playerUrl
                    self.urlhelper.getMatches("http://www.efilmy.tv/mirrory.php?cmd=check_captcha", '(.*?)', ["id"], False, postdata, None, referer)
                    self.getPlaySource(url)
                return links;
                 
        if len(links) == 0:

            d = xbmcgui.Dialog()
            d.ok('Błąd przy przetwarzaniu.', 'Problem. Wejdź na dowolny film/serial na  ' + self.mainUrl + ' i wpisz captcha !')
       

             
        print "EFILMY:::LINKS::" + str(links)

        return links