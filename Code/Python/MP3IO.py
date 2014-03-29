# MP3 reader and writer

import pdb 
import subprocess as sp
import numpy as np
import re

FFMPEG_BIN = '/opt/local/bin/ffmpeg'	 # Location of ffmpeg
INT16_MAX = 32768.0		# Highest possible value for int16

class MP3Handler:
	''' Basic class to read and write mp3s in python. Makes use of FFMPEG calls'''

	def fileInfo(self, fileName):
		'''
		fileInfo() - get basic info about mp3 file

		INPUTS
			fileName - the name fo the file you want to examine

		OUTPUTS
			fileInfo - Dictionary containing the file info
				
				fileInfo['name'] - name of the file
				fileInfo['type'] - type of file
				fileInfo['SR'] - sample rate of file
				fileInfo['bitrate'] - bitrate of file
		'''

		ffmpeg_cmd = [ FFMPEG_BIN,
			'-i', fileName,
			'-']

		pipe = sp.Popen(ffmpeg_cmd, stdin=sp.PIPE, stdout=sp.PIPE, stderr=sp.PIPE)
		raw_output = pipe.stderr.read()


		fileData = raw_output[raw_output.rfind('Audio'):]
		fileData = fileData.split('\n')[0]
		splitData = fileData.split(',')

		fileInfo = {'name': fileName, 
					'type': splitData[0][7:],
					'SR': int(re.findall(r'\d+', splitData[1])[0]),
					'bitrate': int(re.findall(r'\d+', splitData[4])[0])}

		return fileInfo


	def read(self, fileName, channels=2):
		''' 
		read() - Read an mp3 file

		INPUTS
			fileName - the name of the file
			channels - number of channels of audio

		OUTPUTS
			audio - raw audio data
			fileInfo['SR'] - sample rate of file
		'''
		fileInfo = self.fileInfo(fileName)

		ffmpeg_cmd = [ FFMPEG_BIN,
			'-i', fileName,
			'-f', 's16le',
			'-acodec', 'pcm_s16le',
			'-']

		pipe = sp.Popen(ffmpeg_cmd, stdin=sp.PIPE, stdout=sp.PIPE, stderr=sp.PIPE)
		raw_audio = pipe.communicate()[0]

		# pipe.terminate()

		# Reorganize raw_audio as a Numpy array with two-columns (1 per channel)
		audio = np.fromstring(raw_audio, dtype='int16')
		audio = audio.reshape((len(audio)/channels,channels))

		# Scale data to be from -1 to 1
		audio = np.divide(audio, INT16_MAX) # Highest possible 16bit integer

		return audio, fileInfo['SR']


	def write(self, data, fileName, sr, channels=1, bitrate="128k"):
		'''
		write() - write raw audio data to mp3 file

		INPUTS
			data - raw audio 
			filename - output file name
			sr - sample rate
			channels - number of channels of audio
			bitrate - bitrate for file 

		OUTPUTS
			None
		'''

		ffmpeg_cmd = [ FFMPEG_BIN,
		'-y', # (optional) means overwrite the output file if it already exists.
		'-f', 's16le', # means 16bit input
		'-acodec', 'pcm_s16le', # means raw 16bit input
		'-ar', str(sr), # the input will have 44100 Hz
		'-ac',str(channels) , # the input will have 2 channels (stereo)
		'-i', '-', # means that the input will arrive from the pipe
		'-vn', # means "don't expect any video input"
		'-acodec', "libmp3lame",  # output audio codec
		'-b:a', str(bitrate), # output bitrate (=quality). Here, 3000kb/second 
		fileName]

		# scale data to be from -32768 to 32768 (mp3 expects data to be int16)

		f = INT16_MAX / np.max(data)
		scaled_data = np.multiply(data, f).astype("int16")
		
		# audio = scaled_data.reshape((scaled_data.shape[0]*channels,1))

		pipe = sp.Popen(ffmpeg_cmd, stdin=sp.PIPE, stdout=sp.PIPE, stderr=sp.PIPE)
		test = pipe.communicate(input=scaled_data.tostring())

		# data.astype("int16").tofile(pipe.stdin)

		return None
