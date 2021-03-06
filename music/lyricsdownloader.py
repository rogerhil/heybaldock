#!/usr/bin/env python
# -*- coding: utf-8 -*-
#       Lyricsdownloader for Conky
#         eightmillion@gmail.com

import urllib, os, sys, string, re, BeautifulSoup
import urllib2
from optparse import OptionParser, SUPPRESS_HELP

from django.conf import settings

usage = "usage: %prog [-f|-q|-h|-v|-o|-c|-t|-d|-a|--template|--version] FILENAME DIRECTORY LINE NUMBER"

version = "0.9.8-svn"
dbusErr = 10
infoErr = 15
mpcErr  = 20
noPlayerErr = 25
webErr = 30
missingErr = 35
validChars = "-_.() %s%s" % (string.ascii_letters, string.digits)
work_folder = os.path.expanduser ('~/.lyrics')
verbose, longstatus, quiet, outdir = 0,0,0,0
cutline, tailline, align = 0,0,""
wordDict = {
    '&quot;' : '"',
    '\r\n'   : '\n',
    '&gt;'   : '>',
    '&lt;'   : '<'
}

def remove_html_tags(data):
    p = re.compile(r'<[^<]*?/?>')
    data = p.sub('', data)
    p = re.compile(r'/<!--.*?-->/')
    return p.sub('',data)

