% Vocal Extraction Script
clc
close all

audioLoc = '../../Audio/Original/';
saveLoc = '../../Audio/Vocals/';

segments = [24, 39; 29, 166; 6, 50; 21, 80; 46, 87; 26, 55; 30, 71; 11, 65]

% Grab file list
fileDir = audioLoc;
dirList = dir(fileDir);
while dirList(1).name(1) == '.'
    dirList(1) = '';
end

% Run vocal separation code
for j = 1:size(dirList, 1)
    fileName = [fileDir, dirList(j).name];
    saveFile = [saveLoc, 'Vocals_', dirList(j).name, ];
	VocalSep(fileName, saveFile);
end
