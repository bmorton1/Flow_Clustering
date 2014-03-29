import lyrics
import sys

lines = open(sys.argv[1]).readlines()
for line in lines:
    line = line.replace('"', '').replace('/', '')
    url = 'http://rapgenius.com/' + line

    print url
    try:
        lyricData = lyrics.getLyrics(url)
        f = open(line.strip() + '.txt', 'w')
        print 'writing: ' + line
        print lyricData
        f.write(lyricData.encode('utf-8'))
        f.close()
    except:
        print 'error: ' + url
