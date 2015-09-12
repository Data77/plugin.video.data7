# -*- coding: utf-8 -*-
import urllib, urllib2, re, sys, xbmcplugin, xbmcgui
import cookielib, os, string, cookielib, StringIO
import os, time, base64, logging, calendar
import xbmcaddon

scriptID = 'plugin.video.data7'
scriptname = "Films online"
ptv = xbmcaddon.Addon(scriptID)
print("scripid",ptv)


BASE_RESOURCE_PATH = os.path.join( ptv.getAddonInfo('path'), "resources" )
sys.path.append( os.path.join( BASE_RESOURCE_PATH, "lib" ) )
sys.path.append( os.path.join( ptv.getAddonInfo('path'), "host" ) )

import frm_seriale,frm_filmy
import Parser
        

class data7Films:
    def __init__(self):
        BASE_RESOURCE_PATH = os.path.join( ptv.getAddonInfo('path'), "resources" )
        sys.path.append( os.path.join( BASE_RESOURCE_PATH, "lib" ) )
        sys.path.append( os.path.join( ptv.getAddonInfo('path'), "host" ) )
        #self.settings = settings.TVSettings()
        self.parser = Parser.Parser()

    def showListOptions(self):
        params = self.parser.getParams()
        mode = self.parser.getIntParam(params, "mode")
        name = self.parser.getParam(params, "name")
        service = self.parser.getParam(params, 'service')
        if mode == None and name == None and service == None:
            self.CATEGORIES()

        elif mode == 8200 or service == 'frm_seriale':
            tv = frm_seriale.frm_seriale()
            tv.handleService()			
        
        elif mode == 7110 or service == 'frm_filmy':
            tv = frm_filmy.frm_filmy()
            tv.handleService()

        #elif mode == 20:
        #    self.settings.showSettings()

    def CATEGORIES(self):
        self.addDir("[COLOR white]Filmy[/COLOR]", 7110, False, 'Filmy', False)
        self.addDir("[COLOR white]Seriale[/COLOR]", 8200, False, 'Seriale', False)
        #self.addDir('Ustawienia', 20, True, 'Ustawienia', False)
        xbmcplugin.endOfDirectory(int(sys.argv[1]))

    def listsTable(self, table):
        for num, val in table.items():
            nTab.append(val)
        return nTab


    def addDir(self, name, mode, autoplay, icon, isPlayable = True):
        u=sys.argv[0] + "?mode=" + str(mode)
        if icon != False:
          icon = os.path.join(ptv.getAddonInfo('path'), "images/") + icon + '.png'
        else:
          icon = "DefaultVideoPlaylists.png"
        liz=xbmcgui.ListItem(name, iconImage=icon, thumbnailImage='')
        if autoplay and isPlayable:
          liz.setProperty("IsPlayable", "true")
        liz.setInfo( type="Video", infoLabels={ "Title": name } )
        xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u,listitem=liz, isFolder= not autoplay)

init = data7Films()
init.showListOptions()
