import lyrics
import sys

# Simple wrapper around lyrics.py, call like so: python lyrics.py 'Artist' 'Song' to print lyrics for the song, and write a file to disk named '<artist>-<song>-lyrics.txt'

artist = sys.argv[1]
song = sys.argv[2]

lyrics.searchAndWriteFile(artist, song)
