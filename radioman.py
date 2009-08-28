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
#  d opportunity for adding web radio
#    FIXED: By asking for names of streams, a stream on the first file
#           of playlist file will be skipped
#  d editing stations, which are already added
#  d viewing available stations
#  d deletion of stations
#  d selection of stations

import os
import sys
import urllib2

version = 0.02

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
# argument content can be described as followed:
# Type: List
# Element 0: List of URLs
# Element 1: Name of stream / URL if none is determinable
# Element 2: Name of file from which these URLs are read

#    print "listen(%s)" % (content)
    if type(content[0]) == type(str()):
        play(content[0])
    elif type(content[0]) == type(list()):
        for url in content[0]:
            play(url)
    else:
        play(content[0])

def remove(content):
# argument content can be described as followed:
# Type: List
# Element 0: List of URLs
# Element 1: Name of stream / URL if none is determinable
# Element 2: Name of file from which these URLs are read
    infile = file(content[2])
    lines = infile.read()
    infile.close()
    print "Searching in file for '%s'" % (content[0])
    findidx = lines.find(content[0])
    findidx_after = lines.find("http", findidx)
    findidx_before = lines.find("http", 0, findidx-5)
    if findidx_after == -1 and findidx_before == -1:
        # since there are no other links to streams left, 
        # it is safe to delete the whole file
        try:
            os.remove(content[2])
        except os.OSError:
            print "An error occured during attempt to remove desired station."
    else:
        # delete only link to stream
        lines = lines.replace(content[0], "")

        
        # determine if a extinf tag has been parsed before
        # if yes, content[1] contains the name of the station
        # if no, content[1] contains the url like content[0]
        if content[0] != content[1]:
            # lets find and remove the corresponding extinf tag for this stream
            # Note: Changes will be written to the playlist file immidiately
            m3u_out_file = open(content[2], "w")
            slines = lines.split("\n")
            for idx in range(0, len(slines)-1):
                if slines[idx].startswith("#EXTINF") and slines[idx].find(content[1]) != -1:
                    slines[idx] = ""
                    return
                m3u_out_file.write(slines[idx]+"\n")
            m3u_out_file.close()
                
              

def viewStations(function):
    stations = os.listdir(stationsdir)
    stat_menuitems = list()

    for z in range(1, len(stations) + 1):
        stationdata = getStationData(os.getcwd()+
                                 os.sep+
                                 stationsdir+
                                 os.sep+stations[z-1])
    # stationdata is a list, which has these elements:
    # Element 0  = Name/URL
    # Element 1  = URL
    # Element 2  = Input-File (needed for removing and editing)
        for streamdata in stationdata:
            stat_menuitems.append([ streamdata[0], 
                                    function, 
                                    [streamdata[1], 
                                     streamdata[0], 
                                     streamdata[2] ] 
                                    ] )
    stat_menuitems.sort()
    stat_menuitems.append(["Return to mainmenu", nulfunc ])
    menu(stat_menuitems, "Stations")

