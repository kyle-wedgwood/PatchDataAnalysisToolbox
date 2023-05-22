function data = readDataFromEpochGroupGapFree( epochGroup)
  % Reads data from epochBlock object into array
  epochBlocks = epochGroup.getEpochBlocks;
  no_epoch_blocks = length( epochBlocks);
  
  data = [];
  for i = 1:no_epoch_blocks
    temp = epochBlocks{i}.getEpochs{1}.getResponses{1}.getData;
    data = [ data, temp];
  end
  
  plot(data);
  
end