from bs4 import BeautifulSoup
import urllib2
import urllib
import re
import sys


# Quick and Dirty script to take an artist and song name, search for lyrics on rapgenius.com
# contains code from https://github.com/pconner03/rapgenius.py/blob/master/rapgenius.py
artist = sys.argv[1]
song = sys.argv[2]

RAPGENIUS_URL = 'http://rapgenius.com'
RAPGENIUS_SEARCH_URL = 'http://rapgenius.com/search'

# given a rapgenius formatted lyrics url, parse out the raw lyrics text
def getLyrics(url):
    print 'Retrieving Lyrics for %s' % (url)
    soup = BeautifulSoup(urllib2.urlopen(url).read())
    ret = ""
    for row in soup('div', {'class':'lyrics'}):
        text = ''.join(row.findAll(text=True))
        data = text.strip() +'\n'
        ret += data
    return data

# 
def formSearchUrl(artist, song):
    #form search url, take first result.
    raw_query = '%s %s' % (artist, song)
    searchUrl = RAPGENIUS_SEARCH_URL + '?' + urllib.urlencode({'q': raw_query})
    print searchUrl 
    return searchUrl

def executeSearch(searchUrl):
    soup = BeautifulSoup(urllib2.urlopen(searchUrl).read())
    # take the first search result and grab its url:
    return soup.find('li', {'class':'search_result'}).findChildren('a')[0]['href']

url = formSearchUrl(artist, song)
lyricsUrl = executeSearch(url)
lyrics = getLyrics(lyricsUrl)
if not lyrics:
    print 'No lyrics found.'
else:    
    print lyrics
    f = open('%s-%s-lyrics.txt' % (artist, song), 'w');
    f.write(artist + "\n")
    f.write(song + "\n")
    f.write(lyrics.encode('utf-8'))
    f.close()



