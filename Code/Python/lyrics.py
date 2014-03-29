from bs4 import BeautifulSoup
import urllib2
import urllib
import re
import sys

# Quick and Dirty script to take an artist and song name, search for lyrics on rapgenius.com
# contains code from https://github.com/pconner03/rapgenius.py/blob/master/rapgenius.py

RAPGENIUS_URL = 'http://rapgenius.com'
RAPGENIUS_SEARCH_URL = 'http://rapgenius.com/search'

# given a rapgenius formatted lyrics url, parse out the raw lyrics text
def getLyrics(url):
    print 'Retrieving Lyrics for %s\n' % (url)
    soup = BeautifulSoup(urllib2.urlopen(url).read())
    ret = ""
    for row in soup('div', {'class':'lyrics'}):
        text = ''.join(row.findAll(text=True))
        data = text.strip() +'\n'
        ret += data
    return data

# create a search url for the given, artist, song
def formSearchUrl(artist, song):
    #form search url, take first result.
    raw_query = '%s %s' % (artist.strip(), str(song).strip())
    re.sub(r'\W+', '', raw_query)
    searchUrl = RAPGENIUS_SEARCH_URL + '?' + urllib.urlencode({'q': raw_query})
    print searchUrl + "\n" 
    return searchUrl

# execute the search and return the first result
def executeSearch(searchUrl):
    soup = BeautifulSoup(urllib2.urlopen(searchUrl).read())
    # take the first search result and grab its url:
    results = soup.find('li', {'class':'search_result'})
    if results:
        links = results.findChildren('a')
        if links:
            return links[0]['href']

def searchAndWriteFile(artist, song):

    url = formSearchUrl(artist, song)
    lyricsUrl = executeSearch(url)
    if lyricsUrl:
        lyrics = getLyrics(lyricsUrl)

        if not lyrics:
            print 'No lyrics found.'
        else:
            #print lyrics
            #print song
            song = re.sub('[^a-zA-Z0-9 ]+', '', str(song))
            artist = re.sub('[^a-zA-Z0-9 ]+', '', artist)
            f = open('%s-%s-lyrics.txt' % (artist.strip(), str(song)), 'w')
            f.write(artist + "\n")
            f.write(str(song) + "\n")
            f.write(lyrics.encode('utf-8'))
            f.close()