class player():
    def __init__(self):
        self.players = [ 'amarokapp','amarok','rhythmbox','audacious','banshee-1',
                'exaile','gmusicbrowser','juk','quodlibet','listen','songbird',
                'muine','beep-media-play','mpd' ]
        self.progs = os.popen('ps -eo comm').read().split('\n')
        self.dbusPlayers = [ 'amarok', 'audacious', 'juk', 'gmusicbrowser', 'songbird',
                    'muine', 'beep-media-play', 'exaile','listen','quodlibet','banshee-1'
                    ,'rhythmbox' ]
        #if os.popen('pgrep quodli').read(): self.progs.append('quodlibet')
        #if os.popen('pgrep listen').read(): self.progs.append('listen')
        for x in self.players:
            if x in self.progs:
                self.app = x
                break
        else: self.app = False
        if not self.app:
            if verbose: print "Couldn't find a supported media application."
            sys.exit(noPlayerErr)
        else:
            if verbose: print "Found player: %s" % self.app
        if self.app in self.dbusPlayers:
            try:
                import dbus
                self.bus = dbus.SessionBus()
            except ImportError:
                print "Please install python-dbus"
                sys.exit(1)
        if self.app == 'rhythmbox':
            self.rhythmbox = self.bus.get_object('org.gnome.Rhythmbox', '/org/gnome/Rhythmbox/Player')
        if self.app == 'amarok':
            self.rok = self.bus.get_object('org.kde.amarok','/Player')
            self.rokdata = self.rok.GetMetadata()
        if self.app == 'exaile':
            self.exaile = self.bus.get_object('org.exaile.DBusInterface', '/DBusInterfaceObject')
        if self.app == 'muine':
            self.muine = self.bus.get_object('org.gnome.Muine', '/org/gnome/Muine/Player')
            self.muinecs = self.muine.GetCurrentSong().split('\n')
            self.muinedata = {}
            x = 0
            for i in self.muinecs:
                try:
                    self.muinedata[self.muinecs[x].split(':')[0]] = self.muinecs[x].split(':')[1][1:]
                    x +=1
                except: break
        if self.app == 'audacious':
            self.aud = self.bus.get_object('org.mpris.audacious','/Player')
            self.auddata = self.aud.GetMetadata()
        if self.app == 'gmusicbrowser':
            self.gmus = self.bus.get_object("org.gmusicbrowser","/GMBDBusObject")
            self.gmusdata = self.gmus.CurrentSong()
        if self.app == 'songbird':
            self.bird = self.bus.get_object("org.mozilla.songbird","/org/mozilla/songbird")
        if self.app == 'beep-media-play':
            self.beep = self.bus.get_object("org.mpris.bmp","/Player")
            self.beepdata = self.beep.GetMetadata()
        if self.app == 'listen':
            self.listenDbus = self.bus.get_object('org.gnome.Listen','/org/gnome/listen')
            self.listen = os.popen('listen -c 2>/dev/null').read().replace(')','').strip().split('-')
            try:
                for i in range(3):
                    self.listen[i] = self.listen[i].strip()
                self.listen[1] = self.listen[1].replace('(','')
            except: pass
        if self.app == 'quodlibet':
            self.quod = self.bus.get_object('net.sacredchao.QuodLibet', '/net/sacredchao/QuodLibet')
            self.quoddata = self.quod.CurrentSong()
        if self.app == 'banshee-1':
            self.banshee = self.bus.get_object('org.bansheeproject.Banshee', '/org/bansheeproject/Banshee/PlayerEngine')
            self.bansheedata = self.banshee.GetCurrentTrack()
        if self.app == 'amarokapp':
            try:
                import pydcop
                self.rokapp = pydcop.DCOPObject( "amarok", "player" )
                self.rokappdata = {}
                self.rokappdata['artist'] = rokapp.artist()
                self.rokappdata['title'] = rokapp.title()
                self.rokappdata['album'] = rokapp.album()
                self.rokappdata['length'] = rokapp.totalTime()
                self.rokappdata['tracknumber'] = rokapp.track()
                self.rokappdata['position'] = rokapp.currentTime()
                self.rodappdata['status'] = rokapp.status()
                self.rokappdata['CurrentTime'] = rokapp.CurrentTime()
                self.rokappdata['TotalTime'] = rokapp.TotalTime()
                self.rokappdata['volume'] = rokapp.getVolume()
            except:
                self.rokappdata = {}
                self.rokappdata['artist'] = os.popen('dcop amarok player artist 2>/dev/null').read().strip()
                self.rokappdata['title'] = os.popen('dcop amarok player title 2>/dev/null').read().strip()
                self.rokappdata['album'] = os.popen('dcop amarok player album 2>/dev/null').read().strip()
                self.rokappdata['length'] = os.popen('dcop amarok player totalTime 2>/dev/null').read().strip()
                self.rokappdata['tracknumber'] = os.popen('dcop amarok player track 2>/dev/null').read().strip()
                self.rokappdata['position'] = os.popen('dcop amarok player currentTime 2>/dev/null').read().strip()
                self.rokappdata['status'] =  os.popen('dcop amarok player status 2>/dev/null').read().strip()
                self.rokappdata['CurrentTime'] = os.popen('dcop amarok player CurrentTime 2>/dev/null').read().strip()
                self.rokappdata['TotalTime'] =  os.popen('dcop amarok player TotalTime 2>/dev/null').read().strip()
                self.rokappdata['volume'] =  os.popen('dcop amarok player getVolume 2>/dev/null').read().strip()
    def prntime(self,ms):
        s = ms / 1000
        m,s = divmod(s,60)
        h,m = divmod(m,60)
        time = [ h , str(m) , str(s) ]
        if len(time[1]) == 1:      time[1] = '0' + time[1]
        if len(time[2]) == 1:      time[2] = '0' + time[2]
        if time[0] == 0:           del time[0]
        else: time[0] = str(time[0])
        return ':'.join(time)
    def prntimesec(self,sec):
        t = divmod(sec,60)
        x = []
        for i in t:
            x.append(str(i))
        if len(x[1]) == 1:
            x[1] = '0' + x[1]
        return ':'.join(x)
    def birdlength(self,length):
        if length == [u'']: return ''
        length = length.split(':')
        for i in range(3):
            if len(length[i]) == 1:
                length[i] = '0'+length[i]
        if length[0] == '00': length.remove(length[0])
        return ':'.join(length)
    def zeroPad(self,x):
        if len(str(x)) == 1: return '0' + str(x)
        else: return str(x)
    def convSec(self,x):
        if len(x) == 3: return int(x[0])*3600 + int(x[1])*60 + int(x[2])
        else: return int(x[0])*60 + int(x[1])
    def getArtist(self):
        if self.app == 'amarok':
            try: return self.rokdata['artist']
            except KeyError: return ''
        elif self.app == 'rhythmbox':
            return str(os.popen('rhythmbox-client --no-start --print-playing-format %aa').read())
        elif self.app == 'muine':
            try: return self.muinedata['artist']
            except KeyError: return ''
        elif self.app == 'audacious':
            try: return self.auddata['artist']
            except: return ''
        elif self.app == 'gmusicbrowser':
            try: return self.gmusdata['artist']
            except: return ''
        elif self.app == 'songbird':
            try: return self.bird.getArtist()
            except: return ''
        elif self.app == 'beep-media-play':
            try: return self.beepdata['artist']
            except KeyError: return ''
        elif self.app == 'listen':
            try: return self.listenDbus.get_artist()
            except:
                try: return self.listen[2]
                except IndexError: return ''
        elif self.app == 'quodlibet':
            try: return self.quoddata['artist']
            except KeyError: return ''
        elif self.app == 'banshee-1':
            try: return self.bansheedata['artist']
            except: return ''
        elif self.app == 'exaile':
            try: return self.exaile.get_artist()
            except: return ''
        elif self.app == 'amarokapp':
            try: return self.rokappdata['artist']
            except KeyError: return ''
        elif self.app == 'mpd':
            self.mpd = os.popen('mpc --format %artist%').read().split('\n')[0]
            if self.mpd.startswith('volume'):
                return ''
            else: return self.mpd
    def getTitle(self):
        if self.app == 'amarok':
            try: return self.rokdata['title']
            except KeyError: return ''
        elif self.app == 'rhythmbox':
            return str(os.popen('rhythmbox-client --no-start --print-playing-format %tt').read())
        elif self.app == 'muine':
            try: return self.muinedata['title']
            except KeyError: return ''
        elif self.app == 'audacious':
            try: return self.auddata['title']
            except: return ''
        elif self.app == 'gmusicbrowser':
            try: return self.gmusdata['title']
            except: return ''
        elif self.app == 'songbird':
            try: return self.bird.getTitle()
            except: return ''
        elif self.app == 'beep-media-play':
            try: return self.beepdata['title']
            except KeyError: return ''
        elif self.app == 'listen':
            try:
                self.title = self.listenDbus.get_title()
                if not self.title: return ''
                else: return self.title
            except:
                try: return self.listen[0]
                except IndexError: return ''
        elif self.app == 'quodlibet':
            try: return self.quoddata['title']
            except KeyError: return ''
        elif self.app == 'banshee-1':
            try: return self.bansheedata['name']
            except: return ''
        elif self.app == 'exaile':
            try: return self.exaile.get_title()
            except: return ''
        if self.app == 'amarokapp':
            try: return self.rokappdata['title']
            except KeyError: return ''
        elif self.app == 'mpd':
            self.mpd = os.popen('mpc --format %title%').read().split('\n')[0]
            if self.mpd.startswith('volume'):
                return ''
            else: return self.mpd
    def getAlbum(self):
        if self.app == 'amarok':
            try: return self.rokdata['album']
            except KeyError: return ''
        elif self.app == 'rhythmbox':
            return str(os.popen('rhythmbox-client --no-start --print-playing-format %at').read())
        elif self.app == 'muine':
            try: return self.muinedata['album']
            except KeyError: return ''
        elif self.app == 'audacious':
            try: return self.auddata['album']
            except: return ''
        elif self.app == 'gmusicbrowser':
            try: return self.gmusdata['album']
            except: return ''
        elif self.app == 'songbird':
            try: return self.bird.getAlbum()
            except: return ''
        elif self.app == 'beep-media-play':
            try: return self.beepdata['album']
            except KeyError: return ''
        elif self.app == 'listen':
            try: return self.listenDbus.get_album()
            except:
                try: return self.listen[1]
                except IndexError: return ''
        elif self.app == 'quodlibet':
            try: return self.quoddata['album']
            except IndexError: return ''
        elif self.app == 'banshee-1':
            try: return self.bansheedata['album']
            except: return ''
        elif self.app == 'exaile':
            try: return self.exaile.get_album()
            except: return ''
        if self.app == 'amarokapp':
            try: return self.rokappdata['album']
            except KeyError: return ''
        elif self.app == 'mpd':
            self.mpd = os.popen('mpc --format %album%').read().split('\n')[0]
            if self.mpd.startswith('volume'):
                return ''
            else: return self.mpd
    def getTrackNum(self):
        if self.app == 'amarok':
            try: return self.zeroPad(str(self.rokdata['tracknumber']))
            except KeyError: return ''
        elif self.app == 'rhythmbox':
            return str(os.popen('rhythmbox-client --no-start --print-playing-format %tN').read())
        elif self.app == 'muine':
            try: return self.zeroPad(self.muinedata['track_number'])
            except KeyError: return ''
        elif self.app == 'audacious':  # This is a dirty hack because audacious doesn't return the
            try:                       # track number for some unknown reason.
                import ID3
                self.tag = ID3.ID3(self.auddata['URI'].replace('%20',' ')[7:])
                return self.zeroPad(self.tag['TRACKNUMBER'])
            except: return ''
        elif self.app == 'gmusicbrowser':
            try: return self.gmusdata['track']
            except: return ''
        elif self.app == 'songbird':
            try: return self.zeroPad(self.bird.getTrack())
            except: return ''
        elif self.app == 'quodlibet':
            try: return self.quoddata['tracknumber']
            except: return ''
        elif self.app == 'beep-media-play':
            try: return self.zeroPad(self.beepdata['tracknumber'])
            except KeyError: return ''
        elif self.app == 'quodlibet':
            try: return self.quoddata['album']
            except IndexError: return ''
        elif self.app == 'exaile':
            try: return self.zeroPad(self.exaile.get_track_attr('track'))
            except: return ''
        elif self.app == 'banshee-1':
            try: return self.zeroPad(self.bansheedata['track-number'])
            except: return ''
        elif self.app == 'amarokapp':
            try: return self.rokappdata['tracknumber']
            except KeyError: return ''
        elif self.app == 'mpd':
            self.mpd = os.popen('mpc --format %track%').read().split('\n')[0]
            if self.mpd.startswith('volume'):
                return ''
            else: return self.mpd
        else: return "Unsupported"
    def getLength(self):
        if self.app == 'amarok':
            try: return self.prntime(int(self.rokdata['mtime']))
            except: return ''
        elif self.app == 'rhythmbox':
            self.length = str(os.popen('rhythmbox-client --no-start --print-playing-format %td 2>/dev/null').read().strip())
            if self.length == "Not playing": return ''
            else: return self.length
        elif self.app == 'audacious':
            try: return self.prntime(int(self.auddata['length']))
            except: return ''
        elif self.app == 'muine':
            try: return self.prntimesec(int(self.muinedata['duration']))
            except: return ''
        elif self.app == 'gmusicbrowser':
            try: return self.prntimesec(int(self.gmusdata['length']))
            except: return ''
        elif self.app == 'listen':
            try: return self.prntimesec(self.listenDbus.current_song_length())
            except: return ''
        elif self.app == 'quodlibet':
            try: return self.prntimesec(int(self.quod.CurrentSong()['~#length']))
            except: return ''
        elif self.app == 'songbird':
            try: return self.birdlength(self.bird.getLength())
            except: return ''
        elif self.app == 'exaile':
            try: return self.exaile.get_length()
            except: return ''
        elif self.app == 'banshee-1':
            try: return self.prntime(self.banshee.GetLength())
            except: return ''
        if self.app == 'amarokapp':
            try: return self.rokappdata['length']
            except KeyError: return ''
        elif self.app == 'mpd':
            self.mpd = os.popen('mpc --format %time%').read().split('\n')[0]
            if self.mpd.startswith('volume'):
                return ''
            else: return self.mpd
        else: return "Unsupported"
    def getPosition(self):
        if self.app == 'amarok':
            try: return self.prntime(int(self.rok.PositionGet()))
            except: return ''
        elif self.app == 'rhythmbox':
            self.pos = str(os.popen('rhythmbox-client --no-start --print-playing-format %te 2>/dev/null').read().strip())
            if self.pos == 'Not playing': return ''
            else: return self.pos
        elif self.app == 'audacious':
            try: return self.prntime(int(self.aud.PositionGet()))
            except: return ''
        elif self.app == 'muine':
            try: return self.prntimesec(int(self.muine.GetPosition()))
            except: return ''
        elif self.app == 'gmusicbrowser':
            try: return self.prntimesec(int(self.gmus.GetPosition()))
            except: return ''
        elif self.app == 'quodlibet':
            try: return self.prntimesec(self.quod.GetPosition()/1000)
            except: return ''
        elif self.app == 'exaile':
            try: return self.prntimesec(self.convSec(self.getLength().split(':')) * self.exaile.current_position()/100)
            except: return ''
        if self.app == 'amarokapp':
            try: return self.rokappdata['position']
            except KeyError: return ''
        elif self.app == 'mpd':
            try: self.mpd = os.popen('mpc').read().split('\n')[1].split('/')[1].split()[1]
            except IndexError: return ''
            return self.mpd
        elif self.app == 'banshee-1':
            try: return self.prntime(self.banshee.GetPosition())
            except: return ''
        else:
            return 'Unsupported'
    def getStatus(self):
        if self.app == 'amarok':
            try:
                self.caps = self.rok.GetStatus()
                if self.caps[0] == 0: return 'Playing'
                elif self.caps[0] == 1: return 'Paused'
                elif self.caps[0] == 2: return 'Stopped'
                else: return ''
            except: return ''
        elif self.app == 'rhythmbox':
            import time
            self.time1 = os.popen('rhythmbox-client --no-start --print-playing-format %te 2>/dev/null').read().strip().split(':')
            time.sleep(2)
            self.time2 = os.popen('rhythmbox-client --no-start --print-playing-format %te 2>/dev/null').read().strip().split(':')
            if self.time1 == ['Not playing']: return "Stopped"
            elif self.convSec(self.time1) == self.convSec(self.time2): return "Paused"
            else: return "Playing"
        elif self.app == 'muine':
            import time
            self.time1 = int(self.muine.GetPosition())
            time.sleep(2)
            self.time2 = int(self.muine.GetPosition())
            if self.time1 == 0 and self.time2 == 0: return "Stopped"
            elif self.time1 == self.time2: return "Paused"
            else: return "Playing"
        elif self.app == 'quodlibet':
            try:
                self.caps = str(self.quod.IsPlaying())
                if self.caps == '0': return 'Paused'
                elif self.caps == '1': return 'Playing'
                else: return 'Stopped'
            except: return ''
        elif self.app == 'audacious':
            try: self.caps = self.aud.GetStatus()
            except: return ''
            if self.caps == 0: return 'Playing'
            elif self.caps == 1: return 'Paused'
            elif self.caps == 2: return 'Stopped'
            else: return ''
        elif self.app == 'amarokapp':
            self.caps = int(self.rokappdata['status'])
            if self.caps == 0: return 'Stopped'
            elif self.caps == 1: return 'Paused'
            elif self.caps == 2: return 'Playing'
            else: return ''
        elif self.app == 'gmusicbrowser':
            import time
            try:
                self.time1 = self.gmus.GetPosition()
                time.sleep(2)
                self.time2 = self.gmus.GetPosition()
            except: return ''
            if self.time1 == 0 and self.time2 == 0: return "Stopped"
            elif self.time1 == self.time2: return "Paused"
            else: return "Playing"
        elif self.app == 'songbird':
            try: self.status = self.bird.getStatus()
            except: return ''
            if self.status == "playing": return "Playing"
            elif self.status == "paused": return "Paused"
            else: return "Stopped"
        elif self.app == 'exaile':
            try: self.status = self.exaile.status()
            except: return ''
            if self.status == "playing": return "Playing"
            elif self.status == "paused": return "Paused"
            else: return "Stopped"
        elif self.app == 'quodlibet':
            try: self.status = os.popen('quodlibet --status').read().split(' ')[0]
            except: return ''
            if self.status == "playing": return "Playing"
            elif self.status == "paused": return "Paused"
            else: return "Stopped"
        elif self.app == 'banshee-1':
            try: self.status = self.banshee.GetCurrentState()
            except: return ''
            if self.status == "playing": return "Playing"
            elif self.status == "paused": return "Paused"
            else: return "Stopped"
        elif self.app == 'mpd':
            try: self.status = os.popen('mpc').read().split('[')[1].split(']')[0]
            except: return 'Stopped'
            if self.status == "playing": return "Playing"
            elif self.status == "paused": return "Paused"
            else: return ""
        else: return 'Unsupported'
    def getPercent(self):
        if self.app == 'amarok':
            try: return int(self.rok.PositionGet()/ float(self.rokdata['mtime'])*100)
            except: return ''
        elif self.app == 'exaile':
            try: return self.exaile.current_position()
            except: return ''
        elif self.app == 'rhythmbox':
            try:
                self.length = self.convSec(os.popen('rhythmbox-client --no-start --print-playing-format %td 2>/dev/null').read().strip().split(':'))
                self.pos = self.convSec(os.popen('rhythmbox-client --no-start --print-playing-format %te 2>/dev/null').read().strip().split(':'))
                return int(self.pos / float(self.length)*100)
            except: return ''
        elif self.app == 'audacious':
            try:
                self.length = self.auddata['length']
                self.pos = self.aud.PositionGet()
                return int(self.pos / self.length * 100)
            except: return ''
        elif self.app == 'quodlibet':
            try: return int(self.quod.GetPosition()/float(self.quod.CurrentSong()['~#length'])/10)
            except: return ''
        elif self.app == 'muine':
            try: return  int(self.muine.GetPosition()/float(self.muinedata['duration'])*100)
            except: return ''
        elif self.app == 'gmusicbrowser':
            try: return int(self.gmus.GetPosition()/ float(self.gmusdata['length'])*100)
            except: return ''
        elif self.app == 'amarokapp':
            try: return int(float(self.rokappdata['CurrentTime'])/ float(self.rokappdata['TotalTime'])*100)
            except: return ''
        elif self.app == 'banshee-1':
            try: return int(self.banshee.GetPosition()/float(self.banshee.GetLength())*100)
            except: return ''
        elif self.app == 'mpd':
            try: return int(self.convSec(self.getPosition().split(':'))/float(self.convSec(self.getLength().split(':')))*100)
            except: return ''
        else: return 'Unsupported'
    def getVolume(self):
        if self.app == 'amarok':
            try: return self.rok.VolumeGet()
            except: return ''
        elif self.app == 'exaile':
            try: return int(float(self.exaile.get_volume()))
            except: return ''
        elif self.app == 'rhythmbox':
            try: return int(float(self.rhythmbox.getVolume()*100))
            except: return ''
        elif self.app == 'audacious':
            try: return self.aud.VolumeGet()
            except: return ''
        elif self.app == 'beep-media-play':
            try: return self.beep.VolumeGet()
            except: return ''
        elif self.app == 'muine':
            try: return self.muine.GetVolume()
            except: return ''
        elif self.app == 'amarokapp':
            return self.rokdata['volume']
        elif self.app == 'banshee-1':
            try: return self.banshee.GetVolume()
            except: return ''
        elif self.app == 'mpd':
            for i in os.popen('mpc').read().split('\n'):
                if i.startswith('volume'):
                    return int(i[7:][:3])
            return ''
        else: return 'Unsupported'


