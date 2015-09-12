# -*- coding: utf-8 -*-
import urllib, urllib2, re, os, sys, math
import xbmcgui, xbmc, xbmcaddon, xbmcplugin
from urlparse import urlparse, parse_qs
import urlparser, base64
import json, libCommon2, base64

class frm_seriale_eFilmy():
    def __init__(self):
        self.mainUrl = "http://www.efilmy.net/" 
        self.name = "eFilmy"
        self.color = "FeE11680"
        self.up = urlparser.urlparser()
        self.displayname = "eFilmy net"
        self.urlhelper = libCommon2.urlhelper()

# lista z pierwszej strony    
    def getPopular(self):
        retValue = self.urlhelper.getMatches2(self.mainUrl + "/seriale.html",'<div class="prawo-kontener">(?P<group>.*?)<div class="pagin">',  '<a class="overimage" href="(.*?).html">(.*?)</a>.*?class="sposter" src="(.*?)" pagespeed_url_hash', ['url','title','imgUrl', 'description'])
        if retValue.items:
            for item in retValue.items:
                item["url"] = self.mainUrl + item["url"]+ ".html"
                item["imgUrl"] = self.mainUrl + item["imgUrl"] 

        return retValue

# lista odcinków - jeden request per sezon    
    def getEpisodes(self, url):
        print "URLS:::" + url
        array = self.urlhelper.getMatches(url,'<li><a title=".*?" href="([^<]*?)">([^<]*?) <span class="bold">([^<]*?)</span>', ['url','number','title','description'])
        print "TEST:::" + str(array.items)
        array.items = reversed(array.items)

        return array    

    def getAlphabetic(self, letters):
        letters = letters.lower()
        retValue = self.urlhelper.getMatches(self.mainUrl + '/js/menu.js','var serials_pl =\[(.*?)\];\s*?var serials_seo =\[(.*?)\];', ['titles', 'links'])
        titles = str(retValue.items[0]["titles"]).split('",')        
        links = str(retValue.items[0]["links"]).split('",')
        items = []
        for i in range(len(titles)):
            #print "EFIL:::" + titles[i].lstrip().replace(" ","").lower()[1] + "|| LETT:" + letters
            if titles[i].lstrip().replace(" ","").lower()[1] in letters:
                items.append({"url":self.mainUrl+"serial,"+links[i].lstrip('"') + ".html", "title" : titles[i].lstrip('"'), "description" : "", "imgUrl" : "" } )
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
               items.append({"url":self.mainUrl+"serial,"+links[i].lstrip('"') + ".html", "title" : titles[i].lstrip('"'), "description" : "", "imgUrl" : "" } )
        retValue.items = items
        return retValue

# link  do servera
    def getPlaySource(self, url):
        links = {}
        pageData = self.urlhelper.getMatches(self.mainUrl + url, '<input class="blue" alt="(.*?)"(.*?<span id="(.*?)" class="playername">(.*?)<img class="shme"|)', ['id','ignore','number','server'])
        #print "EFILMY::::" + str(pageData.first)
        for item in pageData.items:
            #print "EFILMY222::::" + str(item["id"])
            playerUrl = self.mainUrl + "seriale.php?cmd=show_player&id=" + item["id"]
            pageData = self.urlhelper.getMatches(playerUrl, 'document.write\(Base64.decode\("(.*?)"\)', ["id"], True)
            #print "EFILMY23232::::" + str(pageData.first)
           
            if pageData.first:
                iframe = base64.b64decode(pageData.first["id"])
                #print "EFILMY333::::" + str(iframe)
            
                mylink = re.compile('<IFRAME.*?SRC="(.*?)"',re.DOTALL | re.IGNORECASE).findall(iframe)
                #print "EFILMY444::::" + str(mylink)
            
                if not item["server"]:
                    item["server"] = "Podstawowy"
                links[item["server"] + "(" + item["number"] + ")"] = mylink[0]
            else:
                d = xbmcgui.Dialog()
                d.ok('Błąd przy przetwarzaniu.', 'Problem. Wejdź na dowolny film/serial na  ' + self.mainUrl + ' i wpisz captcha !')
        #print "LINKSSS::: " +  str(links)
        return links