import exiftool
import glob
import lyrics
import sys

path = sys.argv[1]

for file in glob.glob(path + '*.mp3'):
    print file
    with exiftool.ExifTool() as et:
        info = et.get_tags(['Artist', 'Title'], file)
        print info
        artist = info['ID3:Artist']
        song = info['ID3:Title']
        lyrics.searchAndWriteFile(artist, song)