# multi-word replace
def mReplace(text, wordDict):
    for key in wordDict:
        text = text.replace(key, str(wordDict[key]))
    return text

#checks if the last song in missingsongs.txt is the current song so we don't
#keep hitting lyricwiki over and over again
def checkmissing(artistname,songname):
    if os.path.isfile(work_folder + "/missingsongs.txt"):
        try:
            lastmissing = open(work_folder + "/missingsongs.txt","r").readlines()[-1]
        except IndexError:
            lastmissing = "foobar"
        if lastmissing == artistname + " : " + songname +"\n":
            if verbose: print "Failed to find lyrics for song: %s" % lastmissing
            return True

def lyricsmode(artist,title):
    artist = urllib.quote(artist.lower().replace(' ','_'))
    title = urllib.quote(title.lower().replace(' ','_'))
    if verbose: print "Trying to fetch lyrics from lyricsmode.com"
    try:
        lyrics = urllib.urlopen('http://www.lyricsmode.com/lyrics/%s/%s/%s.html' % (artist[0],artist, title))
    except:
        if verbose: print "Could not connect to lyricsmode.com. Exiting..."
        return
    text = lyrics.read().decode('latin-1').replace( u'\xb7','')
    soup = BeautifulSoup.BeautifulSoup(text)
    #lyricsmode places the lyrics in a span with an id of "lyrics"
    lyrics = soup.findAll(attrs= {"id" : "lyrics"})
    if not lyrics:
        if verbose: print "Lyrics not found at lyricsmode.com"
        return []
    else:
        #this function removes formatting and converts html entities into ascii since lyricsmode obfuscates the lyrics.
        return remove_html_tags(unicode(BeautifulSoup.BeautifulStoneSoup(
                                lyrics[0].renderContents(),
                                convertEntities=BeautifulSoup.BeautifulStoneSoup.HTML_ENTITIES
                                )).replace('<br />','\n').strip('\r\n\t\t'))