def addStation():
    # ask the user for url of the desired playlist file
    print "Type URL of the playlist file, which you want to add:"
    url = raw_input()

    # get destination filename from url
    url_spl = url.split("/")
    dest_fn = url_spl[len(url_spl)-1]

    # things to be asked:
    # d destination filename (check if filename is unique)
    # d name of station (make a guess using the first usable pls/m3u attribute)
    # - give a short summary of data to be written
    while True:
        print "Which file name should the playlist file get(%s)?" % ( dest_fn )
        usr_inp = raw_input()
        if len(usr_inp) != 0:
            dest_fn = usr_inp
        try:
            # check if file already exists
            os.stat(stationsdir + os.sep + dest_fn)
            print "Sorry, a file with this name is already existent."
            print "Please choose another name."

            # make a suggestion of a new and unique file name
            # by incrementing the last digit, if there is one already
            # (behavior like wget). For instance:
            # test.file
            # test.file.0
            # test.file.1
            # test.file.2
            if dest_fn[len(dest_fn)-2] == "." and dest_fn[len(dest_fn)-1].isdigit():
                # get digit and increment it by one
                digit = int(dest_fn[len(dest_fn)-1]) + 1
                # build new suggestion
                dest_fn = dest_fn[:len(dest_fn)-1] + str(digit)
            else:
                dest_fn = dest_fn +".0"
            
        except OSError:
            # if this code is executed, the file doesn't exist yet, so
            # we can accept the users input
            break;
    # get playlist file using URL
    req = urllib2.Request(url)
    resp = urllib2.urlopen(req)

    # prepare output file
    outfile = open(stationsdir+os.sep+dest_fn, "w")
    
    pllstcontent_lines = resp.read().split("\n")
    if pllstcontent_lines[0] == "#EXTM3U":
        outfile.write("#EXTM3U\n")

    for line_idx in range(0, len(pllstcontent_lines)-1):
        if pllstcontent_lines[line_idx].startswith("http"):
            # following conditions are ORed:
            # line_idx == 0 -->> that means, first file of playlist file)
            # (line_idx > 0 and not pllstcontent_lines[line_idx-1].sta...
            # -->> at first, it is not the first line in a file
            #      at second, the line before doesn't start with "#EXTINF"
            try:
                has_name = False
                if pllstcontent_lines[line_idx-1].startswith("#EXTINF"):
                    has_name = True
                if not has_name:
                    # since the current stream has no name, ask for it 
                    print "Stream:'%s'" % ( pllstcontent_lines[line_idx] )
                    print "How should this stream be called?"
                    name = raw_input()
                    extinf = "#EXTINF:-1,%s" % ( name )
                    pllstcontent_lines[line_idx] = extinf + "\n" + pllstcontent_lines[line_idx]
            except:
                pass
        print pllstcontent_lines[line_idx]
        outfile.write(pllstcontent_lines[line_idx]+"\n")
    outfile.close()
    
def edit(content):
    # argument content can be described as followed:
    # Type: List
    # Element 0: List of URLs
    # Element 1: Name of stream / URL if none is determinable
    # Element 2: Name of file from which these URLs are read

    print "\n"
    print "Information about selected stream"
    print "---------------------------------"
    print "URLs: %s" % (content[0])
    if content[0] != content[1]:
        print "Name: %s" % (content[1])
    print "Playlist-file: %s" % (content[2])

    print "\n\n"
    options = [ 
        [ "Change URL of stream" ],
        [ "Change name of stream" ],
        [ "Return to mainmenu", nulfunc], 
        ]

    # since this return value of menu() is zero-based, use 0 for first option
    # and 1 for second and so on
    ch = menu(options, "Edit stream")
    if ch == 0:
        print "New URL or nothing to abort."
        n_url = raw_input()
        if len(n_url) == 0:
            return
        # open file for reading complete content
        strf = open(content[2])
        filecontent = strf.read()
        strf.close()

        # change content
        filecontent = filecontent.replace(content[0], n_url)

        # write content back to file
        strf = open(content[2], "w")
        strf.write(filecontent)
        strf.close()
    elif ch == 1:
        # user wants to edit name of stream
        print "New Name or nothing to abort."
        n_name = raw_input()
        if len(n_name) == 0:
            return
        # open file for reading complete content
        strf = open(content[2], "r")
        # read filecontent and split it into lines
        filecontent = strf.read().split("\n")
        strf.close()

        # search m3u-tag and add or replace name tag
        for z in range(0, len(filecontent)-1):
            if filecontent[z] == content[0]:
                # check if a name is existent
                if z > 0:
                    if filecontent[z-1].startswith("#EXTINF"):
                        # replace old name with new one
                        filecontent[z-1] = filecontent[z-1].replace(content[1], n_name)
                    else:
                        # construct m3u-tag line and add it to current line
                        m3uline = "#EXTINF:-1,%s\n" % (n_name)
                        filecontent[z] = m3uline + filecontent[z]
                else:
                    # construct m3u-tag line and add it to current line
                    m3uline = "#EXTINF:-1,%s\n" % (n_name)
                    filecontent[z] = m3uline + filecontent[z]        

        strf = open(content[2], "w")
        # write content back to file
        for fileline in filecontent:
            print fileline
            strf.write(fileline + "\n")
        strf.close()
                
        pass

    print "edit"

# This is a function which does nothing. Do not alter this, since it is
# intended to be void.
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
        if len(items[wahl]) == 1:
            # note: wahl is zero based
            return wahl
        elif len(items[wahl]) == 2:
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
        items = [ [ "Start listening", viewStations, listen ],
                  [ "Add station", addStation],
                  [ "Edit station", viewStations, edit ],
                  [ "Remove station", viewStations, remove ],
                  [ "Exit", sys.exit, 0] ]
        menu(items, "Mainmenu")
