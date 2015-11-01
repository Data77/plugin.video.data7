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
import HTMLParser
import urlparser

import base64
import settings
import Parser
import json
import pickle
import Queue
from threading import Thread
from time import sleep
#from multiprocessing.pool import ThreadPool
try:
   import StorageServer
except:
   import storageserverdummy as StorageServer

scriptID = 'plugin.video.data7'

ptv = xbmcaddon.Addon(scriptID)

BASE_RESOURCE_PATH = os.path.join(ptv.getAddonInfo('path'), "../resources")
sys.path.append(os.path.join(BASE_RESOURCE_PATH, "lib"))

class frm_filmy():
    def __init__(self):
        self.settings = settings.TVSettings()
        self.parser = Parser.Parser()
        self.up = urlparser.urlparser()
        #self.cm = data7_pCommon.common()
        #self.pl = data7_Player.data7_Player()
        self.refl = libCommon2.reflectionHelper()
        self.hp = HTMLParser.HTMLParser()
        self.cache = StorageServer.StorageServer("xbmc.plugin.vine.frm_filmy", 1)
        self.cache.table_name = "xbmc.plugin.vine.frm_filmy"
        self.urlhelper = libCommon2.urlhelper()
        self.instances = {}
        self.load_series()
        self.searchResult = []
        self.queue = Queue.LifoQueue()
        
    def load_series(self):
        path = os.path.join(os.path.dirname(__file__), "frm_filmy")
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

# Start
    def handleService(self):
        params = self.parser.getParams()
        print("url : ", params)
        clicked_item_type = self.parser.getParam(params, "item_type")
        
        #name: {"main-menu-item", "episode-item", "source-server-item"}
        if clicked_item_type == None: #MAIN MENU
            self.addMainMenu(params)
        elif clicked_item_type == "main-menu-item":
            self.addSourcesOrPlay(params)
        elif clicked_item_type == "source-server-item":
            self.playItem(params)
        elif clicked_item_type == "main-menu-search-item":
            self.search(params)

# Compose main menu (popular episodes and search)
    def addMainMenu(self,params):
        self.add('main-menu-search-item','category', '', '[COLOR white]Szukaj...[/COLOR]' , 'icon' , "url", 'None', 'None', True, False)

        # queue
        self.queue = Queue.LifoQueue()

        for serviceName in self.instances:
            try:
            #self.queue.put(serviceName)
                self.getPopularA(serviceName)
            except:
                continue
        #tasksCount = len(self.instances)
        
        #for i in range(tasksCount * 2): # aka number of threadtex
            #t = Thread(target = self.getPopularAsync) # target is the above function
            #t.daemon = True
            #t.start() # start the thread

        #self.queue.join()    
        sorted(self.searchResult, key = lambda r: (r['serviceName']))
        color = 'FFeFe690'
                
        if self.searchResult:   
            for serviceResult in self.searchResult:
                if self.instances[serviceResult["serviceName"]].color:
                    color = self.instances[serviceResult["serviceName"]].color
                for item in serviceResult["result"]:
                    self.add("main-menu-item", serviceResult["serviceName"] , self.urlhelper.clearString(item["title"]), '[COLOR=' + color + '](' + self.instances[serviceResult["serviceName"]].displayname + ')[/COLOR] ' + self.urlhelper.clearString(item["title"]), item["imgUrl"] , item["url"], "")
                
            
        xbmcplugin.endOfDirectory(int(sys.argv[1])) 
      
    def getPopularAsync(self):
        if not self.queue.empty():
            serviceName = self.queue.get()
            if 1 == 1:
            #try:
                instance = self.instances[serviceName] 
                foundItems = instance.getPopular()  
                self.searchResult.append({'serviceName': serviceName, 'result':foundItems.items})
            #except Exception as e:
            #    print e
            self.queue.task_done()

    def getPopularA(self, serviceName):
            instance = self.instances[serviceName] 
            foundItems = instance.getPopular()  
            self.searchResult.append({'serviceName': serviceName, 'result':foundItems.items})
            
                     