def metrolyrics(artist,title):
    artist = urllib.quote(artist.lower().replace(' ','-'))
    title = urllib.quote(title.lower().replace(' ','-'))
    if verbose: print "Trying to fetch lyrics from metrolyrics.com"
    try:
        lyrics = urllib.urlopen("http://www.metrolyrics.com/%s-lyrics-%s.html" % (title,artist))
    except:
        if verbose: print "Could not connect to metrolyrics.com. Exiting..."
        return
    text = lyrics.read()
    text = text.replace('</sc"+"ript>"','') #beautifulsoup chokes on this particular tag so we have to get rid of it.
    soup = BeautifulSoup.BeautifulSoup(text)
    lyrics = soup.findAll(attrs= {"id" : "lyrics"})
    if not lyrics:
        if verbose: print "Lyrics not found at metrolyrics.com"
        return
    else:
        #this removes formatting and converts from html entities
        return '\n'.join(map(lambda x: x.strip(),remove_html_tags(unicode(BeautifulSoup.BeautifulStoneSoup(
                lyrics[0].renderContents(),convertEntities=BeautifulSoup.BeautifulStoneSoup.HTML_ENTITIES)
                ))[2:].replace('\r','\n').split('\n'))[:-2])

def absolutelyrics(artist,title):
    artist = urllib.quote(artist.lower().replace(' ','_'))
    title = urllib.quote(title.lower().replace(' ','_'))
    if verbose: print "Trying to fetch lyrics from absolutelyrics.com"
    try:
        lyrics = urllib.urlopen("http://www.absolutelyrics.com/lyrics/view/%s/%s/" % (artist,title))
    except:
        if verbose: print "Could not connect to absolutelyrics.com. Exiting..."
        return
    text = lyrics.read()
    text = text.replace(u"</scr'+'ipt>",'') #beautifulsoup chokes on this particular tag so we have to get rid of it.
    soup = BeautifulSoup.BeautifulSoup(text)
    lyrics = soup.findAll(attrs= {"id" : "realText"})
    if not lyrics:
        if verbose: print "Lyrics not found at absolutelyrics.com"
        return
    else:
        #this removes formatting and converts from html entities
        return remove_html_tags(str(lyrics[0]).replace("<br />","\n"))

