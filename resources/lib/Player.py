# -*- coding: utf-8 -*-
import re, sys, os, cgi
import urllib, urllib2
import xbmcgui,xbmc

scriptID = sys.modules[ "__main__" ].scriptID
scriptname = "data7 Polish films online"

class Player:
    def __init__(self):
        pass
    
    def LOAD_AND_PLAY_VIDEO(self, videoUrl, title, icon, year='',plot='', referer=''):
    	if videoUrl == '':
            d = xbmcgui.Dialog()
            d.ok('Nie znaleziono streamingu')
            return False
        print ("Playing:",title, icon,year,plot)
        try:
            if icon == '' or  icon == 'None':
                icon = "DefaultVideo.png"
            liz=xbmcgui.ListItem(title, iconImage=icon, thumbnailImage=icon)
            if year == '':
                liz.setInfo( type="video", infoLabels={ "Title": title} )
            else:
                liz.setInfo( type="video", infoLabels={ "Title": title, "Plot": plot, "Year": int(year) } )
            xbmcPlayer = xbmc.Player()
            xbmcPlayer.play(videoUrl, liz)
        except:
            d = xbmcgui.Dialog()
            if pType=="video":
                d.ok('Wyst?pi? b??d!', 'B??d przy przetwarzaniu, lub wyczerpany limit czasowy ogl?dania.', 'Zarejestruj si? i op?a? abonament.', 'Aby ogl?da? za darmo spr?buj ponownie za jaki? czas.')
            elif pType=="music":
                d.ok('Wyst?pi? b??d!', 'B??d przy przetwarzaniu.', 'Aby wys?ucha? spr?buj ponownie za jaki? czas.')
            return False
        return True
        