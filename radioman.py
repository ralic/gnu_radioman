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
#  d viewing available stations
#  - deletion of stations
#  d selection of stations

import os
import sys

version = 0.01

logo = """radioman version %s
Copyright (C) 2009 Markus Zeindl <mrszndl@googlemail.com>
This program comes with ABSOLUTELY NO WARRANTY; for details see 
file "LICENSE", stored in the root directory of radioman.
This is free software, and you are welcome to redistribute it
under certain conditions; see file "LICENSE", stored in the root directory 
of radioman.
""" % (version)


# directory where playlist files of radio streams are stored
stationsdir = "stations"

# available players for different stream types
# first element of the list is a common extension,
# the second element is the name of the used codec
# the third element is the complete path to the player binary
# Note: radioman executes the binaries in following form:
# [binary] [stream]
# For instance: "/usr/bin/ogg123 'http://foo.bar.com/foo.ogg'"
ogg_play = [ "ogg", "OGG Vorbis", "/usr/bin/ogg123" ]
mpg_play = [ "mp3", "MPEG", "/usr/bin/mpg123" ]

players = [ ogg_play, mpg_play ]

def play(url):
    # at first, guess type of stream depending of extension
    for player in players:
        if url.endswith(player[0]):
            os.system("clear")
            cmd = "%s '%s'" % (player[2], url)
            print "Type of stream is probably %s..." % (player[1])
            print "Trying '%s' " % (cmd)
            ret = os.system(cmd)
            return
    # if type of stream cannot be guessed by extension,
    # try all above configured player binaries
    for player in players:
        os.system("clear")
        cmd = "%s '%s'" % (player[2], url)
        print "Trying '%s' " % (cmd)
        ret = os.system(cmd)
        if ret == 0:
            return

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
    stat_menuitems = list()

    for z in range(1, len(stations) + 1):
        stationdata = getStationData(os.getcwd()+
                                 os.sep+
                                 stationsdir+
                                 os.sep+stations[z-1])
        for streamdata in stationdata:
            stat_menuitems.append([ streamdata[0], 
                                    listen, 
                                    streamdata[1] ] )
    stat_menuitems.sort()
    stat_menuitems.append(["Back to Mainmenu", nulfunc ])
    menu(stat_menuitems, "Stations")

def addStation():
    print "add"

def editStation():
    print "edit"

def removeStation(): 
    print "remove"

def nulfunc():
    pass

def menu(items, name=""):
    print "-===========- %s -==============-" % (name)
    for itemind in range(0, len(items)):
        print "%i. %s" % (itemind+1, items[itemind][0])
    print "Your choice? "
    wahl = raw_input()
    wahl = int(wahl) - 1
    try:
        if len(items[wahl]) == 2:
            items[wahl][1]()
        elif len(items[wahl]) == 3:
            items[wahl][1](items[wahl][2])
    except KeyError:
        return


def getStationData(infile):
    ret = list()
    name = ""
    streamfile = file(infile)
    content = streamfile.read()
    cont_lines = content.split("\n")
    for line in cont_lines:
        line = line.strip()
        if line.startswith("#EXTINF"):
             name = line.split(",")[1].strip()
        elif line.startswith("http"):
            if len(name) == 0:
                name = line
            ret.append([name, line, infile])
            name = ""
    return ret



# ---------------------
#| Program entry point |
# ---------------------
if __name__ == "__main__":
    print logo
    while(True):
        items = [ [ "View stations", viewStations ],
                  [ "Add station", addStation],
                  [ "Edit station", editStation],
                  [ "Remove station", removeStation ],
                  [ "Exit", sys.exit, 0] ]
        menu(items, "Mainmenu")