def songlyrics(artist,title):
    artist = urllib.quote(artist.lower().replace(' ','-'))
    title = urllib.quote(title.lower().replace(' ','-'))
    if verbose: print "Trying to fetch lyrics from songlyrics.com"
    try:
        lyrics = urllib.urlopen("http://www.songlyrics.com/%s/%s-lyrics/" % (artist,title))
    except:
        if verbose: print "Could not connect to songlyrics.com Exiting..."
        return
    text = lyrics.read()
    soup = BeautifulSoup.BeautifulSoup(text)
    lyrics = soup.findAll(attrs= {"id" : "songLyricsDiv"})
    if not lyrics:
        if verbose: print "Lyrics not found at songlyrics.com"
        return
    else:
        if str(lyrics[0]).startswith('<p id="songLyricsDiv" class="songLyricsV14" style="font-size: 14px">\n                                         \tSorry, we have no'):
            if verbose: print "Lyrics not found at songlyrics.com"
            return
        #this removes formatting and an advertisement.
        convert = lambda x: str(BeautifulSoup.BeautifulStoneSoup(x, convertEntities=BeautifulSoup.BeautifulStoneSoup.HTML_ENTITIES))
        ls = [convert(str(i)).replace('<br></br>', '').strip() for i in lyrics[0].contents if i]
        rlyrics = []
        s = False
        for l in ls:
            if not l and not s:
                s = True
                continue
            if not l and s:
                s = False
            rlyrics.append(l)
            s = False
        return '\n'.join(rlyrics)

