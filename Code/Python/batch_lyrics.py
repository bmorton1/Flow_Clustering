import lyrics
import sys

# pass csv file path:
lines = open(sys.argv[1]).readlines()

for line in lines:
    parts = line.split(',')
    if len(parts) == 2:
        artist = parts[0]
        song = parts[1]
        print 'Searching for artist: %s; song: %s' % (artist, song)
        lyrics.searchAndWriteFile(artist, song)

