#!/bin/python
# radioman - wrapperinterface for internet radio stations
# Copyright (C) 2009 Markus Zeindl <mrszndl@googlemail.com>

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by 
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version. 

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details. 

# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.


# Invocation: radioman


# TODO:
#  - opportunity for adding web radio
#  - viewing available stations
#  - deletion of stations
#  - selection of stations

import os
import sys

stationsdir = "stations"
ogg_play = "/usr/bin/ogg123"
mpg_play = "/usr/bin/mpg123"

players = [ ogg_play, mpg_play ]

def play(url):
    # at first, guess type of stream depending of extension
    # if there is no extension, try mpg_play and ogg_play both
    if url.endswith("ogg"):
        os.system("clear")
        cmd = "%s '%s'" % (ogg_play, url)
        print "Type of stream is probably ogg vorbis..."
        print "Trying '%s' " % (cmd)
        ret = os.system(cmd)
    elif url.endswith("mp3"):
        os.system("clear")
        cmd = "%s '%s'" % (mpg_play, url)
        print "Type of stream is probably ogg vorbis..."
        print "Trying '%s' " % (cmd)
        ret = os.system(cmd)
    else:
        for player in players:
            os.system("clear")
            cmd = "%s '%s'" % (player, url)
            print "Trying '%s' " % (cmd)
            ret = os.system(cmd)
            if ret == 0:
                break;

def listen(content):
#    print "listen(%s)" % (content)
    if type(content) == type(str()):
        play(content)
    elif type(content) == type(list()):
        for url in content:
            play(url)
    else:
        play(content)

def viewStations():
    stations = os.listdir(stationsdir)
    stat_menuitems = dict()

    for z in range(1, len(stations) + 1):
        station = getStationData(os.getcwd()+
                                 os.sep+
                                 stationsdir+
                                 os.sep+stations[z-1])
        for addrind in range(1, len(station["url"])+1):
            if len(station["name"]) == 0:
                stat_menuitems[str(z)] = [ station["url"][addrind-1], 
                                           listen, 
                                           station["url"] ]
            else:
                stat_menuitems[str(z)] = [ station["name"][addrind-1],
                                           listen,
                                           station["url"]]
                         
    menu(stat_menuitems, "Stations")

def addStation():
    print "add"

def editStation():
    print "edit"

def removeStation(): 
    print "remove"


def menu(items, name=""):
    print "-===========- %s -==============-" % (name)
    for key in items.keys():
        print "%s. %s" % (key, items[key][0])
    print "Your choice? "
    wahl = raw_input()
    try:
        if len(items[wahl]) == 2:
            items[wahl][1]()
        elif len(items[wahl]) == 3:
            items[wahl][1](items[wahl][2])
    except KeyError:
        return


def getStationData(infile):
    ret = dict()
    ret["file"] = infile
    ret["url"] = list()
    ret["name"] = list()
    streamfile = file(infile)
    content = streamfile.read()
    cont_lines = content.split("\n")
    for line in cont_lines:
        line = line.strip()
        if line.startswith("#EXTINF"):
            ret["name"].append(line.split(",")[1])
        elif line.startswith("http"):
            ret["url"].append(line)
    return ret

items = { '1' : [ "View stations", viewStations ],
          '2' : [ "Add station", addStation],
          '3' : [ "Edit station", editStation],
          '4' : [ "Remove station", removeStation ],
          '0' : [ "Exit", sys.exit, 0]}



menu(items, "Mainmenu")
