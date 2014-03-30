import matplotlib.pyplot as plt
import pdb
import numpy as np
import librosa

from cPickle import dump
from os.path import isdir, join, isfile
from MP3IO import MP3Handler
from scipy.io import loadmat

def plotArray(data):
	"""
	plotArray() - Helper function for plotting arrays

		Inputs:
			data - data to be plotted

		Outputs:
			None 
	"""

	fig1 = plt.figure()
	ax = fig1.add_subplot(111)
	ax.plot(data)
	plt.show()

def contrast(spec, sr, a):
	""" 
	contrast() - Compute spectral contrast

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

		valley = np.log(np.sum(sortedFreqs[:nbinsToLook]) + np.spacing(1)) / nbinsToLook
		peak = np.log(np.sum(sortedFreqs[nbins-nbinsToLook:nbins]) + np.spacing(1)) / nbinsToLook

		contrasts[i] = peak - valley

	return contrasts

def centroid(spec, sr):
	""" 
	centroid() - Compute spectral centroid

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
		centroids[i] = np.sum(np.multiply(spec[:,i],centerFreqs)) / (np.sum(spec[:,i]) + np.spacing(1))

	return centroids

def clustering(pickleFile, ):

def main():
	""" 
	main() - Main function for feature extraction

		Inputs: 
			None

		Outputs:
			Pickle file with feature data
	"""

	vocalData = loadmat('../../Data/firstVerseTimes.mat')
	audioPath = '../../Audio/Vocals/'
	assert isdir(audioPath), "Audio path does not exist"		# Make sure directory of audio exists

	fileList = [ join(audioPath, 'Vocals_' + str(vocalData['firstVerseTimes'][i][3][0])) for i in range(len(vocalData['firstVerseTimes'])) ]
	numFiles = len(fileList)
	vocalFeatures = np.zeros((numFiles, 8))

	for i in range(numFiles):

		print 'Working on file {} of {}'.format(i, numFiles)
		# Read in audio 
		audio, sr = librosa.load(fileList[i], sr=44100)
		S = librosa.stft(audio, n_fft = 1024, hop_length = 512)
		spec = np.abs(S)

		# Extract features
		centroids = centroid(spec, sr)														# Spectral centroid
		contrasts = contrast(spec, sr, 0.05)												# Spectral contrast
		onset_frames    = librosa.onset.onset_detect(y=audio, sr=sr, hop_length=64)			# Calculate frames of onsets
		onset_times     = librosa.frames_to_time(onset_frames, sr, hop_length=64)			# Calculate times of onsets

		# Extract feature statistics
		vocalFeatures[i,0] =  np.mean(np.diff(onset_times))						# Mean of onset durations
		vocalFeatures[i,1] = np.var(np.diff(onset_times))						# Variance of onset durations
		vocalFeatures[i,2], beats = librosa.beat.beat_track(audio, sr )			# Get beats and tempo
		vocalFeatures[i,3] = np.mean(centroids)									# Mean of centroids
		vocalFeatures[i,4] = np.var(centroids)									# Variance of centroids
		vocalFeatures[i,5] = np.mean(contrasts)									# Mean of spectral contrast
		vocalFeatures[i,6] = np.var(contrasts)									# Mean of spectral contrast
		vocalFeatures[i,7] = onset_times.shape[0] / (audio.shape[0] / float(sr))# Onset density

	# Create dictionary for features
	dataDict = {'ID': vocalData['firstVerseTimes'][:][0][0][0], 
				'onsetMean': vocalFeatures[:,0],
				'onsetVar': vocalFeatures[:,1],
				'tempo': vocalFeatures[:,2],
				'centroidMean': vocalFeatures[:,3],
				'centroidVar': vocalFeatures[:,4],
				'contrastMean': vocalFeatures[:,5],
				'contrastVar': vocalFeatures[:,6],
				'onsetDensity': vocalFeatures[:,7]}

	dump(dataDict, open('vocalFeatureData.p', 'w'))

	print ('Done')
if __name__ == '__main__':
	main()