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

def viewStations():
    print "view"

def addStation():
    print "add"

def editStation():
    print "edit"

def removeStation(): 
    print "remove"


def menu(items):
    for z in range(1, len(items)+1):
        print "%i. %s" % (z, items[str(z)][0])
    print "Your choice? "
    wahl = raw_input()
    items[wahl][1]()

items = { '1' : [ "View stations", viewStations ],
          '2' : [ "Add station", addStation],
          '3' : [ "Edit station", editStation],
          '4' : [ "Remove station", removeStation ] }

menu(items)
