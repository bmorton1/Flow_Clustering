import matplotlib.pyplot as plt
import pdb
import numpy as np
import librosa
import matplotlib.cm as cm

from cPickle import dump, load
from os.path import isdir, join, isfile
from MP3IO import MP3Handler
from scipy.io import loadmat
from sklearn import mixture, cluster


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

def plotScatter(xdata, ydata,  xlabel, ylabel, saveLoc, labels=None):
	"""
	plotScatter() - make a scatter plot

		Inputs: 
			data - data to be plotted
			xlabel - label for x
			ylabel - label for y

		Outputs: 
			Image

	"""
	
	fig1 = plt.figure()
	ax = fig1.add_subplot(111)
	ax.scatter(xdata, ydata, s = 25, c=labels, alpha=0.7,cmap=cm.Paired, vmin=0, vmax=3)
	ax.set_xlabel(xlabel)
	ax.set_ylabel(ylabel)

	title = "{} vs. {}".format(xlabel, ylabel)

	ax.set_title(title)
	plt.savefig(saveLoc)
	plt.close()

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

def main_playlist(type = 'gmm'):

	data = load(open('vocalFeatureData.p', 'r'))
	ids = data['artist']

	del(data['ID'])
	del(data['artist'])
	del(data['song'])

	data = np.vstack(data.viewvalues()).T

	if type == 'gmm':
		g = mixture.GMM(n_components=4)
		g.fit(data)
		labels = g.predict(data)
	elif type == 'kmeans':
		k = cluster.KMeans(4)
		k.fit(data)
		labels = k.predict(data)

	return labels

def main_plots():
	""" Make plots """
	data = load(open('vocalFeatureData.p', 'r'))

	del(data['ID'])
	del(data['artist'])
	del(data['song'])

	keys = data.keys()

	for i in range(len(keys)):
		for j in range(len(keys)):

			if j <= i:
				continue
			else:
				# Scale data to be from 0 to 1
				saveFile = "Clustered/{} - {}.pdf".format(keys[i], keys[j])
				xData = np.divide(data[keys[i]], np.max(data[keys[i]]))
				yData = np.divide(data[keys[j]], np.max(data[keys[j]]))
				subData = np.vstack((xData, yData)).T
				k = cluster.KMeans(4)
				k.fit(subData)
				labels = k.predict(subData)

				plotScatter(xData, yData, keys[i], keys[j], saveFile, labels)

def fixData():
	vocalData = loadmat('../../Data/firstVerseTimes.mat')
	oldData = load(open('vocalFeatureData.p', 'r'))
	syllableData = load(open('syllAnalysis.p', 'r'))
	newData = {'ID': np.array([vocalData['firstVerseTimes'][i][0][0][0] for i in range(len(vocalData['firstVerseTimes']))]), 
				'artist': [vocalData['firstVerseTimes'][i][1][0] for i in range(len(vocalData['firstVerseTimes']))],
				'song': np.array([vocalData['firstVerseTimes'][i][2][0] for i in range(len(vocalData['firstVerseTimes']))]),
				'syllableMean': np.array([syllableData[i+1][0] for i in range(41)]).astype(float),
				'syllableVar': np.array([syllableData[i+1][1] for i in range(41)]).astype(float)}

	newData['syllableMean'][22] = 0
	newData['syllableVar'][22] = 0

	oldData.update(newData)
	dump(oldData, open('vocalFeatureData.p', 'w'))

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
	dataDict = {'ID': np.array([vocalData['firstVerseTimes'][i][0][0][0] for i in range(len(vocalData['firstVerseTimes']))]), 
				'onsetMean': vocalFeatures[:,0],
				'onsetVar': vocalFeatures[:,1],
				'tempo': vocalFeatures[:,2],
				'centroidMean': vocalFeatures[:,3],
				'centroidVar': vocalFeatures[:,4],
				'contrastMean': vocalFeatures[:,5],
				'contrastVar': vocalFeatures[:,6],
				'onsetDensity': vocalFeatures[:,7],
				'artist': [vocalData['firstVerseTimes'][i][1][0] for i in range(len(vocalData['firstVerseTimes']))],
				'song': np.array([vocalData['firstVerseTimes'][i][2][0] for i in range(len(vocalData['firstVerseTimes']))])}

	dump(dataDict, open('vocalFeatureData.p', 'w'))

	print ('Done')

if __name__ == '__main__':

	# main()

	# fixData()
	main_plots()
	# out_kmeans = main_playlist('kmeans')