def lyricstime(artist,title):
    artist = urllib.quote(artist.lower().replace(' ','-'))
    title = urllib.quote(title.lower().replace(' ','-'))
    if verbose: print "Trying to fetch lyrics from lyricstime.com"
    try:
        lyrics = urllib.urlopen("http://www.lyricstime.com/%s-%s-lyrics.html" % (artist,title))
    except:
        if verbose: print "Could not connect to lyricstime.com"
        return
    text = lyrics.read()
    text = text.replace('</SCR\'+\'IPT>','')
    soup = BeautifulSoup.BeautifulSoup(text)
    lyrics = soup.findAll(attrs= {"id" : "songlyrics"})
    if not lyrics:
        if verbose: print "Lyrics not found at lyricstime.com"
        return
    else:
        return remove_html_tags(str(lyrics[0]).replace('<br />','')).replace('\n\r\n','')

def leoslyrics(artist,title):
    '''leoslyrics provides a nice api that returns easy to handle xml'''
    artist = urllib.quote(artist.lower())
    title = urllib.quote(title.lower())
    if verbose: print "Trying to fetch lyrics from leoslyrics.com"
    try:
        lyrics = urllib.urlopen('http://api.leoslyrics.com/api_search.php?auth=duane&artist=%s&songtitle=%s' % (artist, title))
    except:
        if verbose: print "Could not connect to leoslyrics.com"
        return
    text = lyrics.read()
    soup = BeautifulSoup.BeautifulSoup(text)
    if soup.findAll("response") and soup.findAll("response")[0].renderContents() == 'SUCCESS' and soup.findAll("result")[0].attrs[2][1] == 'true':
        try:
            lyrics = urllib.urlopen('http://api.leoslyrics.com/api_lyrics.php?auth=duane&hid=%s' % soup.findAll("result")[0].attrs[1][1]).read()
        except:
            if verbose: print "Could not connect to leoslyrics.com"
            return
        soup = BeautifulSoup.BeautifulSoup(lyrics)
        lyrics = soup.findAll('text')[0]
        return '\n'.join(filter(lambda x: not x.startswith('From:'),map(lambda x: x.strip(),mReplace(lyrics.renderContents(),{'&#xD;':'','\r\n':'\n'}).split('\n'))))
    else:
        if verbose: print "Lyrics not found at leoslyrics.com"
        return


