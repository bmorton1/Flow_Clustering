import matplotlib.pyplot as plt
import pdb
from os.path import isdir, join, isfile
import numpy as np
import librosa
from MP3IO import MP3Handler
from scipy.io import loadmat

def plotArray(data):
	fig1 = plt.figure()
	ax = fig1.add_subplot(111)
	ax.plot(data)
	plt.show()

def contrast(spec, sr, a):
	""" 
	Compute spectral contrast

		Inputs: 
			spec - spectrogram
			sr - sample rate
			a - percentage of frequencies to consider for peak and valley

		Outputs:
			contrasts - array of centroids for each frame

	"""

	nbins, nframes = spec.shape

	fftSize = (nbins - 1) * 2
	freqRes = sr / 2.0 / fftSize

	contrasts = np.zeros(nframes)
	for i in range(nframes):
		sortedFreqs = np.sort(spec[:,i])
		nbinsToLook = np.round(nbins * a).astype("int")

		valley = np.log(np.sum(sortedFreqs[:nbinsToLook])) / nbinsToLook
		peak = np.log(np.sum(sortedFreqs[nbins-nbinsToLook:nbins])) / nbinsToLook

		contrasts[i] = peak - valley

	return contrasts

def centroid(spec, sr):
	""" 
	Compute spectral centroid

		Inputs: 
			spec - spectrogram
			sr - sample rate

		Outputs:
			centroids - array of centroids for each frame

	"""

	nbins, nframes = spec.shape

	fftSize = (nbins - 1) * 2
	freqRes = sr / 2.0 / fftSize

	centroids = np.zeros(nframes)
	for i in range(nframes):
		centerFreqs = np.multiply(freqRes, range(nbins))
		centroids[i] = np.sum(np.multiply(spec[:,i],centerFreqs)) / np.sum(spec[:,i])

	return centroids

def main():

	vocalData = loadmat('../../Data/firstVerseTimes.mat')
	audioPath = '../../Audio/Vocals/'

	# Make sure directory of audio exists
	assert isdir(audioPath), "Audio path does not exist"
	fileList = librosa.util.find_files(audioPath, ext='mp3')
	numFiles = len(fileList)
	vocalFeatures = np.zeros((numFiles, 3))

	for i in range(numFiles):

		# Read in audio 
		audio, sr = librosa.load(fileList[i], sr=44100)
		S = librosa.stft(audio, n_fft = 1024, hop_length = 512)
		spec = np.abs(S)

		centroids = centroid(spec, sr)
		contrasts = contrast(spec, sr, 0.05)
		pdb.set_trace()

		# Calculate locations of onsets
		onset_frames    = librosa.onset.onset_detect(y=audio, sr=sr, hop_length=64)
		onset_times     = librosa.frames_to_time(onset_frames, sr, hop_length=64)

		#Find average IOI and variance
		vocalFeatures[i,1] =  np.mean(np.diff(onset_times))						# Mean of onset durations
		vocalFeatures[i,2] = np.var(np.diff(onset_times))						# Variance of onset durations
		vocalFeatures[i,3], beats = librosa.beat.beat_track(audio, sr )			# Get beats and tempo
		vocalFeatures[i,4] = np.mean(centroids)									# Mean of centroids
		vocalFeatures[i,5] = np.var(centroids)									# Variance of centroids
		vocalFeatures[i,6] = np.mean(contrasts)									# Mean of spectral contrast
		vocalFeatures[i,7] = np.var(contrasts)									# Mean of spectral contrast

if __name__ == '__main__':
	main()