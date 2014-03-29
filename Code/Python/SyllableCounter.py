import numpy as np
import sqlite3 as lite
import glob
import os

def analyzeVerse(fileName):
	f = open(fileName, 'r')
	
	#first two lines are artist and song title, respecively
	artistName = f.readline()
	songName = f.readline()
	
	#rest of file is lyrics to song's first verse
	syllPerLine = np.array([])
	for line in f:
		syllCount = sum(np.array([CountSyllables(word) for word in line.split()]))
		syllPerLine = np.append(syllPerLine, syllCount)
	return songName, artistName, syllPerLine.mean(), syllPerLine.std()

def CountSyllables(word, isName=True):
    vowels = "aeiouy"
    #single syllables in words like bread and lead, but split in names like Breanne and Adreann
    specials = ["ia","ea"] if isName else ["ia"]
    specials_except_end = ["ie","ya","es","ed"]  #seperate syllables unless ending the word
    currentWord = word.lower()
    numVowels = 0
    lastWasVowel = False
    last_letter = ""

    for letter in currentWord:
        if letter in vowels:
            #don't count diphthongs unless special cases
            combo = last_letter+letter
            if lastWasVowel and combo not in specials and combo not in specials_except_end:
                lastWasVowel = True
            else:
                numVowels += 1
                lastWasVowel = True
        else:
            lastWasVowel = False

        last_letter = letter

    #remove es & ed which are usually silent
    if len(currentWord) > 2 and currentWord[-2:] in specials_except_end:
        numVowels -= 1

    #remove silent single e, but not ee since it counted it before and we should be correct
    elif len(currentWord) > 2 and currentWord[-1:] == "e" and currentWord[-2:] != "ee":
        numVowels -= 1

    return numVowels

def main():

	con = lite.connect('test.db')
	with con:
		cur = con.cursor()
		cur.execute("DROP TABLE IF EXISTS Songs")
		cur.execute("CREATE TABLE Songs(	SongName VARCHAR(30), \
																			Artist VARCHAR(30), \
																			avgSyllPerLine REAL, \
																			stddev REAL, \
																			PRIMARY KEY (SongName, Artist))")

	#lyricDir = raw_input("Enter directory containing lyrics files:")
	lyricDir = "../../Data/Lyrics/"		
	for fileName in glob.glob(lyricDir + "*.txt"):
		print fileName
		results = analyzeVerse(fileName)
		cur.execute("INSERT INTO Songs(SongName, Artist, avgSyllPerLine, stddev) \
																VALUES(	'" + str(results[0]) + "', \
																				'" + str(results[1]) + "', \
																				'" + str(results[2]) + "', \
																				'" + str(results[3]) + "')")


		con.commit()

	cur.execute("SELECT * FROM Songs")
	rows = cur.fetchall()
	for row in rows:
		print row
	
	con.close()

main()