def lyricwiki(artist,title):
    artist = artist.replace(' ','_').title()
    title = title.replace(' ','_').title()
    artist = urllib.quote(artist).replace('%26','&')
    title = urllib.quote(title)
    if verbose: print "Trying to fetch lyrics from lyricwiki.org"
    try:
        lyrics = urllib2.urlopen('http://lyricwiki.org/%s:%s' % (artist, title), timeout=10)
    except:
        if verbose: print "Could not connect to lyricwiki.org. Exiting..."
        return
    text = lyrics.read()
    soup = BeautifulSoup.BeautifulSoup(text)
    lyrics = soup.findAll(attrs= {"class" : "lyricbox"})
    if lyrics:
        return re.sub(r' Send.*?Ringtone to your Cell ','','\n'.join(remove_html_tags(lyrics[0].renderContents().replace('<br />','\n')).replace('\n\n\n','').split('\n')[0:-7]))
    else:
        if verbose: print "Lyrics not found at lyricwiki.org"
        return

def test_valid_lyrics(lyrics):
    if lyrics:
        if lyrics.strip().startswith("Please check the spelling and try again to"):
            return False
        else:
            return True
    return False

def getlyrics(artistname,songname):
    #make names lowercase for folders and remove trailing newflines
    artistname = mReplace(artistname.strip(),{'\'':'','(Live)':''})
    songname = mReplace(songname.strip(),{'\'':'','(Live)':''})

    lyricssite='lyricwiki'
    #get lyrics from lyric wiki who nicely return just the lyrics in plain text. well, they used to anyway :(
    #check if beautifulsoup found any lyrics on the page. if not, we'll try some other sites

    lyrics = ''
    if not test_valid_lyrics(lyrics):
        print "songlyrics"
        lyrics = songlyrics(artistname,songname)
    if not test_valid_lyrics(lyrics):
        print "lyricsmode"
        lyrics = lyricsmode(artistname,songname)
    if not test_valid_lyrics(lyrics):
        print "metrolyrics"
        lyrics = metrolyrics(artistname,songname)
    if not test_valid_lyrics(lyrics):
        print "absolutelyrics"
        lyrics = absolutelyrics(artistname,songname)
    if not test_valid_lyrics(lyrics):
        print "lyricstime"
        lyrics = lyricstime(artistname,songname)
    if not test_valid_lyrics(lyrics):
        print "leoslyrics"
        lyrics = leoslyrics(artistname,songname)
    if not test_valid_lyrics(lyrics):
        lyrics = lyricwiki(artistname, songname)
        print 'lyricwiki'
    if test_valid_lyrics(lyrics):
        lyrics = str(BeautifulSoup.BeautifulStoneSoup(lyrics,convertEntities=BeautifulSoup.BeautifulStoneSoup.HTML_ENTITIES))
        lyrics = mReplace(lyrics, wordDict).split('\n')
        print 'OK!!!'
        print
        return lyrics
    print "NOT FOUND!!", songname
    print

def printlyrics(lyrics):
    if cutline:
        x = 0
        while x < cutline:
            try:
                if align: print align + lyrics[x]
                else: print lyrics[x]
                x += 1
            except IndexError: break
    elif tailline:
        x = 0
        for i in lyrics:
            if x < tailline:
                x +=1
            else:
                try:
                    if align: print align + lyrics[x]
                    else: print lyrics[x]
                    x += 1
                except IndexError:
                    break
    elif align: print '\n'.join(map(lambda x:align + x,lyrics))
    else: print '\n'.join(lyrics)


def getlyricsfile(filename):
    try: from ID3 import ID3
    except ImportError:
        print 'Failed to import module id3. Please install python-id3'
        sys.exit(1)
    filename = os.path.realpath(filename)
    if not os.path.isfile(filename):
        filename = os.path.join(os.getcwd, filename)
    tag = ID3(filename)
    try:
        artistname = tag['ARTIST']
        songname   = tag['TITLE']
        if verbose: print "Artist: %s        Songname: %s" % ( artistname, songname)
    except KeyError:
        if verbose: print "Couldn't find the artist name or song title for: %s.  Check the ID3 tags." % filename
        return False
    if getlyrics(artistname,songname): return True
    else: return False

def formatOutput(format):
    a = player()
    if '%aa' in format: format = format.replace('%aa', a.getArtist())
    if '%bb' in format: format = format.replace('%bb', a.getAlbum())
    if '%tt' in format: format = format.replace('%tt', a.getTitle())
    if '%nn' in format: format = format.replace('%nn', a.getTrackNum())
    if '%td' in format: format = format.replace('%td', a.getLength())
    if '%te' in format: format = format.replace('%te', a.getPosition())
    if '%ss' in format: format = format.replace('%ss', a.getStatus())
    if '%pp' in format: format = format.replace('%pp', str(a.getPercent()))
    if '%vv' in format: format = format.replace('%vv', str(a.getVolume()))
    return format

def tryFormatting(): print formatOutput('Artist: %aa \nAlbum: %bb \nTitle: %tt \nNumber: %nn \nDuration: %td \nElapsed: %te \nStatus: %ss \nPercent: %pp')  #this is for debugging

