# -*- coding: utf-8 -*-
import urllib
import urllib2
import re
import os
import sys
import math
import pkgutil
import xbmcgui
import xbmc
import xbmcaddon
import xbmcplugin
import libCommon2
from urlparse import urlparse, parse_qs
import HTMLParser
import urlparser
import operator

import urlparser
import base64
import  settings
import UParser 
import json
import pickle
import traceback
import sys

try:
   import StorageServer
except:
   import storageserverdummy as StorageServer

scriptID = 'plugin.video.data7'

ptv = xbmcaddon.Addon(scriptID)

BASE_RESOURCE_PATH = os.path.join(ptv.getAddonInfo('path'), "../resources")
sys.path.append(os.path.join(BASE_RESOURCE_PATH, "lib"))



class frm_seriale():
    def __init__(self):
        self.settings = settings.TVSettings()
        self.parser = UParser.UParser()
        self.up = urlparser.urlparser()
        #self.cm = data7_pCommon.common()
        #self.pl = data7_Player.data7_Player()
        self.refl = libCommon2.reflectionHelper()
        self.hp = HTMLParser.HTMLParser()
        self.cache = StorageServer.StorageServer("xbmc.plugin.vine.frm_seriale", 1)
        self.cache.table_name = "xbmc.plugin.vine.frm_seriale"
        self.urlhelper = libCommon2.urlhelper()
        self.instances = {}
        self.load_series()

    def load_series(self):
        path = os.path.join(os.path.dirname(__file__), "frm_seriale")
        sys.path.append(path)
        modules = pkgutil.iter_modules(path=[path])
        for loader, mod_name, ispkg in modules: 
            if mod_name not in sys.modules:
                # Import module
                #loaded_mod = __import__(path+"."+mod_name,
                #fromlist=[mod_name])
                loaded_mod = __import__(mod_name)
                # Load class from imported module
                class_name = self.refl.get_class_name(mod_name)
                loaded_class = getattr(loaded_mod, class_name)
                # Create an instance of the class
                instance = loaded_class()
                self.instances[instance.name] = instance
                print("LOADING-MODULE::" + str(instance.name))

# Start
    def handleService(self):
        params = self.parser.getParams()
        print("url : ", params)
        clicked_item_type = self.parser.getParam(params, "item_type")
        
        #name: {"main-menu-item", "episode-item", "source-server-item"}
        if clicked_item_type == None: #MAIN MENU
            self.addMainMenu(params)
        elif clicked_item_type == "main-menu-item":
            self.addEpisodes(params)
        elif clicked_item_type == "episodes-item":
            self.addSourcesOrPlay(params)
        elif clicked_item_type == "source-server-item":
            self.playItem(params)
        elif clicked_item_type == "main-menu-search-item":
            self.search(params)
        elif clicked_item_type == "main-menu-alphabetic-item":
            self.addAlphabetic(params)

# Compose main menu (popular episodes and search)
    def addMainMenu(self,params):
        self.add('main-menu-search-item','category', '', '[COLOR white]Szukaj...[/COLOR]' , "" , "", "", "", True, False)
        self.add('main-menu-alphabetic-item','category', '', '[COLOR white]Alfabetycznie...[/COLOR]' , "" , "", "", "", True, False)
        self.add('main-menu-history-item','category', '', '[COLOR gray]Historia...[/COLOR]' , "" , "", "", "", True, False)
      
        elements = []
        for serviceName in self.instances:
            #if 1 == 1:
            try:
                newItems = []
                retValue = self.instances[serviceName].getPopular()
                newItems = retValue.items
            except:
                continue
            color = 'FFeFe690'
            
            if self.instances[serviceName].color:
                color = self.instances[serviceName].color
            for item in sorted(newItems, key=operator.itemgetter("title")):
                self.add("main-menu-item", serviceName , self.urlhelper.clearString(item["title"]), '[COLOR=' + color + '](' + self.instances[serviceName].displayname + ')[/COLOR] ' + self.urlhelper.clearString(item["title"]), item["imgUrl"] , item["url"], item["description"])
                
            
        xbmcplugin.endOfDirectory(int(sys.argv[1])) 
    
# Episode list (lista odcinków dla serialu)
    def addEpisodes(self,params):
        instance = self.instances[params['category']]
        episodes = instance.getEpisodes(urllib.unquote(params['url']))
        
        for item in episodes.items:
            self.add("episodes-item", instance.name , urllib.unquote(params['series_title']),'[COLOR white]' + item["number"] + '[/COLOR] ' + self.urlhelper.clearString(item["title"]), urllib.unquote(params['icon']) , item["url"], item["description"])
       
        xbmcplugin.endOfDirectory(int(sys.argv[1])) 

# PREPARE ALPHABETIC LIST    
    def addAlphabetic(self,params):
        if not "url" in params:
            for al in ['#','AB','CD','EF','GH','IJ','KL','MN','OP','RS','TU','WX','YZ']:
                 self.add("main-menu-alphabetic-item", '' , "",'[COLOR white]' + al + '[/COLOR] ' , '' , al.replace("#","1234567890 "), '')
        else:
          for serviceName in self.instances:
                instance = self.instances[serviceName]
                try:
                    newItems = instance.getAlphabetic(urllib.unquote(params['url']))
                except:
                    pass
                color = 'FFeFe690'
            
                if self.instances[serviceName].color:
                    color = self.instances[serviceName].color

                for item in sorted(newItems.items, key=operator.itemgetter("title")):
                    self.add("main-menu-item", serviceName , self.hp.unescape(self.urlhelper.clearString(item["title"])), '[COLOR=' + color + '](' + self.instances[serviceName].displayname + ')[/COLOR] ' + self.urlhelper.clearString(item["title"]), item["imgUrl"] , item["url"], item["description"])

        xbmcplugin.endOfDirectory(int(sys.argv[1])) 
                              
