% Vocal Extraction Script
clc
close all

audioLoc = '../../Audio/Original/';
saveLoc = '../../Audio/Vocals/';
load('/Users/Brandon/Personal Projects/Flow_Clustering/Data/firstVerseTimes.mat')

segments = cell2mat(firstVerseTimes(:,4:5));

% Grab file list
fileDir = audioLoc;
numFiles = size(firstVerseTimes, 1);

% Run vocal separation code
for j = 1:numFiles
    fileName = [fileDir, firstVerseTimes{j,3}];
    saveFile = [saveLoc, 'Vocals_', firstVerseTimes{j,3}];    

    if ~exist(saveFile, 'file')
	    try
			VocalSep(fileName, saveFile, segments(j,:));
		catch
			disp(['\tNeed to convert ', saveFile])
			continue
		end
	end

	disp(['Done with ', saveFile, ' ', num2str(j), ' of ', num2str(numFiles)])
end