def formatOutputTemp(template):
    template = os.path.realpath(template)
    if not os.path.isfile(template):
        print "Template file not found."
        sys.exit(1)
    f = open(template).read().decode('utf-8','ignore')
    a = player()
    if 'ARTIST' in f: f = f.replace('ARTIST', a.getArtist())
    if 'ALBUM' in f: f = f.replace('ALBUM', a.getAlbum())
    if 'TITLE' in f: f = f.replace('TITLE', a.getTitle())
    if 'TRACKNUM' in f: f = f.replace('TRACKNUM', a.getTrackNum())
    if 'DURATION' in f: f = f.replace('DURATION', a.getLength())
    if 'ELAPSED' in f: f = f.replace('ELAPSED', a.getPosition())
    if 'STATUS' in f: f = f.replace('STATUS', a.getStatus())
    if 'PERCENT' in f: f = f.replace('PERCENT', str(a.getPercent()))
    return f

def main():
    a = player()
    artistname, songname = a.getArtist(), a.getTitle()
    if not songname or not artistname: sys.exit(infoErr)
    elif verbose: print "Artist: %s        Songname: %s" % ( artistname, songname)
    if checkmissing(artistname,songname):
        sys.exit(missingErr)
    print getlyrics(artistname,songname)

if __name__ == '__main__':
    parser = OptionParser(usage=usage, version="%prog 0.9.8-svn")
    parser.add_option("-v", "--verbose", dest="verbose", action="store_true", default=False, help="request verbose output.")
    parser.add_option("-q", "--quiet", action="store_true", dest="quiet", default=False, help="Download the lyrics only")
    parser.add_option("-f", "--file", dest="filename", help="Download lyrics for MP3 file")
    parser.add_option("-o", "--outputdir", dest="outputdirectory",metavar="DIRECTORY", help="Set the output directory for the download")
    parser.add_option("--test", dest="test", action="store_true", default=False, help=SUPPRESS_HELP )
    parser.add_option("-c", "--cut", dest="cutline", type="int", metavar="LINE NUMBER",  help="Print the ouptut from the beginning to the specified line.")
    parser.add_option("-t", "--tail", dest="tailline", type="int", metavar="LINE NUMBER", help="Print the ouptut from the specified line to the end.")
    parser.add_option("-d", "--dir", action="store_true", default=False, dest="directory", help="Download lyrics for all the songs in the current directory. This option also turns on the quiet option. To turn it off add -q.")
    parser.add_option("-l","--format",  dest="format", help="Format the output for the song that's currently playing. The metadata delimiters are: %aa  -  Artist | %bb  -  Album | %tt  -  Title | %nn  -  Track Number | %td  -  Track Duration | %te  -  Track Elapsed | %ss  -  Status")
    parser.add_option("--template", dest="template", help="Format the song metadata with a template file. The delimiters are ARTIST ALBUM TITLE TRACKNUM DURATION ELAPSED STATUS See the example template file :/usr/share/doc/lyricsdownloader/template")
    parser.add_option("-a", "--align", dest="align",metavar="VALUE" , help='''Add an alignment setting for conky (${alignr},${alignc},${goto}). Make sure to single quote the arguments so that bash doesn't interpret it as a variable. This option is still experimental.''')
    parser.add_option("--artist", dest="artistname", help="Find lyrics for specific song.")
    parser.add_option("--songname", dest="songname", help="Find lyrics for specific song.")
    (options, args) = parser.parse_args()
    if options.quiet: quiet = True
    else: quiet = False
    if options.verbose:
        verbose = True
        if options.quiet: quiet = False
        else: quiet = True
    else: verbose = False
    if options.test:
        tryFormatting()
        sys.exit()
    if options.template:
        if options.filename:
            print "Options --template and -f conflict."
            sys.exit(1)
        elif options.quiet: quiet = False
        else: quiet = True
        print formatOutputTemp(options.template)
    if options.artistname:
        if not options.songname:
            print 'When using "--artist" a songname must be supplied with the option: --songname'
            sys.exit(1)
        lyrics = getlyrics(options.artistname,options.songname)
        if not lyrics:
            print "Lyrics not found."
        print '\n'.join(lyrics)
        sys.exit(0)
    if options.songname:
        print 'When using "--songname" an artistname must be supplied with the option: --artist'
        sys.exit(1)
    if options.format:
        if options.filename:
            print "Options --format and -f conflict."
            sys.exit(1)
        elif options.quiet: quiet = False
        else: quiet = True
        print formatOutput(options.format)
    if options.cutline: cutline = options.cutline
    else: cutline = False
    if options.tailline: tailline = options.tailline
    else: tailline = False
    if options.align:
       align =  options.align
       print align
    else: align = ''
    if options.outputdirectory != None:
        if os.path.isdir(os.path.realpath(options.outputdirectory)):
            outdir = os.path.realpath(options.outputdirectory)
        else:
            print "%s is not a valid directory" % options.outputdirectory
            sys.exit(1)
    else: outdir = False
    if options.filename:
        result = getlyricsfile(options.filename)
        if result and quiet:
            print "Added lyrics for file: %s" % options.filename
        elif quiet or not result:
            print "Failed to find lyrics for file: %s" % options.filename
        sys.exit(0)
    if options.directory:
        if options.quiet: quiet = False
        else: quiet = True
        files = [ f for f in os.listdir('.') if os.path.splitext(f)[1].lower() == '.mp3' ]
        if len(files) == 0:
            print "No valid music files found."
            sys.exit(1)
        for f in files:
            if getlyricsfile(f):
                print "Added lyrics for file: %s" % f
            else: print "Failed to find lyrics for file: %s" % f
        sys.exit(0)
    main()
