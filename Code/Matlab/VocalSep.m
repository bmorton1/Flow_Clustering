function [foreground] = VocalSep(audioFile, saveFile, segment)

% Read in audio
[y,sr] = mp3read(audioFile);

if nargin < 3
    audioClip = y;
else
    startIdx = segment(1) * sr;
    endIdx = segment(2) * sr;
    audioClip = y(startIdx:endIdx, :);
end

% Find background and foreground
background = repet_sim(audioClip,sr,[0,1,100]);
foreground = audioClip - background;

mp3write(foreground, sr, saveFile)

end