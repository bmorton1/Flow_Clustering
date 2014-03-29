import pdb
import numpy as np
from pyechonest import config, track
from MP3IO import MP3Handler

config.ECHO_NEST_API_KEY="YTHNUEZCTE3Q3HZLH"

def segmentFile(filename, clipNameBase, segLoc):

	# Run Echonest analyzer 
	t = track.track_from_filename(filename, 'mp3')
	t.get_analysis()

	# Song sections from echonest
	sectionDurations = [s['duration'] for s in t.sections]
	sections = np.cumsum(sectionDurations)

	# Read in audio
	audioInfo = MP3Handler().fileInfo(filename)
	audio, sr = MP3Handler().read(filename, 1)
	
	# Write each segment into its own file
	sectionSamples = np.round(np.multiply(sections,sr)).astype("int")

	for i in range(sectionSamples.shape[0]):

		if i == 0:
			audioClip = audio[:sectionSamples[i]]
		else:
			audioClip = audio[sectionSamples[i-1]:sectionSamples[i]]

		clipName = "{}{}_{}.mp3".format(segLoc, clipNameBase, i)

		MP3Handler().write(audioClip, clipName, sr*2)

def main():
	segmentFile("/Users/Brandon/Personal Projects/Flow_Clustering/Audio/Original/02 It\'s Tricky.mp3", 'Its Tricky', './')

if __name__ == '__main__':

	main()