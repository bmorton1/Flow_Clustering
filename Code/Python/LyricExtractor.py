# from musixmatch import track

# def searchForLyrics(artist, trackName):
# 	'''Given the track name and the artist, find the lyrics'''

# 	# Grab track id
# 	queryTrack = track.search(q_track=trackName, 
# 		q_artist=artist, 
# 		f_has_lyrics=True, 
# 		page = 1, 
# 		page_size = 1)

# 	queryTrackId = queryTrack[0].track_id

# 	# Grab lyrics
# 	currTrack = track.Track(queryTrackId)
# 	trackLyrics = currTrack.lyrics()

# 	return trackLyrics

import re
import pdb
from robobrowser import RoboBrowser

def GetLyrics(searchTerm):
	# Browse to Rap Genius
	browser = RoboBrowser(history=True)
	browser.open('http://rapgenius.com/')

	# Search for Queen
	form = browser.get_form(action='/search')
	form
	form['q'].value = searchTerm
	browser.submit_form(form)

	# Look up the first 10 songs and check to see if we can find matching lyrics
	songs = browser.select('.song_link')
	for s in range(5):
		browser.follow_link(songs[s])
		title = browser.select('.song_title')

		myTitle = "{} Lyrics".format(searchTerm).lower()
		myTitle = re.sub(r'\W+', '', myTitle)

		pageTitle = title[0].text.lower()
		pageTitle = str(re.sub(r'\W+', '', pageTitle))

		if myTitle == pageTitle:
			lyrics = browser.select('.lyrics')
			return lyrics[0].text

	return None

if __name__ == '__main__':

	artist = "Flo Rida"
	title = "Right Round"
	query = "{} {}".format(artist, title)

	lyrics = GetLyrics(query)
	print lyrics