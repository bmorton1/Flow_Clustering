import exiftool
import glob
import lyrics
import sys

path = sys.argv[1]

for file in glob.glob(path + '*.*'):
    print file
    with exiftool.ExifTool() as et:
        info = et.get_tags(['Artist', 'Title'], file)
        print info
        if 'ID3:Artist' in info:
            artist = info['ID3:Artist']
        elif 'QuickTime:Artist' in info:
            artist = info['QuickTime:Artist']
        if 'ID3:Title' in info:
            song = info['ID3:Title']
        elif 'QuickTime:Title' in info:
            song = info['QuickTime:Title']
        
        lyrics.searchAndWriteFile(artist, song)