# play or list sources (lista żródeł - serwerów, jesłi jeden rozpocznij
# odtwarzenie)
    def addSourcesOrPlay(self,params):
        instance = self.instances[params['category']]
        videoUrls = instance.getPlaySource(urllib.unquote(params['url']))
        print "URLS::" + str(videoUrls)
        if len(videoUrls) == 1:
            self.playItem(params,videoUrls.itervalues().next())
        else:
            for key in videoUrls:
                print "URLS::: " + str(key) + " *** " + str(videoUrls[key])
                self.add("source-server-item", urllib.unquote(params['category']), urllib.unquote(params['series_title'] + ' - ' + params['title']), key, urllib.unquote(params['icon']), videoUrls[key])
       
                xbmcplugin.endOfDirectory(int(sys.argv[1])) 
        
 # play
    def playItem(self,params,videoUrl=''):
        if videoUrl:
            self.LOAD_AND_PLAY_VIDEO(videoUrl, urllib.unquote(params['title']), urllib.unquote(params['icon']))
        else:
            self.LOAD_AND_PLAY_VIDEO(urllib.unquote(params['url']), urllib.unquote(params['title']), urllib.unquote(params['icon']))

# Search
    def search(self,params):
        text = None
        self.searchResult = []
        k = xbmc.Keyboard()
        k.doModal()
        if (k.isConfirmed()):
            text = urllib.quote_plus(k.getText())
        
        if text:
            # queue
            self.queue = Queue.LifoQueue()

            for serviceName in self.instances:
                self.queue.put(serviceName)
            
            tasksCount = len(self.instances)
       
            for i in range(tasksCount): # aka number of threadtex
                t = Thread(target = self.searchAsync,args=(text,)) # target is the above function
                t.daemon = True
                #print "BEFORE:::" + str(i)
                t.start() # start the thread
                #print "AFTER:::" + str(i)

            #print "LOOPENDED:::"

            self.queue.join()    
            
            color = 'FFeFe690'
                
            if self.searchResult:   
                for serviceResult in self.searchResult:
                    if self.instances[serviceResult["serviceName"]].color:
                        color = self.instances[serviceResult["serviceName"]].color
                    for item in serviceResult["result"]:
                        self.add("main-menu-item", serviceResult["serviceName"] , self.urlhelper.clearString(item["title"]), '[COLOR=' + color + '](' + self.instances[serviceResult["serviceName"]].displayname + ')[/COLOR] ' + self.urlhelper.clearString(item["title"]), item["imgUrl"] , item["url"], item["description"])  

        xbmcplugin.endOfDirectory(int(sys.argv[1])) 
    
    def searchAsync(self, text):
        while not self.queue.empty():
            serviceName = self.queue.get()
            try:
                instance = self.instances[serviceName] 
                foundItems = instance.search(text)  
                self.searchResult.append({'serviceName': serviceName, 'result':foundItems.items})
            except Exception as e:
                print e
            self.queue.task_done()

                         
# Add item to list
    def add(self, item_type, category, series_title ,title, iconimage, url, desc="", rating="", folder=True, isPlayable=True, strona='', filtrowanie=''):
        service = "frm_filmy"
        title = title.replace("|","-")
        if not iconimage:
            iconimage = "#"
        u = sys.argv[0] + "?service=" + service + "&series_title=" + urllib.quote_plus(series_title) + "&item_type=" + item_type + "&category=" + category + "&title=" + title + "&url=" + urllib.quote_plus(url) + "&icon=" + urllib.quote_plus(iconimage) + "&strona=" + urllib.quote_plus(strona) + "&filtrowanie=" + urllib.quote_plus(filtrowanie)
        #log.info(str(u))
        if iconimage == '':
            iconimage = "DefaultVideo.png"
        liz = xbmcgui.ListItem(title, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
        if isPlayable:
            liz.setProperty("IsPlayable", "true")
        liz.setInfo(type="Video", infoLabels={ "Title": title, "Description" : desc })
        #print 'ADD: "' + title + '"'
        xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=folder)

# play video
    def LOAD_AND_PLAY_VIDEO(self, videoUrl, title, icon):
        ok = True
        print "@@@@URL FOUND: " + str(videoUrl)
        
        videoUrl = self.up.getVideoLink(videoUrl) 
        
        print "@@@@VIDEO LINK FOUND: " + str(videoUrl)
        
        if videoUrl == '':
                d = xbmcgui.Dialog()
                d.ok('Nie znaleziono streamingu.', 'Może to chwilowa awaria.', 'Spróbuj ponownie za jakiś czas')
                return False
        liz = xbmcgui.ListItem(title, iconImage=icon, thumbnailImage=icon)
        liz.setInfo(type = "Video", infoLabels={ "Title": title, })
        try:
            xbmcPlayer = xbmc.Player()
            xbmcPlayer.play(videoUrl, liz)
            
            if not xbmc.Player().isPlaying():
                xbmc.sleep(1000)
                #xbmcPlayer.play(url, liz)
            
        except:
            d = xbmcgui.Dialog()
            d.ok('Błąd przy przetwarzaniu.', 'Problem')        
        return ok