# play or list sources (lista żródeł - serwerów, jesli jeden rozpocznij odtwarzenie)
    def addSourcesOrPlay(self,params):
        instance = self.instances[params['category']]
        videoUrls = instance.getPlaySource(urllib.unquote(params['url']))
        #print "###videoUrls##"+ str(videoUrls)
        if len(videoUrls) == 1:
            self.playItem(params,videoUrls.itervalues().next())
        else:
            for key in sorted(videoUrls):
                self.add("source-server-item", urllib.unquote(params['category']), urllib.unquote(params['series_title'] + ' - ' + params['title']), key, urllib.unquote(params['icon']), videoUrls[key])
       
            xbmcplugin.endOfDirectory(int(sys.argv[1])) 
        
 # play   
    def playItem(self,params,videoUrl=''):
        if videoUrl:
            self.LOAD_AND_PLAY_VIDEO(videoUrl, urllib.unquote(params['series_title'] + ' - ' + params['title']), urllib.unquote(params['icon']))
        else:
            self.LOAD_AND_PLAY_VIDEO(urllib.unquote(params['url']), urllib.unquote(params['series_title']), urllib.unquote(params['icon']))

# Search
    def search(self,params):
        
        searchString=''

        if params.has_key("filtrowanie"):
            searchString = params["filtrowanie"]

        if not searchString:
            params["filtrowanie"] = []
            k = xbmc.Keyboard()
            k.doModal()
            if (k.isConfirmed()):
                searchString= urllib.quote_plus(k.getText())
        
        if searchString:
            self.add("main-menu-search-item", '' , '', 'Szukaj: [COLOR=white]\'' + searchString +'\'[/COLOR]','' ,'', '','',True,True,'',searchString)  

            for serviceName in self.instances:
                #try:
                instance = self.instances[serviceName] 
                foundItems = instance.search(searchString)  
                #except Exception as e:
                #    print serviceName + ".Search: " + str(e) + " :: " + traceback.format_exc()
                #    continue

                color = 'FFeFe690'
                
                if self.instances[serviceName].color:
                    color = self.instances[serviceName].color
                
                if foundItems and foundItems.items:   
                    for item in sorted(foundItems.items, key=operator.itemgetter("title")):
                        self.add("main-menu-item", serviceName , self.urlhelper.clearString(item["title"]), '[COLOR=' + color + '](' + self.instances[serviceName].displayname + ')[/COLOR] ' + self.urlhelper.clearString(item["title"]), item["imgUrl"] , item["url"], item["description"])  

        xbmcplugin.endOfDirectory(int(sys.argv[1])) 


# Add item to list
    def add(self, item_type, category, series_title ,title, iconimage, url, desc="", rating="", folder=True, isPlayable=True, strona='', filtrowanie=''):
        service = "frm_seriale"
        if not iconimage:
            iconimage = "#"
        u = sys.argv[0] + "?service=" + service + "&series_title=" + urllib.quote_plus(series_title) + "&item_type=" + item_type + "&category=" + category + "&title=" + title + "&url=" + urllib.quote_plus(url) + "&icon=" + urllib.quote_plus(iconimage) + "&strona=" + urllib.quote_plus(strona) + "&filtrowanie=" + urllib.quote_plus(filtrowanie)
        #log.info(str(u))
        if iconimage == '':
            iconimage = "DefaultVideo.png"
        liz = xbmcgui.ListItem(title, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
        if isPlayable:
            liz.setProperty("IsPlayable", "true")
        liz.setInfo(type="Video", infoLabels={ "Title": title })
        #print 'ADD: "' + title + '"'
        xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=folder)

# play video
    def LOAD_AND_PLAY_VIDEO(self, videoUrl, title, icon):
        ok = True
        result = self.up.getVideoLink(videoUrl) 
        
        videoUrl = result["video"]
        subUrl = result["subtitles"]
        
        if videoUrl == '':
                d = xbmcgui.Dialog()
                d.ok('Nie znaleziono streamingu.', 'Może to chwilowa awaria.', 'Spróbuj ponownie za jakiś czas')
                return False
        liz = xbmcgui.ListItem(label=title, iconImage=icon, thumbnailImage=icon)
        liz.setInfo(type = "video", infoLabels={ "Title": title,"Label":title })
        try:
            xbmcPlayer = xbmc.Player()
            xbmcPlayer.play(videoUrl, liz)
            xbmc.sleep(500)

            if not xbmc.Player().isPlaying():
                xbmc.sleep(1000)
                xbmcPlayer.setSubtitles(title)
                xbmcPlayer.play(videoUrl, liz)
            
            if subUrl:
                xbmc.sleep(10000)
                xbmcPlayer.setSubtitles(subUrl)

        except:
            d = xbmcgui.Dialog()
            d.ok('Błąd przy przetwarzaniu.', 'Problem')        
        return ok
